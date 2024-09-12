from django.urls import path

from . import views

app_name = "commentSection"

urlpatterns = [
    path("", views.comments_view, name="commentsView"),
]
