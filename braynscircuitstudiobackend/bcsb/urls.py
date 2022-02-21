from django.contrib import admin
from django.urls import path

urlpatterns = [
    path("admin/", admin.site.urls),
]

admin.site.site_header = "Brayns Circuit Studio Backend"
admin.site.site_title = "BCSB"
admin.site.index_title = "Brayns Circuit Studio Backend"
