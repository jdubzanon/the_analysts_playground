import os

from django.contrib.postgres.search import SearchRank
from django.contrib.postgres.search import SearchVector
from django.http import HttpResponse
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)
from theanalystsplayground.Search.models import StockSearch

from .helperFunctions.indices_helper_functions import build_data_map
from .helperFunctions.indices_helper_functions import build_search_query
from .helperFunctions.indices_helper_functions import get_index_high
from .helperFunctions.indices_helper_functions import get_index_low
from .helperFunctions.indices_helper_functions import process_etf_string
from .helperFunctions.indices_helper_functions import process_index_search_string


def index_search_view(request, user_id=None):
    context = {}
    index_start = 0
    max_page_result = 50
    if request.method == "POST":
        search_string = request.POST.get("indexSearch")
        # EMPTY SEARCH
        if not search_string:
            return HttpResponseBadRequest("Please Type Something!!!")
        # STRICT SEARCH
        polygon_api_key = os.getenv("POLYGON_API_KEY")
        query = StockSearch.objects.filter(
            public_ticker=search_string.upper(),
            market_type="indices",
        )
        # LOOSE SEARCH
        if not query.exists():
            query = StockSearch.objects.filter(
                company_name__icontains=search_string,
                market_type="indices",
            )
        # IF I CANT FIND IT AFTER LOOSE SEARCH
        if not query.exists():
            return HttpResponseBadRequest(f"Sorry No Matches for {search_string}")

        # SEARCH TERM RETURNS SOMETHING
        # CHECKING OF THERE IS A NEXT PAGE
        context["totalMatches"] = len(query)
        context["search_string"] = search_string
        context["index_low"] = index_start
        context["index_high"] = (
            max_page_result if len(query) > max_page_result else len(query)
        )

        if len(query) > max_page_result:
            context["nextPage"] = True
            context["firstFifty"] = True

        else:
            context["nextPage"] = False
        first_fifty = query[index_start:max_page_result]
        all_data = {
            q.api_call_symbol: {
                "ticker": q.public_ticker,
                "company_name": q.company_name,
                "data": None,
            }
            for q in first_fifty
        }

        tickers = ",".join([ticker.api_call_symbol for ticker in first_fifty])
        url = (
            "https://api.polygon.io/v3/snapshot/indices?"
            f"ticker.any_of={tickers}"
            f"&sort=ticker&apiKey={polygon_api_key}"
        )

        response = common_api_call(url)
        if "error" in response:
            context["error"] = True
            return HttpResponse(
                render_to_string(
                    "reusables/indexSearchPlaceholder.html",
                    context,
                ),
            )
        results = response.get("results", [])
        for result in results:
            all_data[result.get("ticker")]["data"] = result

        context["allData"] = all_data
        return HttpResponse(
            render_to_string(
                "reusables/indexSearchPlaceholder.html",
                context,
            ),
        )
    return render(request, "indexSearch/indexSearch.html", context)


def index_search(
    request,
    page_requested=None,
    search_string=None,
    index_high=None,
    index_low=None,
):
    max_page_result = 50
    index_start = 0
    if request.method == "GET":
        return redirect(reverse("indexSearch:indexSearch_view"))
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    context = {}
    context["search_string"] = search_string
    index_high = get_index_high(page_requested=page_requested, index_high=index_high)
    index_low = get_index_low(page_requested=page_requested, index_low=index_low)
    context["previousPage"] = index_low > index_start
    context["index_high"] = index_high
    context["index_low"] = index_low
    query = StockSearch.objects.filter(
        company_name__icontains=search_string,
        market_type="indices",
    )
    context["totalMatches"] = len(query)
    requested_fifty = query[index_low:index_high]
    context["nextPage"] = len(requested_fifty) >= max_page_result
    all_data = {
        q.api_call_symbol: {
            "ticker": q.public_ticker,
            "data": None,
            "company_name": q.company_name,
        }
        for q in requested_fifty
    }

    url = (
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of="
        f"{','.join([ticker.api_call_symbol for ticker in requested_fifty])}"
        f"&sort=ticker&apiKey={polygon_api_key}"
    )
    response = common_api_call(url)
    if "error" in response:
        context["error"] = True
        return HttpResponse(
            render_to_string(
                "reusables/indexSearchPlaceholder.html",
                context,
            ),
        )
    results = response.get("results", [])
    for result in results:
        all_data[result.get("ticker")]["data"] = result

    context["allData"] = all_data
    return HttpResponse(
        render_to_string(
            "reusables/indexSearchPlaceholder.html",
            context,
        ),
    )


# INDEX SEARCH RESULTS PAGE
def related_indices(
    request,
    company_name=None,
    page_requested=None,
    index_high=None,
    index_low=None,
):
    index_start = 0
    min_results = 5
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    context = {}
    if request.method == "GET":
        redirect_query = StockSearch.objects.filter(
            company_name=company_name,
            market_type="indices",
        ).first()
        return redirect(
            reverse(
                "search:indices_search_result",
                kwargs={"ticker_id": redirect_query.public_ticker, "mtype": "indices"},
            ),
        )

    search_strings = process_index_search_string(company_name=company_name)
    combined_queries = build_search_query(search_strings=search_strings)

    search_vector = SearchVector("company_name")
    related_index_search = (
        StockSearch.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, combined_queries),
        )
        .filter(search=combined_queries, market_type="indices")
        .order_by("-rank")
        .exclude(company_name=company_name)
    )

    if related_index_search.exists():
        context["MatchesFound"] = True
        # IMPLIMENT PAGINANTION
        index_high = get_index_high(
            page_requested=page_requested,
            index_high=index_high,
        )
        index_low = get_index_low(page_requested=page_requested, index_low=index_low)
        results = related_index_search[index_low:index_high]
        total_results = len(related_index_search)
        context["index_high"] = index_high
        context["index_low"] = index_low
        context["prevPage"] = index_low > index_start
        context["nextPage"] = all(
            [index_high < total_results, len(results) > min_results],
        )
        context["company_name"] = company_name
        data_map = build_data_map(results=results)
        url = (
            f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of="
            f"{','.join([ticker.api_call_symbol for ticker in  results])}"
            f"&apiKey={polygon_api_key}"
        )
        response = common_api_call(url)
        if "error" in response:
            context["error"] = True
            return HttpResponse(
                render_to_string(
                    "reusables/relatedIndexPlaceholder.html",
                    context,
                ),
            )

        for json_item in response.get("results", []):
            data_map[json_item.get("ticker", {"data": None})]["data"] = json_item
        context["dataMap"] = data_map
    else:
        context["MatchesFound"] = False

    return HttpResponse(
        render_to_string(
            "reusables/relatedIndexPlaceholder.html",
            context,
        ),
    )


def related_etf(request, **data):
    index_start = 0
    min_results = 5
    polygon_api_key = os.getenv("POLYGON_API_KEY")

    company_name = data.get("company_name")
    page_requested = data.get("page_requested")
    index_high = data.get("index_high")
    index_low = data.get("index_low")
    ticker_type = data.get("ticker_type")

    context = {}

    if request.method == "GET":
        redirect_query = StockSearch.objects.filter(
            company_name=company_name,
            market_type="stocks",
        ).first()
        return redirect(
            reverse(
                "search:indices_search_result",
                kwargs={
                    "ticker_id": redirect_query.public_ticker,
                    "mtype": "indices",
                    "ticker_type": ticker_type,
                },
            ),
        )

    search_strings = process_etf_string(company_name=company_name)
    combined_queries = build_search_query(search_strings=search_strings)

    search_vector = SearchVector("company_name")
    related_index_search = (
        StockSearch.objects.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, combined_queries),
        )
        .filter(
            search=combined_queries,
            market_type="stocks",
            security_type=ticker_type,
        )
        .order_by("-rank")
        .exclude(company_name=company_name)
    )

    if related_index_search.exists():
        context["MatchesFound"] = True
        # IMPLIMENT PAGINANTION
        index_high = get_index_high(
            page_requested=page_requested,
            index_high=index_high,
        )
        index_low = get_index_low(page_requested=page_requested, index_low=index_low)
        results = related_index_search[index_low:index_high]
        total_results = len(related_index_search)
        context["index_high"] = index_high
        context["index_low"] = index_low
        context["prevPage"] = index_low > index_start
        context["nextPage"] = all(
            [index_high < total_results, len(results) > min_results],
        )
        context["company_name"] = company_name
        context["tickerType"] = ticker_type

        data_map = build_data_map(results=results)

        url = (
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="
            f"{','.join([ticker.api_call_symbol for ticker in results])}"
            f"&apiKey={polygon_api_key}"
        )
        response = common_api_call(url)
        if "error" in response:
            context["error"] = True
            return HttpResponse(
                render_to_string(
                    "reusables/relatedEtfPlaceholder.html",
                    context,
                ),
            )
        for json_item in response.get("tickers", []):
            data_map[json_item.get("ticker")]["data"] = json_item
        context["dataMap"] = data_map
    else:
        context["MatchesFound"] = False
    return HttpResponse(
        render_to_string(
            "reusables/relatedEtfPlaceholder.html",
            context,
        ),
    )


# NEXT 3 FUNCTIONS HANDLE indexSearch/view-all-indices/
def view_all_indices(request, user_id=None):
    context = {}
    max_page_result = 50
    index_start = 0
    list_of_indices = [
        "OMX",
        "DOW JONES",
        "CBOE",
        "PROSHARES",
        "NASDAQ",
        "AMERIBOR",
        "ALLIANZIM",
        "TRUESHARES",
        "ALPHA VEE",
        "STANDARD & POOR",
        "CRSP",
        "FIRST NORTH",
        "DORSEY WRIGHT",
        "PHLX",
        "ISE",
        "MORGAN STANLEY",
        "MORNINGSTAR",
        "FACTSET",
        "GLOBAL",
        "IBOXX",
        "IDB",
        "KELLY",
        "HORIZON KINETICS",
        "IPOX",
        "LINDEN THOMAS",
        "ISHARES",
        "STRATEGIC",
        "KBW",
        "DWA",
    ]
    list_of_indices.sort()
    context["list_of_indices"] = list_of_indices
    front_page_query = StockSearch.objects.filter(
        company_name__istartswith="dow jones",
        market_type="indices",
    )
    context["allData"] = front_page_query[0:50]
    context["nextPage"] = True
    context["prevPage"] = False
    context["index_low"] = index_start
    context["index_high"] = max_page_result
    context["name"] = "dow jones"
    context["from"] = index_start
    context["to"] = max_page_result
    return render(request, "indexSearch/view_all_indices.html", context)


def htmx_index_category_link_click(
    request,
    name=None,
    index_high=None,
    index_low=None,
    page_requested=None,
):
    max_page_result = 50
    index_start = 0

    context = {}
    front_page_query = StockSearch.objects.filter(
        company_name__istartswith=name,
        market_type="indices",
    )
    context["data"] = front_page_query[0:max_page_result]
    context["name"] = name
    if len(front_page_query) > max_page_result:
        context["nextPage"] = True

    else:
        context["nextPage"] = False
    context["prevPage"] = False
    context["index_low"] = index_start
    context["index_high"] = max_page_result
    # for displaying results text
    context["from"] = index_start
    if len(front_page_query) >= max_page_result:
        context["to"] = max_page_result
    else:
        context["to"] = len(front_page_query)

    context["total_results"] = len(front_page_query)
    return HttpResponse(
        render_to_string(
            "reusables/indexResultsPlaceholder.html",
            context,
        ),
    )


def htmx_category_pagination(
    request,
    name=None,
    index_high=None,
    index_low=None,
    page_requested=None,
):
    max_page_result = 50
    index_start = 0
    if request.method == "GET":
        return redirect(reverse("indexSearch:viewAllIndices"))
    context = {}
    index_high = get_index_high(
        page_requested=page_requested,
        index_high=index_high,
        big_switch=True,
    )
    index_low = get_index_low(
        page_requested=page_requested,
        index_low=index_low,
        big_switch=True,
    )

    requested_results_query = StockSearch.objects.filter(
        company_name__istartswith=name,
        market_type="indices",
    )
    # ASSIGNMENTS FOR FUTURE USE
    all_results = requested_results_query[index_low:index_high]
    # TOGGLE NEXT AND PREVIOUS RESULTS LINKS
    context["nextPage"] = len(requested_results_query) > index_high
    context["prevPage"] = index_low > index_start
    context["data"] = all_results
    context["index_high"] = index_high
    context["index_low"] = index_low
    context["name"] = name
    context["total_results"] = len(requested_results_query)
    context["from"] = index_low
    context["to"] = (
        index_high
        if len(all_results) == max_page_result
        else len(requested_results_query)
    )

    return HttpResponse(
        render_to_string(
            "reusables/indexResultsPlaceholder.html",
            context,
        ),
    )
