from django.urls import path

from . import views

app_name = "indexSearch"

urlpatterns = [
    path("", views.index_search_view, name="indexSearch_view"),
    path("user=<str:user_id>", views.index_search_view, name="user_indexSearch_view"),
    path(
        "htmxRelatedIndices/<str:company_name>/<str:page_requested>/<int:index_low>/<int:index_high>/",
        views.related_indices,
        name="htmxRelatedIndices",
    ),
    path(
        "htmxAdditional/<str:page_requested>/<str:search_string>/<int:index_high>/<int:index_low>/",
        views.index_search,
        name="indexSearch",
    ),
    path(
        "htmxRelatedEtf/<str:company_name>/<str:page_requested>/<int:index_high>/<int:index_low>/<str:ticker_type>/",
        views.related_etf,
        name="htmxRelatedEtf",
    ),
    path("view-all-indices/", views.view_all_indices, name="viewAllIndices"),
    path(
        "view-all-indices/user=<str:user_id>",
        views.view_all_indices,
        name="user_viewAllIndices",
    ),
    path(
        "htmxIndexCategoryLinkClick/<str:name>/<int:index_low>/<int:index_high>/<str:page_requested>/",
        views.htmx_index_category_link_click,
        name="htmxIndexCategoryLinkClick",
    ),
    path(
        "htmxCategoryPagination/<str:name>/<int:index_low>/<int:index_high>/<str:page_requested>/",
        views.htmx_category_pagination,
        name="htmxCategoryPagination",
    ),
]
