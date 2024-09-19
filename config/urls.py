# ruff: noqa
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include
from django.urls import path
from django.views import defaults as default_views
from django.views.generic import TemplateView

urlpatterns = [
    # path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    # path(
    #     "about/",
    #     TemplateView.as_view(template_name="pages/about.html"),
    #     name="about",
    # ),
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    # User management
    path("users/", include("theanalystsplayground.users.urls", namespace="users")),
    path("accounts/", include("allauth.urls")),
    # Your stuff: custom urls includes go here
    path("", include("theanalystsplayground.HomePage.urls")),
    path("Search/", include("theanalystsplayground.Search.urls", namespace="Search")),
    path("StockCenter/", include("theanalystsplayground.StockCenter.urls")),
    path("newsCenter/", include("theanalystsplayground.newsCenter.urls")),
    path("dashboard/", include("theanalystsplayground.dashboard.urls")),
    path("comments/", include("theanalystsplayground.commentSection.urls")),
    path("currencies/", include("theanalystsplayground.currencies.urls")),
    path("indexSearch/", include("theanalystsplayground.indexSearch.urls")),
    path("dbloader/", include("theanalystsplayground.dbloader.urls")),
    # Media files
    *static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT),
]
if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()


if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
