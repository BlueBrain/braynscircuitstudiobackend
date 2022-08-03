import logging

from django import apps

logger = logging.getLogger(__name__)


class MainConfig(apps.AppConfig):
    name = "bcss.main"

    def ready(self):
        self.load_consumer_methods()

    @staticmethod
    def load_consumer_methods():
        from .consumers import CircuitServiceConsumer

        CircuitServiceConsumer.autodiscover_methods()
