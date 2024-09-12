import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from datetime import timedelta

import humanize
import pandas as pd
import pytz
from django.utils import timezone

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import fetch_api_info


def get_search_page_info(ticker=None, data=None):
    na = "N/A"
    d = {}
    snapshot_json = data[0]
    financials_json = data[1]
    dividend_json = data[2]
    ticker_details_json = data[3]
    market_status_json = data[4]
    price = snapshot_json.get("ticker", d).get("min", d).get("c", na)
    current_volume = snapshot_json.get("ticker", d).get("day", d).get("v", na)
    market_status = market_status_json.get("market", na)
    company_name = ticker_details_json.get("results", d).get("name", na)
    market_cap = humanize.intword(
        ticker_details_json.get("results", d).get("market_cap", na),
    )
    industry = ticker_details_json.get("results", d).get("sic_description", na)
    shares_outstanding = ticker_details_json.get("results", d).get(
        "share_class_shares_outstanding",
        na,
    )

    cik_string = ticker_details_json.get("results", d).get("cik", False)

    try:
        eps = financials_json["results"][0]["financials"]["income_statement"][
            "diluted_earnings_per_share"
        ]["value"]
        pe_ratio = price / eps
    except (KeyError, IndexError, TypeError):
        eps = pe_ratio = None

        # dividend section
    last_yr = timezone.now().year - 1
    prior_year = str(last_yr)

    if len(dividend_json.get("results", [])) > 0:
        dividend_freq = dividend_json.get("results")[0].get("frequency", None)
        last_div_payment = dividend_json.get("results")[0].get("cash_amount", None)
        last_div_payment_date = dividend_json.get("results")[0].get("record_date", None)
        try:
            dividend_df = pd.DataFrame(dividend_json.get("results"))
            dividend_df["pay_date"] = pd.to_datetime(dividend_df["pay_date"])
            last_year_div_df = dividend_df[dividend_df["pay_date"].dt.year == last_yr]
            last_yr_total_div_payment = last_year_div_df["cash_amount"].sum()
        except KeyError:
            last_yr_div_payments = [
                dividend.get("cash_amount", 0)
                for dividend in dividend_json.get("results")
                if dividend.get("pay_date", [])[0:4] == prior_year
            ]

            last_yr_total_div_payment = sum(last_yr_div_payments)
    else:
        dividend_freq = last_div_payment = last_div_payment_date = (
            last_yr_total_div_payment
        ) = None

    if any(
        [isinstance(shares_outstanding, int), isinstance(shares_outstanding, float)],
    ):
        shares_outstanding = f"{int(current_volume):,}"

    if any([isinstance(current_volume, int), isinstance(current_volume, float)]):
        current_volume = f"{int(current_volume):,}"

    return (
        snapshot_json,
        eps,
        pe_ratio,
        dividend_freq,
        last_div_payment,
        last_div_payment_date,
        last_yr_total_div_payment,
        current_volume,
        company_name,
        industry,
        shares_outstanding,
        market_cap,
        market_status,
        cik_string,
    )


def api_call_common_stock(ticker=None, competitor_query_obj=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    news_api_key = os.getenv("STOCK_NEWS_API_KEY")
    current_date = datetime.now(pytz.utc)
    one_yr_ago = current_date - timedelta(days=365)

    if competitor_query_obj:
        list_of_tickers = [obj.ticker for obj in competitor_query_obj]
        list_of_urls = [
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={polygon_api_key}",
            f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&apiKey={polygon_api_key}",
            f"https://api.polygon.io/v3/reference/dividends?ticker={ticker}&apiKey={polygon_api_key}",
            f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={polygon_api_key}",
            f"https://api.polygon.io/v1/marketstatus/now?apiKey={polygon_api_key}",
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&limit=800&apiKey={polygon_api_key}",
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers?tickers={','.join(list_of_tickers)}&include_otc=true&apiKey={polygon_api_key}",
            f"https://stocknewsapi.com/api/v1?tickers={ticker}&items=60&page=1&type=article&token={news_api_key}",
        ]
    else:
        list_of_tickers = None
        list_of_urls = [
            f"https://api.polygon.io/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}?apiKey={polygon_api_key}",
            f"https://api.polygon.io/vX/reference/financials?ticker={ticker}&apiKey={polygon_api_key}",
            f"https://api.polygon.io/v3/reference/dividends?ticker={ticker}&apiKey={polygon_api_key}",
            f"https://api.polygon.io/v3/reference/tickers/{ticker}?apiKey={polygon_api_key}",
            f"https://api.polygon.io/v1/marketstatus/now?apiKey={polygon_api_key}",
            f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{one_yr_ago.date()}/{current_date.date()}?adjusted=true&limit=800&apiKey={polygon_api_key}",
            f"https://stocknewsapi.com/api/v1?tickers={ticker}&items=60&page=1&type=article&token={news_api_key}",
        ]

    with ThreadPoolExecutor() as executor:
        results = executor.map(fetch_api_info, list_of_urls)
        list_results = list(results)
    if list_of_tickers:
        data_map = {
            "searchPageInfo": list_results[0:5],
            "aggData": list_results[5],
            "competitorData": list_results[6],
            "news": list_results[7],
        }
    else:
        data_map = {
            "searchPageInfo": list_results[0:5],
            "aggData": list_results[5],
            "competitorData": None,
            "news": list_results[6],
        }
    return data_map
