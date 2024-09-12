from django.urls import path

from . import views

app_name = "currencies"

urlpatterns = [
    path(
        "switchCurrencies/<str:currency>/",
        views.switch_currencies,
        name="switchCurrencies",
    ),
    path(
        "crypto/<str:letter>/",
        views.view_crypto_currencies,
        name="moreCryptoCurrencies",
    ),
    path(
        "crypto/<str:letter>/user=<int:user_id>/",
        views.view_crypto_currencies,
        name="user_moreCryptoCurrencies",
    ),
    path(
        "forex/<str:letter>/",
        views.view_forex_currencies,
        name="moreForexCurrencies",
    ),
    path(
        "forex/<str:letter>/user=<int:user_id>/",
        views.view_forex_currencies,
        name="user_moreForexCurrencies",
    ),
]
