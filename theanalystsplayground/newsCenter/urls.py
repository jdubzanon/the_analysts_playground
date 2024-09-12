from django.urls import path

from . import views

app_name = "newsCenter"

urlpatterns = [
    path("", views.newscenter_view, name="newsCenter_view"),
    path(
        "news_form_response/",
        views.newscenter_form_handler,
        name="newscenter_form_handler",
    ),
    path("user=<int:user_id>/", views.newscenter_view, name="user_newsCenter_view"),
    path(
        "<str:receiving_string>/<int:index_low>/<int:index_high>/<str:page_request>/<str:mtype>/",
        views.htmx_swap,
        name="_htmxSwap",
    ),
]
