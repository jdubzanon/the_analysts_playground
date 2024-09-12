import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta

import pytz

from theanalystsplayground.currencies.helperFunctions.currency_helpers import get_url
from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def api_call_forex(query_obj=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    current_date = datetime.now(pytz.utc)
    one_yr_ago = current_date - timedelta(days=365)
    base_url = get_url(single_ticker=True)
    if "any_of" in base_url:
        end_url = f"&apiKey={polygon_api_key}"
    else:
        end_url = f"?apiKey={polygon_api_key}"
    list_of_urls = [
        f"https://api.polygon.io/v2/aggs/ticker/{query_obj.api_call_symbol}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&sort=asc&apiKey={polygon_api_key}",
        f"{base_url}{query_obj.api_call_symbol}{end_url}",
        f"https://api.polygon.io/v1/conversion/{query_obj.base_currency}/{query_obj.currency}?amount=1.00&precision=2&apiKey={polygon_api_key}",
        f"https://api.polygon.io/v1/marketstatus/now?apiKey={polygon_api_key}",
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        list_results = list(results)

    return {
        "aggData": list_results[0],
        "snapshot": list_results[1],
        "convertedCurrency": list_results[2],
        "marketStatus": list_results[3].get("currencies", {}).get("fx", "unavailable"),
    }
