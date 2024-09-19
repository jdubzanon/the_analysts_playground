import os
from datetime import timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone

from theanalystsplayground.HomePage.HomeFunctions.helper_functions import (
    common_api_call,
)


def aggregate_data(ticker=None, res_j=None):
    count = res_j.get("resultsCount")
    if not count:
        count = res_j.get("queryCount")
    if not count:
        return ("N.A", "N.A")
    if count > 0:
        data = res_j["results"]
        aggregate_df = pd.DataFrame(data, index=range(len(data)))
    list_of_highs = np.flip(aggregate_df["h"].tolist())
    list_of_lows = np.flip(aggregate_df["l"].tolist())
    fifty_two_wk_high = list_of_highs.max()
    fifty_two_wk_low = list_of_lows.min()
    return (fifty_two_wk_high, fifty_two_wk_low)


def get_chart(time_frame=None, ticker=None):
    date_today = timezone.now().date()
    polygon_api_key = os.getenv("POLYGON_API_KEY")
    if time_frame == "oneWeek":
        user_time_frame = date_today - timedelta(days=7)
        title = "One Week 30 Minute Chart"
    elif time_frame == "threeMos":
        user_time_frame = date_today - timedelta(days=31 * 3)
        title = "Three Months Daily Chart"
    elif time_frame == "sixMos":
        user_time_frame = date_today - timedelta(days=31 * 6)
        title = "Six Months Daily Chart"

    elif time_frame == "oneYr":
        user_time_frame = date_today - timedelta(days=365)
        title = "One Year Daily Chart"
    elif time_frame == "threeYr":
        user_time_frame = date_today - timedelta(days=365 * 3)
        title = "Three Year Daily Chart"

    if time_frame == "oneWeek":
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/15/minute/{user_time_frame}/{date_today}?adjusted=true&sort=asc&apiKey={polygon_api_key}"
    else:
        url = f"https://api.polygon.io/v2/aggs/ticker/{ticker}/range/1/day/{user_time_frame}/{date_today}?adjusted=true&sort=asc&apiKey={polygon_api_key}"
    res_j = common_api_call(url)
    if "error" in res_j:
        return "error"
    chart_df = pd.DataFrame(res_j.get("results"))
    chart_df["t"] = pd.to_datetime(chart_df["t"] / 1000, unit="s")
    traces = [
        go.Scatter(
            x=chart_df["t"],
            y=chart_df["c"],
        ),
    ]
    layout = go.Layout(
        title=title,
        dragmode="pan",
        xaxis={"gridcolor": "rgba(255,255,255,0.2)"},
        yaxis={"gridcolor": "rgba(255,255,255,0.2)"},
        plot_bgcolor="#000",
        modebar_add=["drawcircle", "drawrect", "drawline", "eraseshape"],
        hovermode="closest",
    )
    fig = go.Figure(data=traces, layout=layout)
    average_y = chart_df["c"].mean()
    fig.add_hline(y=average_y, line={"color": "#fff", "width": 1, "dash": "dashdot"})
    return pio.to_html(fig, full_html=False)


def competitors_info(competitor_query_obj=None, res_j=None):
    map_dict = {}
    for competitor in competitor_query_obj:
        map_dict[competitor.ticker] = {
            "ticker": competitor.ticker,
            "company_name": competitor.company_name,
            "data": None,
        }

    # #adding data to map_dict
    for data in res_j.get("tickers", []):
        ticker = data.get("ticker", None)
        if ticker == map_dict[ticker]["ticker"]:
            map_dict[ticker]["data"] = data
    return map_dict


def return_reverse_helper(
    request,
    ticker_types,
    query,
):
    ticker_type = query.security_type
    if request.user.is_authenticated:
        if ticker_type in ticker_types:
            return redirect(
                reverse(
                    "search:user_etf_search_result",
                    kwargs={
                        "ticker_id": query.api_call_symbol,
                        "mtype": query.market_type,
                        "ticker_type": ticker_type,
                        "user_id": request.user.username,
                    },
                ),
            )
        return redirect(
            reverse(
                f"search:user_{query.market_type}_search_result",
                kwargs={
                    "ticker_id": query.api_call_symbol,
                    "mtype": query.market_type,
                    "user_id": request.user.username,
                },
            ),
        )
    # NOT SIGNED IN
    if ticker_type in ticker_types:
        return redirect(
            reverse(
                "search:etf_search_result",
                kwargs={
                    "ticker_id": query.api_call_symbol,
                    "mtype": query.market_type,
                    "ticker_type": ticker_type,
                },
            ),
        )
    return redirect(
        reverse(
            f"search:{query.market_type}_search_result",
            kwargs={
                "ticker_id": query.api_call_symbol,
                "mtype": query.market_type,
            },
        ),
    )


def send_to_search_error_page(request):
    if request.user.is_authenticated:
        return redirect(
            reverse(
                "search:user_search",
                kwargs={"status": "error", "user_id": request.user.username},
            ),
        )

    return redirect(reverse("search:search", kwargs={"status": "error"}))
