from django import apps


class MainConfig(apps.AppConfig):
    name = "bcsb.main"

    def ready(self):
        self.load_consumer_methods()

    @staticmethod
    def load_consumer_methods():
        from .consumers import CircuitStudioConsumer

        # Currently, the loaded consumers are "greedy". It means, they register (autodiscover) all methods they
        # encounter in the registered apps. If you plan to add more than one consumer in the app, you'll need to:
        # - update settings.WEBSOCKET_ENTRYPOINTS list
        # - somehow divide the methods (classes inheriting from JSONRPCMethod) between the consumers so that they
        #   don't take over all methods available
        CircuitStudioConsumer.autodiscover_methods()
