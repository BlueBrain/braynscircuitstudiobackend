import logging
from importlib import import_module

from django import apps
from django.conf import settings

logger = logging.getLogger(__name__)


class MainConfig(apps.AppConfig):
    name = "bcss.main"

    def ready(self):
        self.load_consumer_methods()

    def load_consumer_methods(self):
        for app in apps.apps.get_app_configs():
            package_name = f"{app.module.__package__}.{settings.API_METHODS_PACKAGE_NAME}"
            try:
                methods_module = import_module(package_name)
                logger.debug(f"Loaded consumer methods module: {methods_module.__package__}")
            except ImportError:
                pass
