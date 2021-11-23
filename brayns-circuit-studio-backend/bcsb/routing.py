from bcsb.consumers import CircuitStudioConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r"ws/$", CircuitStudioConsumer.as_asgi()),
]
