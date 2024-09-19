from django.urls import path

from . import views

app_name = "dashboard_app"

urlpatterns = [
    path(
        "",
        views.dashboard_dispatch_for_redirect,
        name="dashboardDispatchForRedirect",
    ),
    path("user=<str:user_id>/", views.dashboard_view, name="dashboard_view"),
    path("htmxReload/", views.htmx_reload, name="htmxReload"),
    path("swapping/", views.htmx_swap_function, name="_htmxSwapfunction"),
    path(
        "multipe_watchlist_match/<str:ticker_id>/<str:mtype>/",
        views.multipe_watchlist_match,
        name="multipe_watchlist_match",
    ),
    path(
        "deleting/<str:ticker_id>/<str:mtype>/",
        views.htmx_swap_delete,
        name="_htmxSwapDelete",
    ),
    path("portfolioSwapping/", views.htmx_portfolio_swap, name="_htmxPortfolioSwap"),
    path("portfolioEditting/", views.htmx_edit_portfolio, name="_htmxEditPortfolio"),
    path(
        "PortfolioDeleting/<str:ticker_id>/<str:mtype>/",
        views.htmx_portfolio_item_delete,
        name="_htmxPortfolioItemDelete",
    ),
]
