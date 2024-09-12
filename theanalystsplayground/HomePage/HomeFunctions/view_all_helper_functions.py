import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)
from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    fetch_api_info_special_case,
)
from theanalystsplayground.Search.models import StocksData


def get_dow30(value=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    data_map = {}
    dow30 = [
        "AMZN",
        "AXP",
        "AMGN",
        "AAPL",
        "BA",
        "CAT",
        "CSCO",
        "CVX",
        "GS",
        "HD",
        "HON",
        "IBM",
        "INTC",
        "JNJ",
        "KO",
        "JPM",
        "MCD",
        "MMM",
        "MRK",
        "MSFT",
        "NKE",
        "PG",
        "TRV",
        "UNH",
        "CRM",
        "VZ",
        "WMT",
        "DIS",
        "DOW",
    ]
    for ticker in dow30:
        data_map[ticker] = {
            "obj": StocksData.objects.get(ticker=ticker),
            "data": None,
        }

    url = f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={','.join(dow30)}&apiKey={polygon_api_key}"
    data = common_api_call(url)
    for item in data.get("tickers", []):
        data_map.get(item.get("ticker"))["data"] = item
    return data_map


def get_api_info(value=None):  # <--- Generalized handles multipe get more links
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    data_map = {}
    list_of_urls = []
    if value == "Software":
        industry_choices = [
            "Internet Content & Information",
            "Software - Application",
            "Software - Infrastructure",
        ]
        industry_tickers_map = {
            key: StocksData.objects.filter(industry=key) for key in industry_choices
        }

    else:  # original
        polygon_api_key = os.getenv("POLYGON_API_KEY")
        column_values = StocksData.objects.filter(industry__contains=value)
        column_values_df = pd.DataFrame(column_values.values())
        industry_tickers_map = {
            key: StocksData.objects.filter(industry=key)
            for key in column_values_df["industry"].unique()
        }

    # PREP
    base_url = (
        "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers="
    )
    end_url = f"&apiKey={polygon_api_key}"
    for industry, stocks in industry_tickers_map.items():
        if industry not in data_map:
            list_of_urls.append(
                (
                    industry,
                    (
                        f"{base_url}"
                        f"{','.join([ticker.ticker for ticker in stocks])}"
                        f"{end_url}"
                    ),
                ),
            )
            data_map[industry] = {}
        for stock in stocks:
            data_map[industry][stock.ticker] = {
                "company_name": stock.company_name,
                "data": None,
            }

    # FIRE
    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info_special_case, list_of_urls)
        list_results = list(results)
    # CATCH
    for industry_returned, data_returned in list_results:
        if "error" in data_returned:
            continue
        for each_item in data_returned.get("tickers"):
            data_map[industry_returned][each_item["ticker"]]["data"] = each_item

    return data_map
