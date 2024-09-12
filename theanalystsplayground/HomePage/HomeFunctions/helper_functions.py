import requests
from requests.exceptions import Timeout

from theanalystsplayground.currencies.helperFunctions.currency_helpers import get_url


def fetch_api_info(url_string):
    try:
        response = requests.get(url_string, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Timeout:
        return {"error": "bad request"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    else:
        return response.json()


def fetch_api_info_special_case(url_string):
    try:
        response = requests.get(url_string[1], timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Timeout:
        return (url_string[0], {"error": "bad request"})
    except requests.exceptions.RequestException as e:
        return (url_string[0], {"error": str(e)})
    else:
        return (url_string[0], response.json())


def common_api_call(url_string):
    try:
        response = requests.get(url_string, timeout=5)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Timeout:
        return {"error": "bad request"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    else:
        return response.json()


def final_map_creation(data=None, name_map=None):
    for asset in data:
        asset["name"] = name_map.get(asset.get("ticker"))
    return data


def data_assignment(all_data, index, key, name_map):
    items = all_data[index].get(key, [])
    return final_map_creation(data=items, name_map=name_map)


def get_swap_base_url(mtype):
    if mtype == "crypto":
        base_url = (
            "https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers/"
        )

    elif mtype == "fx":
        base_url = get_url(single_ticker=True)

    elif mtype == "stocks":
        base_url = (
            "https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/"
        )

    elif mtype == "indices":
        base_url = "https://api.polygon.io/v3/snapshot/indices?ticker.any_of="
    return base_url


def get_swap_end_url(mtype, context, polygon_api_key):
    if mtype == "indices" or all([context.get("any_of"), mtype == "fx"]):
        end_url = f"&apiKey={polygon_api_key}"
    else:
        end_url = f"?apiKey={polygon_api_key}"
    return end_url


def assign_context(mtype, context, response):
    context["data"] = None
    if mtype == "fx":
        if context["any_of"]:
            context["data"] = response.get("results", [])[0]
        else:
            context["data"] = response.get("ticker")
    elif mtype == "indices":
        context["data"] = response.get("results", [])[0]
    else:
        context["data"] = response.get("ticker")
    return context
