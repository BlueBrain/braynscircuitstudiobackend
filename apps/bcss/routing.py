from django.urls import re_path

from bcss.main.consumers import CircuitServiceConsumer

websocket_urlpatterns = [
    re_path(r"ws/$", CircuitServiceConsumer.as_asgi()),
]
