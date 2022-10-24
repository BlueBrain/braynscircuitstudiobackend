from django.contrib import admin

from django.urls import path, include

urlpatterns = [
    path("docs/", include("common.api_browser.urls", namespace="api-browser")),
    path("admin/", admin.site.urls),
]

admin.site.site_header = "Brayns Circuit Studio Service"
admin.site.site_title = "BCSS"
admin.site.index_title = "Brayns Circuit Studio Service"
