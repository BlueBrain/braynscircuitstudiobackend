from django.contrib import admin

urlpatterns = [
    # path("docs/", include("bcss.api_browser.urls", namespace="api-browser")),
    # path("admin/", admin.site.urls),
]

admin.site.site_header = "Brayns Circuit Studio Service"
admin.site.site_title = "BCSS"
admin.site.index_title = "Brayns Circuit Studio Service"
