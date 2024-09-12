from django.urls import path

from . import views

app_name = "search"
urlpatterns = [
    path(
        "htmxChartSwitch/<str:time_frame>/<str:ticker>/",
        views.htmx_chart_switch,
        name="_htmxChartSwitch",
    ),
    path(
        "_htxmAddRemoveWatchlist/<str:ticker_id>/<str:mtype>/",
        views.add_remove_watchlist,
        name="_addRemoveWatchlist",
    ),
    path(
        "_htmxCompetitors/<str:ticker_id>/",
        views.htmx_competitors,
        name="_htmxCompetitors",
    ),
    path(
        "_htmxCompanySwap/<str:ticker_id>",
        views.htmx_company_swap,
        name="_htmxCompanySwap",
    ),
    path("_htmxGet/", views.htmx_get, name="_htmxGet"),
    path(
        "_htmxGet/htmxLinkClick/<ticker_id>",
        views.dispatcher,
        name="search__redirect",
    ),  # <--- CLICK THE HTMX POPUP FOR SEARCH MATCHES LINKS ACROSS WHOLE WEBSITE
    path(
        "htmxLink/type=<str:htmxTickerType>/<str:ticker_id>/",
        views.dispatcher,
        name="htmx_dispatcher",
    ),
    path("getFinancials/<str:ticker_id>/", views.get_financials, name="getFinancials"),
    path("search+dispatch/", views.dispatcher, name="dispatch"),
    path("search+dispatch/<int:user_id>/", views.dispatcher, name="user_dispatch"),
    path(
        "search+dispatch/<str:ticker_id>/<str:mtype>/",
        views.dispatcher,
        name="recursive_dispatch",
    ),
    # I BADLY NAMED THIS BUT IM NOT CHANGING EVERYTHING
    #  THIS IS THE DEFAULT LINK CLICK ADDRESS
    path(
        "search+dispatch/<str:ticker_id>/<str:mtype>/",
        views.dispatcher,
        name="htmxLinkDispatch",
    ),
    # COMMON STOCK
    path(
        "result=CS/<str:ticker_id>/<str:mtype>/",
        views.common_search_result,
        name="stocks_search_result",
    ),
    path(
        "result=CS/<str:ticker_id>/<str:mtype>/user=<int:user_id>/",
        views.common_search_result,
        name="user_stocks_search_result",
    ),
    # CRYPTO
    path(
        "result=crypto/<str:ticker_id>/<str:mtype>/",
        views.crypto_search_result,
        name="crypto_search_result",
    ),
    path(
        "result=crypto/<str:ticker_id>/<str:mtype>/<int:user_id>/",
        views.crypto_search_result,
        name="user_crypto_search_result",
    ),
    # FOREX
    path(
        "results=forex/<str:ticker_id>/<str:mtype>/",
        views.forex_search_result,
        name="fx_search_result",
    ),
    path(
        "results=forex/<str:ticker_id>/<str:mtype>/<int:user_id>/",
        views.forex_search_result,
        name="user_fx_search_result",
    ),
    # INDICES
    path(
        "results=index/<str:ticker_id>/<str:mtype>/",
        views.indices_search_result,
        name="indices_search_result",
    ),
    path(
        "results=index/<str:ticker_id>/<str:mtype>/user=<int:user_id>/",
        views.indices_search_result,
        name="user_indices_search_result",
    ),
    #    ETF
    path(
        "result=other/<str:ticker_id>/<str:mtype>/<str:ticker_type>/",
        views.etf_search_result,
        name="etf_search_result",
    ),
    path(
        "result=other/<str:ticker_id>/<str:mtype>/<str:ticker_type>/user=<int:user_id>/",
        views.etf_search_result,
        name="user_etf_search_result",
    ),
    path("<str:status>/user=<int:user_id>/", views.search, name="user_search"),
    path("<str:status>/", views.search, name="search"),
]
