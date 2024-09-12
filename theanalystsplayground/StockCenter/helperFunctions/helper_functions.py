import os
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    fetch_api_info_special_case,
)
from theanalystsplayground.Search.models import StocksData


def get_industry_drop_down_menu_options():
    industry_df = pd.DataFrame(StocksData.objects.all().values())
    industries = industry_df["industry"].unique()
    industries.sort()
    return industries


def get_sector_drop_down_menu_options():
    sectors_df = pd.DataFrame(StocksData.objects.all().values())
    sectors = sectors_df["sector"].unique()
    sectors.sort()
    return sectors


def get_sector_api_data(value=None):
    polygon_api_key = os.environ.get("POLYGON_API_KEY")
    query = StocksData.objects.filter(sector=value)
    sector_df = pd.DataFrame(query.values())
    data_map = {
        key: StocksData.objects.filter(industry=key)
        for key in sector_df.industry.unique()
    }
    list_of_urls = []
    data = {}
    for industry, stocks in data_map.items():
        if industry not in data:
            list_of_urls.append(
                (
                    industry,
                    (
                        f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?"
                        f"tickers={','.join(ticker.ticker for ticker in stocks)}&"
                        f"apiKey={polygon_api_key}"
                    ),
                ),
            )
            data[industry] = {}
        for stock in stocks:
            data[industry][stock.ticker] = {
                "company_name": stock.company_name,
                "data": None,
            }

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info_special_case, list_of_urls)
        results_list = list(results)
    for industry_returned, data_returned in results_list:
        if "error" in data_returned:
            continue
        for each_item in data_returned.get("tickers"):
            data[industry_returned][each_item["ticker"]]["data"] = each_item
    return data
