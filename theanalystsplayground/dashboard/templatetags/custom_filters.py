import re

import pandas as pd
from django import template

register = template.Library()


# DASHBOARD
@register.filter
def calculate_value(data):
    if any(
        [
            not data.get("data"),
            "error" in data.get("data", {}),
        ],
    ):
        return None
    lower_level = data.get("data", {})
    if lower_level.get("session"):
        session = lower_level.get("session", {})
        current_price = session.get("previous_close")
        try:
            return (current_price - data["price_per_unit"]) * data["shares_owned"]
        except (TypeError, AttributeError, KeyError):
            return None

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

    try:
        return (current_price - data["price_per_unit"]) * data["shares_owned"]

    except (TypeError, AttributeError, KeyError):
        return None


@register.filter
def calculate_forex_value(data):
    try:
        current_price = data["data"]["last_quote"]["ask"]
        result = (current_price - data["pricePerUnit"]) * data["sharesOwned"]
    except (TypeError, AttributeError, KeyError):
        return "Calculation Error"
    else:
        return result if result else "Calculation Error"


# FINANCIAL SUMMARY CUSTOM FILTER
@register.filter
def add_commas(value=None):
    if any(
        [
            not value,
            isinstance(value, str),
        ],
    ):
        return None
    minimum_length = 4
    if len(str(int(value))) < minimum_length:
        return value
    if any([isinstance(value, int), isinstance(value, float)]):
        converted = f"{int(value):,}"
    else:
        converted = None
    return converted


@register.filter
def get_asset_price(data):
    if not data:
        return None
    if "error" in data:
        return None
    minute = data.get("min", {})
    todays_perc = data.get("todaysChangePerc", 0)
    todays_change = data.get("todaysChange", 0)
    if data.get("updated", 0) == 0:
        return data.get("prevDay", {}).get("c", None)

    if all(
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
        use = data.get.get("prevDay", {})

    else:
        use = minute
    return use.get("c", None)


@register.filter
def get_asset_price_change(data):
    if not data:
        return None
    if "error" in data:
        return None
    minute = data.get("min", {})
    todays_perc = data.get("todaysChangePerc", 0)
    todays_change = data.get("todaysChange", 0)
    if data.get("updated", 0) == 0:
        use = data.get("prevDay", {})
        prev_open = use.get("o", None)
        prev_close = use.get("c", None)
        try:
            return prev_close - prev_open
        except TypeError:
            return None

    elif all(
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
        use = data.get("prevDay", {})
        prev_open = use.get("o")
        prev_close = use.get("c")
        try:
            todays_change = prev_close - prev_open
        except TypeError:
            return None
    return todays_change


@register.filter
def get_asset_percent_change(data):
    if not data:
        return None
    if "error" in data:
        return None
    minute = data.get("min", {})

    if data.get("updated", 0) == 0 or all(
        [
            minute.get("av", 0) == 0,
            minute.get("v", 0) == 0,
            minute.get("o", 0) == 0,
            minute.get("h", 0) == 0,
            minute.get("l", 0) == 0,
            minute.get("c", 0) == 0,
            data.get("todaysChangePerc", 0) == 0,
            data.get("todaysChange", 0) == 0,
        ],
    ):
        use = data.get("prevDay", {})
        prev_open = use.get("o")
        prev_close = use.get("c")
        try:
            todays_perc = ((prev_close - prev_open) / prev_open) * 100
        except (TypeError, ZeroDivisionError):
            return None

    else:
        todays_perc = data.get("todaysChangePerc", None)
    return todays_perc


@register.filter
def timestamp_converter(timestamp=None):
    if not timestamp:
        return "unavailable"
    nano_seconds = 19
    if len(str(timestamp)) >= nano_seconds:
        date_time = pd.to_datetime(timestamp, unit="ns")
    else:
        date_time = pd.to_datetime(timestamp, unit="ms")
    try:
        return date_time[0]
    except TypeError:
        return date_time


# crypto specific filters
@register.filter
def last_trade_price(data):
    if any([data.get("updated", 0) == 0, "error" in data]):
        return None
    return data.get("lastTrade", {}).get("p")


@register.filter
def last_trade_size(data):
    if not data:
        data = {"error": "bad request"}
    if any([data.get("updated", 0) == 0, "error" in data]):
        return None
    return data.get("lastTrade", {}).get("s")


# forex filter
@register.filter
def last_quote_ask(data):
    if not data:
        data = {"error": "bad request"}
    if data.get("lastQuote"):
        if any([data.get("updated", 0) == 0, "error" in data]):
            return None
        return data.get("lastQuote", {}).get("a")

    if data.get("last_quote"):
        if any(
            [
                data.get("last_quote", {}).get("last_updated", 0) == 0,
                "error" in data,
            ],
        ):
            return None

        return data.get("last_quote", {}).get("ask")
    return None


@register.filter
def last_quote_bid(data):
    if not data:
        data = {"error": "bad request"}
    if data.get("lastQuote"):
        if any([data.get("updated", 0) == 0, "error" in data]):
            return None

        return data.get("lastQuote", {}).get("b")
    if data.get("last_quote"):
        if any(
            [
                data.get("last_quote").get("last_updated", 0) == 0,
                "error" in data,
            ],
        ):
            return None

        return data.get("last_quote", {}).get("bid")
    return None


@register.filter
def get_asset_price_special_case(data):
    if not data:
        return None
    if "error" in data:
        return None
    if not data.get("session"):
        return None
    if data.get("last_updated", 0) == 0:
        price = data.get("session", {}).get("previous_close")
    else:
        todays_open = data.get("session", {}).get("open")
        todays_change = data.get("session", {}).get("change")
        try:
            price = todays_open + todays_change
        except TypeError:
            return None
    return price


@register.filter
def get_asset_price_change_special_case(data):
    try:
        if not data.get("session"):
            return None
    except AttributeError:
        return None
    if all(
        [
            data.get("session", {}).get("change") == 0,
            data.get("session", {}).get("change_percent") == 0,
        ],
    ):
        price = data.get("value")
        last_open = data.get("session", {}).get("open")
        try:
            change = price - last_open
        except TypeError:
            return None
    else:
        change = data.get("session", {}).get("change", None)
    return change


@register.filter
def get_asset_percent_change_special_case(data):
    try:
        if not data.get("session"):
            return None
    except AttributeError:
        return None
    if all(
        [
            data.get("session", {}).get("change") == 0,
            data.get("session", {}).get("change_percent") == 0,
        ],
    ):
        price = data.get("value")
        last_open = data.get("session", {}).get("open")
        try:
            percent_change = ((price - last_open) / price) * 100
        except (TypeError, ZeroDivisionError):
            return None
    else:
        percent_change = data.get("session", {}).get("change_percent")

    return percent_change


@register.filter
def process_ticker(ticker=None):
    if not ticker:
        return None
    return ticker[2:]


@register.filter
def forex_price_alternative(data):
    if not data or any(["error" in data, not data.get("session")]):
        return None
    return data.get("session", {}).get("previous_close")


@register.filter
def forex_price_change_alternative(data):
    if not data or any(["error" in data, not data.get("session")]):
        return None
    open_price = data.get("session", {}).get("open", 0)
    close_price = data.get("session", {}).get("close", 0)

    return close_price - open_price


@register.filter
def forex_percent_change_alternative(data):
    if not data:
        return None
    if any(["error" in data, not data.get("session")]):
        return None
    open_price = data.get("session", {}).get("open", 0)
    close_price = data.get("session", {}).get("close", 0)
    return ((close_price - open_price) / open_price) * 100

    # HANDLE NAMES WITH / IN THEM.  "/" IN NAMES CAUSING ERROR WHEN PASSING COMPANYNAME


@register.filter
def name_check_and_fix(company_name=None):
    if "/" in company_name:
        pattern = r"\b[a-zA-Z0-9]\w*\b"
        return " ".join(re.findall(pattern, company_name))
    return company_name
