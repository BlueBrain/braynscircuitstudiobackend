import os

from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

asgi_app = get_asgi_application()

from common.auth.middleware import KeyCloakAuthASGIMiddleware  # noqa
from bcsb import routing  # noqa

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bcsb.settings")

application_mapping = {
    "http": asgi_app,
    "websocket": KeyCloakAuthASGIMiddleware(
        URLRouter(routing.websocket_urlpatterns),
    ),
}

application = ProtocolTypeRouter(application_mapping)
