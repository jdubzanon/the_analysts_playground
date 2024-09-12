import os
import string

from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from theanalystsplayground.currencies.helperFunctions.currency_helpers import (
    QueryHandler,
)
from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)
from theanalystsplayground.Search.models import StockSearch

from .helperFunctions.currency_helpers import get_url


def view_forex_currencies(request, letter=None, user_id=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    if request.method == "GET":
        query = QueryHandler(letter)
        try:
            currency = StockSearch.objects.filter(
                base_currency=query.filtered_df.iloc[0].base_currency,
                market_type="fx",
            )
        except AttributeError:
            return render(
                request,
                "currencies/moreForex.html",
                {
                    "populated": False,
                    "error": True,
                },
            )
        tickers_bucket = [ticker.api_call_symbol for ticker in currency]
        fx_map = {
            item.api_call_symbol: {
                "ticker": item.public_ticker,
                "market_type": item.market_type,
                "company_name": item.company_name,
                "data": None,
            }
            for item in currency
        }
        # Check day and time due to forex market constraints
        base_url = get_url()
        any_of = "any_of" in base_url
        end_url = f"&apiKey={polygon_api_key}"
        url = f"{base_url}{",".join(tickers_bucket)}{end_url}"
        res_json = common_api_call(url)
        if "error" in res_json:
            return HttpResponse(
                render_to_string(
                    "reusables/moreItemsPlaceholder.html",
                    {
                        "error": True,
                    },
                ),
            )
        if any_of:
            for data in res_json.get("results", []):
                fx_map[data.get("ticker")]["data"] = data
        else:
            for data in res_json.get("tickers", []):
                fx_map[data.get("ticker")]["data"] = data
        context = {
            "alphabet": list(string.ascii_uppercase),
            "any_of": any_of,
            "fxTypes": query.zipped_values,
            "fxMap": fx_map,
            "populated": True,
            "letter": "AUD",
        }
    # POST OPERATIONS
    # RENDERS CURRENCIES THAT STARTSWITH LETTER
    if request.method == "POST":
        query = QueryHandler(letter)
        context = {
            "currencies": query.zipped_values,
            "populated": query.database_query.exists(),
        }
        return HttpResponse(
            render_to_string(
                "reusables/fxTypePlaceholder.html",
                context,
            ),
        )
    return render(request, "currencies/moreForex.html", context)


def view_crypto_currencies(request, letter=None, user_id=None):
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    context = {}
    context["alphabet"] = list(string.ascii_uppercase)
    model_instance = StockSearch.objects.filter(
        public_ticker__startswith=letter.upper(),
        market_type="crypto",
    )

    crypto_data = {
        key.api_call_symbol: {
            "ticker": key.public_ticker,
            "company_name": key.company_name,
            "market_type": "crypto",
            "data": None,
        }
        for key in model_instance
    }
    url = (
        f"https://api.polygon.io/v2/snapshot/locale/global/markets/crypto/tickers?tickers="
        f"{",".join([stock.api_call_symbol for stock in model_instance])}"
        f"&apiKey={polygon_api_key}"
    )
    response = common_api_call(url)
    if "error" in response:
        context["error"] = True
        return HttpResponse(
            render_to_string(
                "reusables/moreItemsPlaceholder.html",
                context,
            ),
        )

    res_json = response.get("tickers", [])
    for data in res_json:
        crypto_data[data.get("ticker")]["data"] = data
    if request.method == "GET":
        context = {
            "alphabet": list(string.ascii_uppercase),
            "cryptoData": crypto_data,
            "letter": letter.upper(),
        }
        return render(request, "currencies/moreCrypto.html", context)

    # method is "POST"
    context = {
        "alphabet": list(string.ascii_uppercase),
        "dataMap": crypto_data,
        "letter": letter.upper(),
    }
    return HttpResponse(
        render_to_string(
            "reusables/moreItemsPlaceholder.html",
            context,
        ),
    )


def switch_currencies(request, currency=None):
    # handles when a currency is clicked
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    context = {}
    fx = StockSearch.objects.filter(base_currency=currency.upper(), market_type="fx")
    tickers_bucket = [ticker.api_call_symbol for ticker in fx]
    fx_map = {
        item.api_call_symbol: {
            "ticker": item.public_ticker,
            "market_type": item.market_type,
            "company_name": item.company_name,
            "data": None,
        }
        for item in fx
    }
    base_url = get_url()
    if "any_of" in base_url:
        context["any_of"] = True
    else:
        context["any_of"] = False
    end_url = f"&apiKey={polygon_api_key}"
    url = f"{base_url}{",".join(tickers_bucket)}{end_url}"
    res_json = common_api_call(url)
    if "error" in res_json:
        context["error"] = True
        return HttpResponse(
            render_to_string(
                "reusables/moreItemsPlaceholder.html",
                context,
            ),
        )
    if context["any_of"]:
        for data in res_json.get("results", []):
            fx_map[data.get("ticker")]["data"] = data
    else:
        for data in res_json.get("tickers"):
            fx_map[data.get("ticker")]["data"] = data
    context["dataMap"] = fx_map
    context["populated"] = True
    context["letter"] = currency
    return HttpResponse(
        render_to_string(
            "reusables/moreItemsPlaceholder.html",
            context,
        ),
    )
