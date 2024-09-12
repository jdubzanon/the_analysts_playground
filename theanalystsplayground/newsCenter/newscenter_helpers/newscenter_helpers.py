import os
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.exceptions import Timeout


def newscenter_api_call(url_string):
    try:
        response = requests.get(url_string, timeout=2)
        response.raise_for_status()  # Raise an exception for HTTP errors
    except Timeout:
        return {"timeout_error": "bad request"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    else:
        return response.json()


def querytracker_injection():
    return {
        "ticker": None,
        "sentiment": None,
        "type": {
            "article": None,
            "video": None,
        },
        "source": {
            "Bitcoin+Magazine": None,
            "Coindesk": None,
            "Bitcoin": None,
            "Blockchain+News": None,
            "BeInCrypto": None,
            "Bitcoinist": None,
            "Blockworks": None,
            "Crypto+Daily": None,
            "Coingape": None,
            "Crypto+Briefing": None,
            "Crypto+Economy": None,
            "CryptoNews": None,
            "Dailycoin": None,
            "Decrypt": None,
            "Crypto+Reporter": None,
            "TheNewsCrypto": None,
            "CNBC": None,  # checked
            "Forbes": None,  # checked
            "Benzinga": None,  # checked
            "Fox+Business": None,  # checked
            "New+York+Post": None,  # checked
            "Barrons": None,  # checked
            "Bloomberg+Markets+and+Finance": None,  # checked
            "Business+Insider": None,  # checked
            "ETF+Trends": None,  # checked
            "Investopedia": None,
            "Market+Watch": None,
            "Reuters": None,
            "Schwab+Network": None,
            "Seeking+Alpha": None,
            "Yahoo+Finance": None,
            "Zacks+Investment+Research": None,
        },
    }


def fetch_info(*args):
    with ThreadPoolExecutor() as executor:
        return executor.map(newscenter_api_call, args)


def get_pagination_endpoint(mtype, receiving_string, ticker=None):
    crypto_api_key = os.getenv("CRYPTO_NEWS")
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    if mtype == "crypto":
        if "tickers" in receiving_string:
            api_call_string = (
                f"https://cryptonews-api.com/api/v1?{receiving_string}{crypto_api_key}"
            )
        else:
            api_call_string = (
                f"https://cryptonews-api.com/api/v1/{receiving_string}{crypto_api_key}"
            )
    elif "tickers" in receiving_string:
        api_call_string = (
            f"https://stocknewsapi.com/api/v1?{receiving_string}{news_api_key}"
        )
    else:
        api_call_string = (
            f"https://stocknewsapi.com/api/v1/{receiving_string}{news_api_key}"
        )
    return api_call_string


def set_initial_endpoint(market_type, query_tracker):
    crypto_api_key = os.getenv("CRYPTO_NEWS")
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    url_tracker = {
        "base_url": None,
        "url_ending": None,
    }

    if market_type == "crypto":
        if query_tracker["ticker"]:
            url_tracker["base_url"] = "https://cryptonews-api.com/api/v1?tickers="
        else:
            url_tracker["base_url"] = (
                "https://cryptonews-api.com/api/v1/category?section=general"
            )

        url_tracker["url_ending"] = (
            f"&sortby=rank&items=100&page=1&token={crypto_api_key}"
        )

    else:
        if query_tracker["ticker"]:
            url_tracker["base_url"] = "https://stocknewsapi.com/api/v1?tickers="
        else:
            url_tracker["base_url"] = (
                "https://stocknewsapi.com/api/v1/category?section=general"
            )
        url_tracker["url_ending"] = (
            f"&sortby=rank&items=100&page=1&token={news_api_key}"
        )

    return url_tracker


def set_final_endpoint_with_ticker(
    ticker,
    source_bucket,
    string_query_tracker,
    base_url,
    url_ending,
):
    if source_bucket:
        with_ticker_address = (
            f"{base_url}{ticker.upper()}"
            f"&source={",".join(source_bucket)}"
            f"{''.join(string_query_tracker)}{url_ending}"
        )
    else:
        with_ticker_address = (
            f"{base_url}{ticker.upper()}{"".join(string_query_tracker)}{url_ending}"
        )
    return with_ticker_address


def set_final_endpoint_without_ticker(
    source_bucket,
    string_query_tracker,
    base_url,
    url_ending,
):
    if source_bucket:
        without_ticker_url = (
            f"{base_url}&source={",".join(source_bucket)}"
            f"{"".join(string_query_tracker)}{url_ending}"
        )
    else:
        without_ticker_url = f"{base_url}{"".join(string_query_tracker)}{url_ending}"
    return without_ticker_url


def get_ticker_snapshot_urls(
    ticker,
    market_type,
    polygon_api_key,
):
    url_tracker = {
        "ticker_price_url": None,
        "company_name_url": None,
    }

    if market_type == "crypto":
        url_tracker["ticker_price_url"] = (
            f"https://api.polygon.io/v2/snapshot/locale/global/markets/"
            f"crypto/tickers/X:{ticker.upper()}"
            f"USD?apiKey={polygon_api_key}"
        )
        url_tracker["company_name_url"] = (
            f"https://api.polygon.io/v3/snapshot?ticker.any_of="
            f"X:{ticker.upper()}USD&limit=10"
            f"&apiKey={polygon_api_key}"
        )

    else:
        url_tracker["ticker_price_url"] = (
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/"
            f"stocks/tickers/{ticker.upper()}"
            f"?apiKey={polygon_api_key}"
        )
        url_tracker["company_name_url"] = (
            f"https://api.polygon.io/v3/reference/tickers/"
            f"{ticker.upper()}?apiKey={polygon_api_key}"
        )
    return url_tracker


def create_passing_string(source_bucket, string_query_tracker, ticker):
    if ticker:
        if source_bucket:
            passing_string = (
                f"tickers={ticker}"
                f"&source={",".join(source_bucket)}{"".join(string_query_tracker)}"
                f"&sortby=rank&items=100&page=1&token="
            )

        else:
            passing_string = (
                f"tickers={ticker}"
                f"{"".join(string_query_tracker)}&sortby=rank&items=100&page=1&token="
            )
    elif source_bucket:
        passing_string = (
            f"category?section=general&source={",".join(source_bucket)}"
            f"{"".join(string_query_tracker)}&items=100&page=1&token="
        )
    else:
        passing_string = (
            f"category?section=general"
            f"{"".join(string_query_tracker)}&items=100&page=1&token="
        )
    return passing_string


def add_to_context_with_ticker(**data):
    if data.get("ticker_found") and not data.get("snapshot_apicall_failed"):
        if data.get("market_type") == "crypto":
            data["context"]["cryptoTicker"] = data.get("ticker")
            data["context"]["priceDetails"] = data.get("price_details").get("ticker")
            data["context"]["infoDataTicker"] = data.get("ticker")
            data["context"]["companyDetails"] = data.get("company_details", {}).get(
                "results",
                [],
            )[0]

        else:
            data["context"]["companyDetails"] = data.get("company_details", {}).get(
                "results",
            )
            data["context"]["priceDetails"] = data.get("price_details").get("ticker")
            data["context"]["infoDataTicker"] = data.get("ticker")
    else:
        data["context"]["infoDataTicker"] = data.get("ticker")
        data["context"]["companyDetails"] = None
        data["context"]["priceDetails"] = None
        data["context"]["ticker_found_error"] = True
    return data.get("context")


def process_query_parameters(
    request,
    source_bucket,
    query_tracker,
):
    for choices in request.GET:
        if choices in query_tracker["source"]:
            source_bucket.append(choices)
        elif choices in query_tracker["type"]:
            query_tracker["type"][choices] = request.GET.get(choices)
        elif choices == "ticker":
            query_tracker[choices] = request.GET.get("ticker").upper()
        elif choices == "market_type":
            continue
        else:
            query_tracker[choices] = request.GET.get(choices)

    return {
        "query_tracker": query_tracker,
        "source_bucket": source_bucket,
    }


def set_string_query_tracker(
    request,
    query_tracker,
    string_query_tracker,
):
    # LOOPING THROUGH query_tracker DICT AND LOOKING FOR CHANGED VALUES
    for key in query_tracker:
        if key == "type":
            for dict_item in query_tracker[key]:
                if query_tracker.get(key).get(dict_item) is not None:
                    string_query_tracker.append(f"&type={dict_item}")
        elif all(
            [
                query_tracker[key] is not None,
                key != "type",
                key != "source",
                key != "ticker",
            ],
        ):
            string_query_tracker.append(f"&{key}={request.GET.get(key)}")

    return string_query_tracker
