from django.urls import path

from . import views

app_name = "dbloader"

urlpatterns = [
    path("", views.dbloader_view, name="dbloader_view"),
    path("load_forex/", views.dbloader_forex_view, name="dbloader_forex_view"),
    path("load_stocks/", views.dbloader_stocks_view, name="dbloader_stocks_view"),
    path("load_index/", views.dbloader_index_view, name="dbloader_index_view"),
    path("load_crypto/", views.dbloader_crypto_view, name="dbloader_crypto_view"),
]
