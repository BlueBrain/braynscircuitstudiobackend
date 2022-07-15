import logging
from importlib import import_module

from django import apps
from django.conf import settings


logger = logging.getLogger(__name__)


class BraynCircuitStudioBackendConfig(apps.AppConfig):
    name = "bcsb"

    def ready(self):
        from bcsb import api_methods  # noqa

        self.load_consumer_methods()

    def load_consumer_methods(self):
        for app in apps.apps.get_app_configs():
            package_name = f"{app.module.__package__}.{settings.API_METHODS_PACKAGE_NAME}"
            try:
                methods_module = import_module(package_name)
                logger.debug(f"Loaded consumer methods module: {methods_module.__package__}")
            except ImportError:
                pass

        # List all registered methods at the time the app started
        from bcsb.consumers import CircuitStudioConsumer

        registered_methods = []
        for method_name in CircuitStudioConsumer.get_available_method_names():
            registered_methods.append(method_name)
        registered_methods.sort()
        logger.info(
            f"Registered methods:\n"
            + "\n".join([f"{i+1}. {name}" for i, name in enumerate(registered_methods)])
        )
