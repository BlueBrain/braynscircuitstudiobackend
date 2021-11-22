from django.urls import re_path

from bcsb.consumers import CircuitStudioConsumer


websocket_urlpatterns = [
    re_path(r"ws/$", CircuitStudioConsumer.as_asgi()),
]
