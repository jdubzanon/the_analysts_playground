import os
from concurrent.futures import ThreadPoolExecutor

from theanalystsplayground.currencies.helperFunctions.currency_helpers import get_url
from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def tickers_list_generator(model_instance, mtype):
    tickers = [
        ticker.api_call_symbol
        for ticker in model_instance
        if ticker.market_type == mtype
    ]
    return tickers if tickers else None


def organize_dashboard_data(all_data, results):
    for json_response in results:
        if json_response.get("tickers"):
            bundle = json_response.get("tickers", [])
        elif json_response.get("results", []):
            bundle = json_response.get("results", [])
        elif json_response.get("error"):
            continue
        for each_item in bundle:
            all_data[each_item.get("ticker")]["data"] = each_item
    return all_data


def portfolio_data_injector(model_instance=None):
    # ADDED MORE THINGS TO DICTIONARY
    # THIS IS NOT THE SAME FUNCTION AS watchlistDataInjector
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    all_data = {}
    crypto_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="crypto",
    )
    stock_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="stocks",
    )
    forex_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="fx",
    )

    list_of_urls = []

    for stock in model_instance:
        all_data[stock.api_call_symbol] = {
            "ticker": stock.ticker,
            "company_name": stock.company_name,
            "market_type": stock.market_type,
            "api_call_symbol": stock.api_call_symbol,
            "price_per_unit": stock.price_per_unit,
            "shares_owned": stock.shares_owned,
            "data": None,
        }

    if crypto_tickers:
        list_of_urls.append(
            f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers?tickers={','.join(crypto_tickers)}&apiKey={polygon_api_key}",
        )
    if forex_tickers:
        base_url = get_url()
        end_url = f"&apiKey={polygon_api_key}"
        list_of_urls.append(f"{base_url}{','.join(forex_tickers)}{end_url}")
    if stock_tickers:
        list_of_urls.append(
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={','.join(stock_tickers)}&apiKey={polygon_api_key}",
        )

    with ThreadPoolExecutor() as executor:
        response = executor.map(fetch_api_info, list_of_urls)
        results = list(response)

    return organize_dashboard_data(all_data=all_data, results=results)


def watchlist_data_injector(model_instance=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    crypto_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="crypto",
    )
    stock_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="stocks",
    )
    forex_tickers = tickers_list_generator(model_instance=model_instance, mtype="fx")
    index_tickers = tickers_list_generator(
        model_instance=model_instance,
        mtype="indices",
    )
    list_of_urls = []

    all_data = {}
    for each_obj in model_instance:
        all_data[each_obj.api_call_symbol] = {
            "ticker": each_obj.ticker,
            "company_name": each_obj.company_name,
            "market_type": each_obj.market_type,
            "data": None,
        }

    if crypto_tickers:
        list_of_urls.append(
            f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers?tickers={','.join(crypto_tickers)}&apiKey={polygon_api_key}",
        )
    if forex_tickers:
        base_url = get_url()
        end_url = f"&apiKey={polygon_api_key}"
        list_of_urls.append(f"{base_url}{','.join(forex_tickers)}{end_url}")
    if stock_tickers:
        list_of_urls.append(
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={','.join(stock_tickers)}&apiKey={polygon_api_key}",
        )
    if index_tickers:
        list_of_urls.append(
            f"https://api.polygon.io/v3/snapshot/indices?ticker.any_of={",".join(index_tickers)}&apiKey={polygon_api_key}",
        )

    with ThreadPoolExecutor() as executor:
        response = executor.map(fetch_api_info, list_of_urls)
        results = list(response)

    return organize_dashboard_data(all_data=all_data, results=results)


def get_current_price(data=None):
    lower_level = data.get("data", {})
    if lower_level.get("session", {}):
        return lower_level.get("session", {}).get("previous_close", 0)
    minute = lower_level.get("min", {})
    todays_perc = lower_level.get("todaysChangePerc", 0)
    todays_change = lower_level.get("todaysChange", 0)
    if lower_level.get("updated", 0) == 0 or all(
        [
            minute.get("av", 0) == 0,
            minute.get("v", 0) == 0,
            minute.get("o", 0) == 0,
            minute.get("h", 0) == 0,
            minute.get("l", 0) == 0,
            minute.get("c", 0) == 0,
            todays_perc == 0,
            todays_change == 0,
        ],
    ):
        current_price = lower_level.get("prevDay", {}).get("c")

    else:
        current_price = minute.get("c")
    return current_price


def get_totals(context):
    total = []
    for data in context["Portfolio"].values():
        try:
            ppu = data.get("price_per_unit")
            shares = data.get("shares_owned")
            cp = get_current_price(data=data)
            if all([ppu is not None, shares is not None, cp is not None]):
                total.append((cp - ppu) * shares)
        except (AttributeError, KeyError, TypeError):
            continue
    return total if total else False
