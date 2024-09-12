import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta

import humanize
import pandas as pd
import pytz
from django.utils import timezone

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def api_call_etf(ticker=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    current_date = datetime.now(pytz.utc)
    one_yr_ago = current_date - timedelta(days=365)
    list_of_urls = [
        f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={polygon_api_key}",
        f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={polygon_api_key}",
        f"https://api.polygon.io/v3/reference/dividends?ticker={ticker}&apiKey={polygon_api_key}",
        f"https://api.polygon.io/v1/marketstatus/now?apiKey={polygon_api_key}",
        f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&&apiKey={polygon_api_key}",
        f"https://stocknewsapi.com/api/v1?tickers={ticker}&items=60&page=1&type=article&token={news_api_key}",
    ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        json_data = list(results)
    return {
        "searchPageInfo": json_data[0:4],
        "aggData": json_data[4],
        "news": json_data[5],
    }


def get_etf_search_page_info(ticker=None, data=None):
    d = {}
    na = "N/A"
    # JSONS
    snapshot = data[0]
    details_json = data[1]
    dividend_json = data[2]
    market_status_json = data[3]
    price = snapshot.get("ticker", d).get("min", d).get("c", na)
    previous_close = snapshot.get("ticker", d).get("prevDay", d).get("c", na)
    current_volume = snapshot.get("ticker", d).get("min", d).get("av", na)
    etf_name = details_json.get("results", d).get("name", na)
    shares_outstanding = details_json.get("results", d).get(
        "share_class_shares_outstanding",
        na,
    )
    market_status = market_status_json.get("market", na)
    # CREATE MARKET CAP THEN CONVERT TO HUMAN READABLE
    if all(
        [
            any(
                [
                    isinstance(price, int),
                    isinstance(price, float),
                ],
            ),
            any(
                [
                    isinstance(shares_outstanding, int),
                    isinstance(shares_outstanding, float),
                ],
            ),
            price != 0,
            price != na,
            shares_outstanding != 0,
            shares_outstanding != na,
        ],
    ):
        market_cap_calculate = price * shares_outstanding
        market_cap_convert = str(int(market_cap_calculate)).replace(",", "")
        market_cap = humanize.intword(market_cap_convert)
    else:
        market_cap = na

    # DIVIDENDS AND DIVIDEND CALCULATIONS

    if dividend_json.get("results"):
        last_div_payment = dividend_json.get("results")[0].get("cash_amount")
        if len(dividend_json.get("results")) > 0:
            dividend_freq = dividend_json.get("results")[0].get("frequency")

            dividend_df = pd.DataFrame(dividend_json.get("results"))
            prior_year = int(timezone.now().year - 1)
            dividend_df["pay_date"] = pd.to_datetime(dividend_df["pay_date"])
            prior_year_df = dividend_df[dividend_df["pay_date"].dt.year == prior_year]

            last_yr_div_total = prior_year_df["cash_amount"].sum()
            last_div_payment_date = dividend_df["pay_date"][0].date()
        else:
            dividend_freq = last_yr_div_total = last_div_payment_date = (
                last_div_payment
            ) = na
    else:
        dividend_freq = last_yr_div_total = last_div_payment_date = last_div_payment = (
            na
        )

    return (
        snapshot,
        previous_close,
        current_volume,
        etf_name,
        dividend_freq,
        last_yr_div_total,
        market_status,
        shares_outstanding,
        last_div_payment_date,
        market_cap,
        last_div_payment,
    )
