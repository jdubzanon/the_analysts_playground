import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta

import pytz

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def api_call_index(query_obj=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    current_date = datetime.now(pytz.utc)
    one_yr_ago = current_date - timedelta(days=365)
    list_of_urls = [
        f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={query_obj.api_call_symbol}&apiKey={polygon_api_key}",
        f"https://api.polygon.io/v2/aggs/ticker/{query_obj.api_call_symbol}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&sort=asc&apiKey={polygon_api_key}",
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        results_list = list(results)

    return {
        "snapshot": results_list[0],
        "aggData": results_list[1],
    }
