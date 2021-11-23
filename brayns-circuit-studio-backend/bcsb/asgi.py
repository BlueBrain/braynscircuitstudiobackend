import os

from bcsb import routing
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bcsb.settings")

application_mapping = {
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns)),
}

application = ProtocolTypeRouter(application_mapping)
