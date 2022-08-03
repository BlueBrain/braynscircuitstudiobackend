from django import apps


class MainConfig(apps.AppConfig):
    name = "bcsb.main"

    def ready(self):
        self.load_consumer_methods()

    @staticmethod
    def load_consumer_methods():
        from .consumers import CircuitStudioConsumer

        CircuitStudioConsumer.autodiscover_methods()
