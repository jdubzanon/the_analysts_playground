import os

from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    add_to_context_with_ticker,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    create_passing_string,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    fetch_info,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    get_pagination_endpoint,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    get_ticker_snapshot_urls,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    newscenter_api_call,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    process_query_parameters,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    querytracker_injection,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    set_final_endpoint_with_ticker,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    set_final_endpoint_without_ticker,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    set_initial_endpoint,
)
from theanalystsplayground.newsCenter.newscenter_helpers.newscenter_helpers import (
    set_string_query_tracker,
)


def htmx_swap(request, **pagination_args):
    index_low = pagination_args.get("index_low")
    index_high = pagination_args.get("index_high")
    receiving_string = pagination_args.get("receiving_string")
    page_request = pagination_args.get("page_request")
    mtype = pagination_args.get("mtype")
    if request.method == "GET":
        return redirect(reverse("newsCenter:newsCenter_view"))

    api_call_string = get_pagination_endpoint(
        mtype=mtype,
        receiving_string=receiving_string,
    )
    response = common_api_call(api_call_string)

    if "error" in response:
        context = {}
        context["error"] = True
        return HttpResponse(
            render_to_string(
                "reusables/newsPlaceholder.html",
                context,
            ),
        )
    response = response.get("data")
    # HANDLES THE DATA OF THE API CALL SLICING
    result_count = 12
    index_start = 0
    if page_request == "nextPage":
        index_low = int(index_low) + result_count
        index_high = int(index_high) + result_count

    elif page_request == "prevPage":
        index_low = int(index_low) - result_count
        index_high = int(index_high) - result_count

    # THIS IS FOR TOGGLING THE PREVIOUS PAGE LINK ON AND OFF
    previous_page = index_low > index_start
    # THIS SLICES THE NEWS STORIES FROM THE API RESPONSE
    sliced_json = response[index_low:index_high]

    # THIS IS FOR TOGGLING THE NEXT PAGE LINK ON AND OFF
    next_page = len(sliced_json) >= result_count

    context = {
        "receivedString": receiving_string,
        "newIndexLow": index_low,
        "newIndexHigh": index_high,
        "data": sliced_json,
        "requestCheck": True,
        "nextPage": next_page,
        "prevPage": previous_page,
        "market_type": mtype,
    }
    return HttpResponse(
        render_to_string(
            "reusables/newsPlaceholder.html",
            context,
        ),
    )


def newscenter_form_handler(request, user_id=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    minimum_response = 10
    passed_low = 0
    passed_high = 12
    market_type = request.GET.get("market_type", "stocks")

    processed_data = process_query_parameters(
        request=request,
        source_bucket=[],
        query_tracker=querytracker_injection(),
    )

    source_bucket = processed_data.get("source_bucket")
    query_tracker = processed_data.get("query_tracker")

    string_query_tracker = set_string_query_tracker(
        request=request,
        query_tracker=query_tracker,
        string_query_tracker=[],
    )

    base_url = set_initial_endpoint(
        market_type=market_type,
        query_tracker=query_tracker,
    ).get("base_url")
    url_ending = set_initial_endpoint(
        market_type=market_type,
        query_tracker=query_tracker,
    ).get("url_ending")

    if query_tracker["ticker"]:
        with_ticker_address = set_final_endpoint_with_ticker(
            ticker=query_tracker["ticker"],
            source_bucket=source_bucket,
            string_query_tracker=string_query_tracker,
            base_url=base_url,
            url_ending=url_ending,
        )

        # getting the ticker snapshot urls
        snapshot_urls = get_ticker_snapshot_urls(
            ticker=query_tracker["ticker"],
            market_type=market_type,
            polygon_api_key=polygon_api_key,
        )

        ticker_price_url = snapshot_urls.get("ticker_price_url")
        company_name_url = snapshot_urls.get("company_name_url")

        # GETTING PRICE DETAILS FROM POLYGON API
        snapshot_details_response = fetch_info(
            ticker_price_url,
            company_name_url,
        )
        snapshot_details = list(snapshot_details_response)
        price_details = snapshot_details[0]
        company_details = snapshot_details[1]

        # bad request
        snapshot_apicall_failed = list(
            filter(lambda each_dict: "timeout_error" in each_dict, snapshot_details),
        )
        # bad ticker
        ticker_found = price_details.get("status", None) == "OK"
        # GETTING THE NEWS STORIES FROM NEWS APIS
        news_response = newscenter_api_call(with_ticker_address)
        # TOTAL FAILURE
        news_response_failed = "timeout_error" in news_response
        # TICKER FAILURE
        news_response_ticker_failure = "error" in news_response

        context = {
            "passedHigh": passed_high,
            "passedLow": passed_low,
            "requestCheck": True,
            "market_type": market_type,
            "with_ticker": bool(query_tracker.get("ticker")),
            "snapshot_statuscheck_failed": bool(snapshot_apicall_failed),
            "ticker_found": ticker_found,
            "news_response_failed": news_response_failed,
            "news_response_ticker_failure": news_response_ticker_failure,
        }

        context = add_to_context_with_ticker(
            ticker=query_tracker.get("ticker"),
            ticker_found=ticker_found,
            snapshot_apicall_failed=snapshot_apicall_failed,
            price_details=price_details,
            company_details=company_details,
            market_type=market_type,
            context=context,
        )

    else:  # NO TICKER SPECIFIED
        without_ticker_url = set_final_endpoint_without_ticker(
            source_bucket=source_bucket,
            string_query_tracker=string_query_tracker,
            base_url=base_url,
            url_ending=url_ending,
        )

        news_response = newscenter_api_call(without_ticker_url)
        # TOTAL FAILURE
        news_response_failed = "timeout_error" in news_response

        context = {
            "passedHigh": passed_high,
            "passedLow": passed_low,
            "requestCheck": True,
            "market_type": market_type,
            "with_ticker": False,
            "news_response_failed": news_response_failed,
        }
    # CREATING AND ADDING PASSING STRING TO CONTEXT
    context["passing_string"] = create_passing_string(
        source_bucket=source_bucket,
        string_query_tracker=string_query_tracker,
        ticker=query_tracker.get("ticker"),
    )

    # SETTING VALUES FOR NEXT PAGE
    if not news_response_failed:
        context["newsData"] = news_response.get("data", [])[passed_low:passed_high]
        # HANDLES IF THE "load more news" LINK SHOWS UP ON THE PAGE
        context["nextPage"] = len(news_response["data"]) > minimum_response

    else:
        context["newsData"] = None
        context["nextPage"] = False

    return render(request, "newsCenter/newsCenterMain.html", context)


def newscenter_view(request, user_id=None):
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    api_call_string = (
        f"https://stocknewsapi.com/api/v1/category?section=general"
        f"&items=60&page=1&token={news_api_key}"
    )
    response = common_api_call(api_call_string)

    context = {
        "generalNews": response.get("data") if response else None,
        "defaultDisplay": True,
        "ticker_found_error": False,
        "snapshot_apicall_failedcheck_passed": True,
        "requestCheck": False,
    }
    return render(request, "newsCenter/newsCenterMain.html", context)
