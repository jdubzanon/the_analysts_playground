from django.urls import path

from . import views

app_name = "stockCenter"

urlpatterns = [
    path("", views.stock_center_view, name="stockCenter_view"),
    path("user=<str:user_id>/", views.stock_center_view, name="user_stockCenter_view"),
]
