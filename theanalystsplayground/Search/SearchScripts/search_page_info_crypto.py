import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta

import pytz

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def api_call_crypto(query_obj=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    crypto_news_api = os.getenv("CRYPTO_NEWS")
    current_date = datetime.now(pytz.utc)
    one_yr_ago = current_date - timedelta(days=365)
    list_of_urls = [
        f"https://api.polygon.io/v2/aggs/ticker/{query_obj.api_call_symbol}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&sort=asc&apikey={polygon_api_key}",
        f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/{query_obj.api_call_symbol}?apiKey={polygon_api_key}",
        f"https://cryptonews-api.com/api/v1?tickers={query_obj.public_ticker}&items=21&page=1&token={crypto_news_api}",
        f"https://api.polygon.io/v1/last/crypto/{query_obj.public_ticker}/USD?apiKey={polygon_api_key}",
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        list_results = list(results)

    return {
        "aggData": list_results[0],
        "snapshot": list_results[1],
        "news": list_results[2],
        "lastTrade": list_results[3],
    }
