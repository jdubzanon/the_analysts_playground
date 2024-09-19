import os
from concurrent.futures import ThreadPoolExecutor

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse

from theanalystsplayground.currencies.helperFunctions.currency_helpers import get_url
from theanalystsplayground.Search.models import StockSearch

from .HomeFunctions.helper_functions import assign_context
from .HomeFunctions.helper_functions import common_api_call
from .HomeFunctions.helper_functions import data_assignment
from .HomeFunctions.helper_functions import fetch_api_info
from .HomeFunctions.helper_functions import get_swap_base_url
from .HomeFunctions.helper_functions import get_swap_end_url
from .HomeFunctions.view_all_helper_functions import get_api_info
from .HomeFunctions.view_all_helper_functions import get_dow30
from .maps.maps import inject_crypto_map
from .maps.maps import inject_forex_map
from .maps.maps import inject_name_map

User = get_user_model()


def front_page(request):
    return render(request, "FrontPage/frontPage.html", {})


def about_me_view(request):
    return render(request, "aboutMe/aboutMe.html", {})


def dispatcher(request, user_id=None):
    if request.user.is_authenticated:
        return redirect(
            reverse(
                "HomePage:user-home-view",
                kwargs={"user_id": request.user.username},
            ),
        )

    return redirect(reverse("HomePage:home-view"))


def home_view(request, user_id=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    crypto_news_api_key = os.getenv("CRYPTO_NEWS")

    # ENDPOINTS
    polygon_snapshot_url = (
        "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="
    )
    polygon_end_url = f"&apiKey={polygon_api_key}"

    news_api_base_url = "https://stocknewsapi.com/api/v1?tickers="
    end_news_api_url = f"&token={news_api_key}"

    crypto_map = inject_crypto_map()
    forex_map = inject_forex_map()

    list_of_crypto_tickers = list(crypto_map)
    list_of_fx_tickers = list(forex_map)

    forex_base_url = get_url()
    any_of = "any_of" in forex_base_url
    all_data_tickers = (
        "META,AMZN,AAPL,NFLX,GOOGL,NVDA,AMD,TSM,INTC,TXN,"
        "SPY,DIA,IWM,QQQ,EWU,MCHI,EWJ,INDA,EWA,GLD,"
        "SLV,UNG,USO,ORCL,ADBE,PANW,PLTR,SNPS,CRM,MSFT,"
        "SHOP,AXP,AMGN,BA,CAT,CSCO,CVX,GS,HD,HON,"
        "MCD,JNJ,KO,XLC,XLY,XLP,XLE,XLF,XLV,XLI,"
        "XLB,XLK,XLRE,XLU,JPM,BAC,WFC,HSBC,C,UBS"
    )

    us_index = "I:DJI,I:COMP,I:SPX,I:MRUT,I:VIX"
    europe_index = "I:GBDOW,I:NQEU,I:NQFR,I:NQDE,I:EDOW"
    asia_index = "I:NQASIA,I:HXC,I:NQJP,I:NQHK,I:ADOW"
    titan_index = "I:DJGT,I:UK50,I:FR30D,I:XLHK,I:DJAT"

    list_of_urls = [
        f"{polygon_snapshot_url}META,AMZN,AAPL,NFLX,GOOGL{polygon_end_url}",
        f"{polygon_snapshot_url}NVDA,AMD,TSM,INTC,TXN{polygon_end_url}",
        f"{polygon_snapshot_url}SPY,DIA,IWM,QQQ{polygon_end_url}",
        f"{polygon_snapshot_url}EWU,MCHI,EWJ,INDA,EWA{polygon_end_url}",
        f"{polygon_snapshot_url}GLD,SLV,UNG,USO{polygon_end_url}",
        f"{polygon_snapshot_url}ORCL,ADBE,PANW,PLTR,SNPS,CRM,MSFT,SHOP{polygon_end_url}",
        f"{polygon_snapshot_url}AXP,AMGN,CAT,CVX,GS,HD,HON,MCD,JNJ,KO{polygon_end_url}",
        f"{polygon_snapshot_url}XLC,XLY,XLP,XLE,XLF,XLV,XLI,XLB,XLK,XLRE,XLU{polygon_end_url}",
        f"{polygon_snapshot_url}JPM,BAC,WFC,HSBC,C,UBS{polygon_end_url}",
        f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers?tickers={",".join(list_of_crypto_tickers)}{polygon_end_url}",
        f"{forex_base_url}{",".join(list_of_fx_tickers)}{polygon_end_url}",
        # news starts at index 11
        f"{news_api_base_url}AMZN,META,AAPL,NFLX,GOOGL&items=9&page=1{end_news_api_url}",
        f"{news_api_base_url}NVDA,AMD,TSM,INTC,TXN&items=9&page=1{end_news_api_url}",
        f"https://stocknewsapi.com/api/v1/category?section=general&items=13&page=1{end_news_api_url}",
        f"{news_api_base_url}SPY,DIA,GLD,USO,EWU,INDA,QQQ,IWM,EWJ,EWU,MCHI&sortby=rank&items=13&page=1{end_news_api_url}",
        f"{news_api_base_url}MSFT,CRM,ADBE,SHOP,PLTR&items=6&page=1{end_news_api_url}",
        f"{news_api_base_url}JPM,BAC,WFC,HSBC,C,UBS&items=9&page=1{end_news_api_url}",
        f"https://cryptonews-api.com/api/v1/category?section=general&items=13&page=1&token={crypto_news_api_key}",
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={us_index}&limit={len(us_index.split(","))}{polygon_end_url}",
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={europe_index}&limit={len(europe_index.split(","))}{polygon_end_url}",
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={asia_index}&limit={len(asia_index.split(","))}{polygon_end_url}",
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={titan_index}&limit={len(titan_index.split(","))}{polygon_end_url}",
        f"https://api.polygon.io/v3/snapshot?ticker.any_of={all_data_tickers}&limit={len(all_data_tickers.split(","))}{polygon_end_url}",
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        all_data = list(results)

    status_check = [
        returned_item for returned_item in all_data if "error" not in returned_item
    ]
    if not status_check:
        context = {}
        context["api_down"] = True
        return render(request, "HomePage/homePage.html", context)

    name_map = inject_name_map(data=all_data[-1].get("results"))
    # MODIFYING CRYPTO AND FOREX MAP data KEYS
    for data in all_data[9].get("tickers", []):
        crypto_map[data.get("ticker")]["data"] = data

    if any_of:
        for data in all_data[10].get("results", []):
            forex_map[data.get("ticker")]["data"] = data
    else:
        for data in all_data[10].get("tickers", []):
            forex_map[data.get("ticker")]["data"] = data

    for item in all_data[0:8]:
        generic = item.get("tickers", [])
        generic.sort(key=lambda value: value["ticker"])
    context = {
        "current_type": "percent",
        "defaultDisplay": True,
        "any_of": any_of,
        "faang_stocks": data_assignment(
            all_data=all_data,
            index=0,
            key="tickers",
            name_map=name_map,
        ),
        "semi_conductors": data_assignment(
            all_data=all_data,
            index=1,
            key="tickers",
            name_map=name_map,
        ),
        "us_index_etf": data_assignment(
            all_data=all_data,
            index=2,
            key="tickers",
            name_map=name_map,
        ),
        "global_index_etf": data_assignment(
            all_data=all_data,
            index=3,
            key="tickers",
            name_map=name_map,
        ),
        "commodity_etfs": data_assignment(
            all_data=all_data,
            index=4,
            key="tickers",
            name_map=name_map,
        ),
        "software_stocks": data_assignment(
            all_data=all_data,
            index=5,
            key="tickers",
            name_map=name_map,
        ),
        "dowStocks": data_assignment(
            all_data=all_data,
            index=6,
            key="tickers",
            name_map=name_map,
        ),
        "sector_etfs": data_assignment(
            all_data=all_data,
            index=7,
            key="tickers",
            name_map=name_map,
        ),
        "big_banks": data_assignment(
            all_data=all_data,
            index=8,
            key="tickers",
            name_map=name_map,
        ),
        "us_indices": all_data[18].get("results"),
        "europe_indices": all_data[19].get("results"),
        "asia_indices": all_data[20].get("results"),
        "titan_indices": all_data[21].get("results"),
        "cryptoMap": crypto_map,
        "forexMap": forex_map,
        "faangNews": all_data[11].get("data", None),
        "semiNews": all_data[12].get("data", None),
        "mixedEtfNews": all_data[14].get("data", None),
        "softwareNews": all_data[15].get("data", None),
        "bankNews": all_data[16].get("data", None),
        "data_news": all_data[13].get("data", None),
        "cryptoNews": all_data[17].get("data", None),
    }

    return render(request, "HomePage/homePage.html", context)


def htmx_swap_changes(request, ticker=None, mtype=None, current_type=None, any_of=None):
    context = {}
    context["defaultDisplay"] = False
    context["Mtype"] = mtype
    model_instance = StockSearch.objects.filter(
        api_call_symbol=ticker,
        market_type=mtype,
    )
    context["value"] = model_instance.first()
    if current_type == "price":
        context["current_type"] = "percent"
    elif current_type == "percent":
        context["current_type"] = "price"
    # GET BASE URL
    base_url = get_swap_base_url(mtype=mtype)

    context["any_of"] = all(["any_of" in base_url, mtype == "fx"])

    # GET URL ENDING
    end_url = get_swap_end_url(
        mtype=mtype,
        context=context,
        polygon_api_key=os.getenv("POLYGON_API_KEY"),
    )
    url = f"{base_url}{model_instance.first().api_call_symbol}{end_url}"
    response = common_api_call(url)
    if "error" in response:
        return HttpResponse("Bad Request")

    context = assign_context(mtype=mtype, context=context, response=response)
    return HttpResponse(
        render_to_string(
            f"reusables/swapChanges/{mtype}SwapChangesPlaceholder.html",
            context,
        ),
    )


def view_all_view(request, value=None):
    if value == "Dow30":
        data = get_dow30()  # <-returns a json
        status_check = [
            json_item.get("data")
            for ticker, json_item in data.items()
            if bool(json_item.get("data"))
        ]

        api_down = not bool(status_check)
        context = {
            "dow30": data,  # <-- this is a LIST of results
            "type": "Dow30",
            "table_title": "DOW JONES INDUSTRIAL AVERAGE STOCKS",
            "api_down": api_down,
        }

    elif value == "Software":
        data = get_api_info(value=value)
        status_check = [
            payload.get("data")
            for industry, industry_payload in data.items()
            for ticker, payload in industry_payload.items()
            if bool(payload.get("data"))
        ]
        api_down = not bool(status_check)
        context = {
            "data": data,
            "type": "software",
            "api_down": api_down,
        }

    else:
        data = get_api_info(value=value)
        status_check = [
            payload.get("data")
            for industry, industry_payload in data.items()
            for ticker, payload in industry_payload.items()
            if bool(payload.get("data"))
        ]
        api_down = not bool(status_check)
        context = {
            "data": data,
            "type": value,
            "api_down": api_down,
        }

    return render(request, "viewAll/viewAll.html", context)
