import calendar
from datetime import time

import pandas as pd
import pytz
from django.utils import timezone

from theanalystsplayground.Search.models import StockSearch


def get_url(single_ticker=None):
    # FOREX MARKET OPENS 5PM EST SUNDAY AND CLOSES 4PM EST FRIDAY
    today_date = timezone.now()
    day = calendar.day_name[today_date.weekday()]
    # SATURDAY AND SUNDAY
    if day == "Sunday":
        six_oclock = time(18, 0)
        date_obj = timezone.now()
        est = pytz.timezone("US/Eastern")
        now_est_timezone = date_obj.astimezone(est)
        current_time = now_est_timezone.time()
        if current_time < six_oclock:
            # THIS IS IF FOREX IS DOWN GO TO THIS ENDPOINT
            base_url = "https://api.polygon.io/v3/snapshot?ticker.any_of="
        elif not single_ticker:
            #    THIS IS FOR HOMEPAGE AND MORE CURRENCIES,
            #   FOREX IS NOT DOWN,
            # ITS SUNDAY I NEED MULTIPLE TICKER ENDPOINT
            base_url = (
                "https://api.polygon.io/v2/snapshot/locale/"
                "global/markets/forex/tickers?tickers="
            )
        else:
            # THIS IS FOR NOT HOMEPAGE,
            # FOREX IS NOT DOWN AND SUNDAY: SINGLE TICKER NEEDED
            base_url = "https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers/"
    elif day == "Saturday":
        # FOREX IS DOWN GO TO THIS ENDPOINT ON SATURDAYS
        base_url = "https://api.polygon.io/v3/snapshot?ticker.any_of="
    elif not single_ticker:
        # HOMEPAGE,MORE CURRENCIES,DASHBOARD NEED MULTIPLE TICKERS
        base_url = "https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers?tickers="
    else:
        # NEED SINGLE TICKER
        base_url = (
            "https://api.polygon.io/v2/snapshot/locale/global/markets/forex/tickers/"
        )
    return base_url


class QueryHandler:
    def __init__(self, letter):
        self.letter = letter
        self.database_query = StockSearch.objects.filter(
            base_currency__startswith=letter.upper(),
            market_type="fx",
        )
        self.filtered_df = None
        self.zipped_values = None
        if self.database_query.exists():
            fx_dataframe = pd.DataFrame(self.database_query.values())
            self.filtered_df = fx_dataframe[["base_currency", "base_currency_name"]]

            self.zipped_values = zip(
                self.filtered_df["base_currency"].unique(),
                self.filtered_df["base_currency_name"].unique(),
                strict=False,
            )
