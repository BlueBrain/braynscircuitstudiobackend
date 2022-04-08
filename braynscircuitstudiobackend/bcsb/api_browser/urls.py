from django.urls import path, re_path

from bcsb.api_browser import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    re_path(r"^method/(?P<method_name>[a-z\-]+)/", views.MethodView.as_view(), name="method"),
]

app_name = "api_browser"
