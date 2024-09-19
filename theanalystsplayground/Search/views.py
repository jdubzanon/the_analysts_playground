import os

import pandas as pd
import yfinance as yf
from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from theanalystsplayground.dashboard.models import Watchlist
from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)
from theanalystsplayground.Search.models import StocksData
from theanalystsplayground.Search.models import StockSearch
from theanalystsplayground.Search.SearchScripts.financials_helpers import (
    balance_sheet_processor,
)
from theanalystsplayground.Search.SearchScripts.financials_helpers import (
    cashflow_statement_processor,
)
from theanalystsplayground.Search.SearchScripts.financials_helpers import (
    income_statement_processor,
)
from theanalystsplayground.users.models import User

from .SearchScripts.helper_functions import aggregate_data
from .SearchScripts.helper_functions import competitors_info
from .SearchScripts.helper_functions import get_chart
from .SearchScripts.helper_functions import return_reverse_helper
from .SearchScripts.helper_functions import send_to_search_error_page

# crypto
from .SearchScripts.search_page_info_crypto import api_call_crypto

# etf
from .SearchScripts.search_page_info_etf import api_call_etf
from .SearchScripts.search_page_info_etf import get_etf_search_page_info

# forex market
from .SearchScripts.search_page_info_forex import api_call_forex

# indices
from .SearchScripts.search_page_info_index import api_call_index
from .SearchScripts.search_page_info_stock import api_call_common_stock

# common stock
from .SearchScripts.search_page_info_stock import get_search_page_info


def htmx_get(request):
    context = {}
    search_query = request.GET.get("q", "")  # Get the search query from the request

    if request.GET.get("q"):
        model_query = StockSearch.objects.filter(public_ticker=search_query.upper())[
            0:6
        ]
        if not model_query.exists():
            model_query = StockSearch.objects.filter(
                public_ticker__icontains=search_query.upper(),
            )[0:6]
        if not model_query.exists():
            model_query = StockSearch.objects.filter(
                company_name__icontains=search_query,
            )[0:15]

        if model_query.exists():
            context["model_query"] = model_query
            html_content = render_to_string(
                "reusables/htmxSearchPlaceholder.html",
                context,
            )
    else:
        html_content = ""

    return HttpResponse(html_content)


def htmx_company_swap(request, ticker_id):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    na = "N/A"
    url = f"https://api.polygon.io/v3/reference/tickers/{ticker_id}?apiKey={polygon_api_key}"
    response = common_api_call(url)
    if "error" in response:
        error = True
        results = {}
    else:
        error = False
        results = response.get("results", {})
    context = {
        "address": results.get("address", na),
        "description": results.get("description", na),
        "phoneNumber": results.get("phone_number", na),
        "totalEmployees": results.get("total_employees", na),
        "company_name": results.get("name", na),
        "website": results.get("homepage_url", None),
        "error": error,
    }
    return HttpResponse(
        render_to_string(
            "reusables/companyInfoPlaceholder.html",
            context,
        ),
    )


def htmx_competitors(request, ticker_id=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    stock = StocksData.objects.filter(ticker=ticker_id.upper()).first()
    competitors = StocksData.objects.filter(industry=stock.industry).exclude(
        ticker=ticker_id.upper(),
    )
    minimum = 5
    if len(competitors) > minimum:
        see_more = True
        competitors = competitors[0:5]
        industry = stock.industry
    else:
        see_more = False
        industry = None
    list_of_tickers = [obj.ticker for obj in competitors]
    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={','.join(list_of_tickers)}&include_otc=true&apiKey={polygon_api_key}"
    response = common_api_call(url)
    if "error" in response:
        context = {}
        context["error"] = True
        return HttpResponse(
            render_to_string(
                "reusables/competitorsPlaceholder.html",
                context,
            ),
        )

    competitors_snapshot = competitors_info(
        competitor_query_obj=competitors,
        res_j=response,
    )
    context = {
        "competitors_snapshot": competitors_snapshot,
        "ticker": ticker_id,
        "see_more": see_more,
        "industry": industry,
    }
    return HttpResponse(
        render_to_string(
            "reusables/competitorsPlaceholder.html",
            context,
        ),
    )


def htmx_chart_switch(request, ticker=None, time_frame=None):
    context = {
        "chart": get_chart(time_frame=time_frame, ticker=ticker),
        "current_ticker": ticker,
    }
    return HttpResponse(
        render_to_string("reusables/chartPlaceholder.html", context),
    )


def add_remove_watchlist(request, ticker_id=None, mtype=None):
    if not request.user.is_authenticated:
        response = HttpResponse("Redirecting...")
        response["HX-Redirect"] = reverse("account_login")
        return response
    user = User.objects.get(username=request.user.username)

    user_watchlist = Watchlist.objects.filter(
        ticker=ticker_id.upper(),
        market_type=mtype,
        user=user,
    )
    if user_watchlist.exists():
        user_watchlist.delete()
        return HttpResponse("Add to watchlist")

    additonal_ticker_info = StockSearch.objects.filter(
        public_ticker=ticker_id,
        market_type=mtype,
    ).first()

    if mtype != "crypto":
        model_instance = StocksData.objects.filter(ticker=ticker_id)
        if model_instance.exists():
            company_name = model_instance.first().company_name
        else:
            company_name = additonal_ticker_info.company_name
    else:
        company_name = additonal_ticker_info.company_name

    api_call_symbol = additonal_ticker_info.api_call_symbol
    market_type = additonal_ticker_info.market_type
    Watchlist.objects.create(
        ticker=ticker_id,
        company_name=company_name,
        api_call_symbol=api_call_symbol,
        market_type=market_type,
        user=user,
    )

    return HttpResponse("Remove from watchlist")


def dispatcher(request, ticker_id=None, user_id=None, mtype=None):
    types = [
        "BOND",
        "ETF",
        "ETN",
        "ETV",
        "SP",
        "FUND",
        "BASKET",
        "AGEN",
        "EQLK",
        "ETS",
    ]

    # ONLY 2 SEARCHES SEARCH BAR OR LINK
    # LINKS COME WITH mtype AND SEARCH BAR IS WITHOUT mtype
    # LINK CLICKING SEARCH

    model_query = (
        StockSearch.objects.filter(
            public_ticker=ticker_id,
            market_type=mtype,
        )
        if mtype
        else StockSearch.objects.filter(public_ticker=request.GET.get("q", "").upper())
    )
    # crypto and stocks use same tickers
    # so if i have multiple results
    # i want to send to multi query result page
    if model_query.exists():
        if len(model_query) > 1:
            context = {
                "queryResults": model_query,
            }
            return render(request, "Search/multiResultQuery.html", context)

        # SEARCH BAR DISPATCHING/ TRIGGERS WHEN THERE IS ON MATCH
        return return_reverse_helper(
            request=request,
            ticker_types=types,
            query=model_query.first(),
        )

    if search_parameter := request.GET.get("q"):
        # SEARCH FOR TICKER BY COMPANY NAME (NON RIGID SEARCH)
        model_query = StockSearch.objects.filter(
            company_name__icontains=search_parameter,
        )
    else:
        # LINK DOESNT EXISTS
        return send_to_search_error_page(request)

    # SEND TO SEARCH PAGE WITH ERROR MESSAGE IF DOESNT EXISTS
    if not model_query.exists():
        return send_to_search_error_page(request)

        # IF MULTIPLE MATCHES ARE RETURNED MOST LIKELY
        # FROM A COMPNAY NAME SEARCH SET THESE VALUES
    if len(model_query) > 1:
        return render(
            request,
            "Search/multiResultQuery.html",
            {
                "queryResults": model_query,
            },
        )

    # RETURN IF ONLY ONE MATCHES
    return return_reverse_helper(
        request=request,
        ticker_types=types,
        query=model_query.first(),
    )


def search(request, user_id=None, status=None):
    if status == "error":
        context = {
            "error": True,
            "error_msg": "could not find that stock, would you like to try again?",
        }

    else:
        context = {}

    return render(request, "Search/search_home.html", context)


def get_financials(request, ticker_id=None):
    context = {}
    stock = yf.Ticker(ticker_id.upper())
    income_statement = stock.income_stmt
    balance_sheet = stock.balance_sheet
    cf_statement = stock.cashflow
    # BAD RETURN YF FAILED
    if all(
        [
            income_statement.empty,
            balance_sheet.empty,
            cf_statement.empty,
        ],
    ):
        context["Failed"] = True
        return HttpResponse("SORRY ISSUES RETRIEVING DATA")

    # GLOBAL TABLE COLUMN DATES IM GRABBING FROM BALANCE SHEET
    context["tableColumns"] = []
    for dates in balance_sheet.columns[0:4]:
        timestamp = pd.Timestamp(dates)
        context["tableColumns"].append(timestamp.strftime("%b, %d, %Y"))

    context["bsMap"] = balance_sheet_processor(balance_sheet=balance_sheet)
    context["incomeMap"] = income_statement_processor(income_statement=income_statement)
    context["cashflowMap"] = cashflow_statement_processor(cf_statement=cf_statement)
    return HttpResponse(
        render_to_string("reusables/financialsTablePlaceholder.html", context),
    )


# RETURNED WHOLE SEARCH PAGES BELOW


def common_search_result(
    request,
    ticker_id=None,
    user_id=None,
    mtype=None,
):  # handles search bar link clicks
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        precheck = Watchlist.objects.filter(
            ticker=ticker_id.upper(),
            market_type=mtype,
            user=user,
        )
        in_watchlist = precheck.exists()
    else:
        in_watchlist = False
    # get search result
    ticker = ticker_id
    db_check = StocksData.objects.filter(ticker=ticker)
    if db_check.exists():
        in_database = True
        competitors = StocksData.objects.filter(industry=db_check[0].industry).exclude(
            ticker=ticker,
        )[0:6]
        industry = db_check.first().industry
    else:
        competitors = None
        in_database = False
        industry = None

    data_map = api_call_common_stock(
        ticker=ticker.upper(),
        competitor_query_obj=competitors,
    )
    # getting competitors snapshot

    if competitors:
        competitors_snapshot = competitors_info(
            competitor_query_obj=competitors,
            res_j=data_map.get("competitorData"),
        )
    else:
        competitors_snapshot = None

    search_page_info = get_search_page_info(
        ticker=ticker.upper(),
        data=data_map.get("searchPageInfo"),
    )

    # 52wk high/low and 3yr chart data
    all_aggregate_data = aggregate_data(
        ticker=ticker.upper(),
        res_j=data_map.get("aggData"),
    )
    fifty_two_week_high = all_aggregate_data[0]
    fifty_two_week_low = all_aggregate_data[1]

    snapshot = search_page_info[0].get("ticker", {"error": "bad request"})
    eps = search_page_info[1]
    pe_ratio = search_page_info[2]
    dividend_freq = search_page_info[3]
    last_div_payment = search_page_info[4]
    last_div_payment_date = search_page_info[5]
    last_yr_total_div_payment = search_page_info[6]
    current_volume = search_page_info[7]

    company_name = search_page_info[8]
    if not industry:
        industry = search_page_info[9]
    shares_outstanding = search_page_info[10]
    market_cap = search_page_info[11]
    market_status = search_page_info[12]
    cik_string = search_page_info[13]
    sec_url = f"https://www.sec.gov/edgar/browse/?CIK={cik_string}&owner=exclude"

    context = {
        "in_watchlist": in_watchlist,
        "in_database": in_database,
        "ticker": ticker,
        "market_type": mtype,
        "snapshot": snapshot,
        "company_name": company_name,
        "market_status": market_status,
        "cik_string": bool(cik_string),
        "secURL": sec_url,
        "chart": get_chart(time_frame="oneYr", ticker=ticker),
        "competitors": competitors,
        "competitors_snapshot": competitors_snapshot,
        "52_wk_high": fifty_two_week_high,
        "52_wk_low": fifty_two_week_low,
        "current_volume": current_volume,
        "pe_ratio": pe_ratio,
        "dividend_freq": dividend_freq,
        "last_yr_total_dividend": last_yr_total_div_payment,
        "last_div_payment": last_div_payment,
        "last_div_payment_date": last_div_payment_date,
        "eps": eps,
        "industry": industry,
        "shares_outstanding": shares_outstanding,
        "market_cap": market_cap,
        "all_news": data_map.get("news"),
    }

    return render(request, "Search/search_result.html", context)


def etf_search_result(
    request,
    ticker_id=None,
    user_id=None,
    ticker_type=None,
    mtype=None,
):
    # Checking if user is trying to use random numbers in URL
    ticker = ticker_id.upper()
    data_map = api_call_etf(ticker=ticker)
    etf_info = get_etf_search_page_info(
        ticker=ticker,
        data=data_map.get("searchPageInfo"),
    )

    snapshot = etf_info[0].get("ticker", {"error": "bad request"})
    prev_close = etf_info[1]
    current_volume = etf_info[2]
    etf_name = etf_info[3]
    dividend_freq = etf_info[4]
    last_yr_div_total = etf_info[5]
    market_status = etf_info[6]
    shares_outstanding = etf_info[7]
    last_div_pay_date = etf_info[8]
    market_cap = etf_info[9]
    last_div_payment = etf_info[10]

    # getting three yrs of data and grabbing 52 week high and 52 week low
    price_aggregate_info = aggregate_data(ticker=ticker, res_j=data_map.get("aggData"))
    fifty_two_wk_high = price_aggregate_info[0]
    fifty_two_wk_low = price_aggregate_info[1]

    # GET NEWS RELATED ARTICLES
    all_news = data_map.get("news")

    context = {
        "ticker": ticker,
        "ticker_type": ticker_type,
        "market_type": mtype,
        "snapshot": snapshot,
        "prev_close": prev_close,
        "chart": get_chart(time_frame="oneYr", ticker=ticker),
        "current_volume": f"{current_volume:,}",
        "market_cap": market_cap,
        "etf_name": etf_name,
        "52_week_high": fifty_two_wk_high,
        "52_week_low": fifty_two_wk_low,
        "dividend_freq": dividend_freq,
        "last_yr_div_total": last_yr_div_total,
        "last_div_pay_date": last_div_pay_date,
        "last_div_payment": last_div_payment,
        "shares_outstanding": f"{shares_outstanding:,}",
        "market_status": market_status,
        "all_news": all_news,
    }

    return render(request, "Search/etf_search_result.html", context)


def crypto_search_result(request, ticker_id=None, mtype=None, user_id=None):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        model_instance = StockSearch.objects.get(api_call_symbol=ticker_id.upper())
        ticker = model_instance.public_ticker
        precheck = Watchlist.objects.filter(
            ticker=model_instance.public_ticker,
            market_type=mtype,
            user=user,
        )
        in_watchlist = precheck.exists()
    else:
        model_instance = StockSearch.objects.get(api_call_symbol=ticker_id.upper())
        ticker = model_instance.public_ticker
        in_watchlist = False

    data_map = api_call_crypto(query_obj=model_instance)
    all_aggregate_data = aggregate_data(
        ticker=ticker_id.upper(),
        res_j=data_map.get("aggData"),
    )
    fifty_two_week_high = all_aggregate_data[0]
    fifty_two_week_low = all_aggregate_data[1]

    context = {
        "in_watchlist": in_watchlist,
        "market_type": mtype,
        "chart": get_chart(time_frame="oneYr", ticker=model_instance.api_call_symbol),
        "snapshot": data_map.get("snapshot", {}).get(
            "ticker",
            {"error": "bad request"},
        ),
        "timestamp": data_map.get("snapshot", {})
        .get("ticker", {})
        .get("lastTrade", {})
        .get("t", None),
        "ticker": ticker,
        "news": data_map.get("news"),
        "name": model_instance.company_name,
        "fiftyTwoHigh": fifty_two_week_high,
        "fiftyTwoLow": fifty_two_week_low,
        "nonPublicTicker": model_instance.api_call_symbol,
    }
    return render(request, "Search/crypto_search_result.html", context)


def forex_search_result(request, ticker_id=None, mtype=None, user_id=None):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        model_instance = StockSearch.objects.get(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
        )
        precheck = Watchlist.objects.filter(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
            user=user,
        )
        in_watchlist = precheck.exists()
    else:
        model_instance = StockSearch.objects.get(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
        )
        in_watchlist = False

    data_map = api_call_forex(query_obj=model_instance)

    all_aggregate_data = aggregate_data(
        ticker=None,
        res_j=data_map.get("aggData"),
    )
    fifty_two_week_high = all_aggregate_data[0]
    fifty_two_week_low = all_aggregate_data[1]

    #  SETTING SNAPSHOT AND TIMESTAMP BASED ON WHICH API ENDPOINT IS CALLED
    # ENDPOINT IS BASED ON IF ITS THE WEEKEND OR A WEEKDAY
    try:
        session = "session" in data_map.get("snapshot", {}).get("results", [])[0]
        if session:
            snapshot = data_map.get("snapshot", {}).get("results", [])[0]
            timestamp = snapshot.get("last_quote", {}).get("last_updated")
        else:
            snapshot = data_map.get("snapshot", {}).get(
                "ticker",
                {"error": "bad request"},
            )
            timestamp = snapshot.get("lastQuote", {}).get("t", 0)
    except IndexError:
        snapshot = data_map.get("snapshot", {}).get(
            "ticker",
            {"error": "bad request"},
        )
        timestamp = snapshot.get("lastQuote", {}).get("t", 0)
        # ONLY SETTING SESSION HERE BECAUSE SESSION IS ALREADY SET IN TRY BLOCK
        session = False

    if timestamp == 0:
        timestamp = None

    context = {
        "in_watchlist": in_watchlist,
        "market_type": mtype,
        "market_status": data_map.get("marketStatus"),
        "ticker": model_instance.public_ticker,
        "name": model_instance.company_name,
        "snapshot": snapshot,
        "timestamp": timestamp,
        "chart": get_chart(time_frame="oneYr", ticker=model_instance.api_call_symbol),
        "fiftyTwoHigh": fifty_two_week_high,
        "fiftyTwoLow": fifty_two_week_low,
        "nonPublicTicker": model_instance.api_call_symbol,
        "convertedCurrency": data_map.get(
            "convertedCurrency",
            {"converted": "N/A", "from": "N/A", "to": "N/A"},
        ),
        "session": session,
    }

    return render(request, "Search/forexSearchResult.html", context)


def indices_search_result(request, ticker_id=None, mtype=None, user_id=None):
    if request.user.is_authenticated:
        user = User.objects.get(username=request.user.username)
        model_instance = StockSearch.objects.get(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
        )
        precheck = Watchlist.objects.filter(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
            user=user,
        )
        in_watchlist = precheck.exists()
    else:
        model_instance = StockSearch.objects.get(
            api_call_symbol=ticker_id.upper(),
            market_type=mtype,
        )
        in_watchlist = False
    data_map = api_call_index(query_obj=model_instance)
    all_aggregate_data = aggregate_data(
        ticker=None,
        res_j=data_map.get("aggData"),
    )
    fifty_two_week_high = all_aggregate_data[0]
    fifty_two_week_low = all_aggregate_data[1]

    context = {
        "ticker": model_instance.public_ticker,
        "fiftyTwoHigh": fifty_two_week_high,
        "fiftyTwoLow": fifty_two_week_low,
        "in_watchlist": in_watchlist,
        "chart": get_chart(time_frame="oneYr", ticker=model_instance.api_call_symbol),
        "nonPublicTicker": model_instance.api_call_symbol,
        "market_type": model_instance.market_type,
        "indexName": model_instance.company_name,
        "indexLow": 0,
        "indexHigh": 6,
    }
    for json_item in data_map.get("snapshot", {}).get("results", []):
        context["snapshot"] = json_item
    context["name"] = context.get("snapshot", {}).get("name")
    return render(request, "Search/index_search_results.html", context)
