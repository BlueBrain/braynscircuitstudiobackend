from django.urls import path

from common.api_browser import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
]

app_name = "api_browser"
