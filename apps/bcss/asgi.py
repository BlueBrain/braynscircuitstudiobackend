import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

asgi_app = get_asgi_application()

from common.auth.middleware import KeyCloakAuthMiddleware
from bcss import routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bcss.settings")

application_mapping = {
    "http": asgi_app,
    "websocket": KeyCloakAuthMiddleware(
        URLRouter(routing.websocket_urlpatterns),
    ),
}

application = ProtocolTypeRouter(application_mapping)
