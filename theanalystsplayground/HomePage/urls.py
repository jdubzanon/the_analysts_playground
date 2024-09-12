from django.urls import path

from . import views

app_name = "HomePage"
urlpatterns = [
    path("", views.front_page, name="front-page"),
    path("aboutMe/", views.about_me_view, name="aboutMeView"),
    path("dipatcher/", views.dispatcher, name="dispatcher-view"),
    path(
        "dispatcher/user=<int:user_id>",
        views.dispatcher,
        name="user-dispatcher-view",
    ),
    path("home/", views.home_view, name="home-view"),
    path("home/user=<int:user_id>", views.home_view, name="user-home-view"),
    path("view-all/<str:value>", views.view_all_view, name="viewAll-view"),
    path(
        "htmxSwapChanges/<str:ticker>/<str:mtype>/<str:current_type>/",
        views.htmx_swap_changes,
        name="htmxSwapChanges",
    ),
]
