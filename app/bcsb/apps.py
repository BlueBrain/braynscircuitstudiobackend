from django import apps


class BraynCircuitStudioBackendConfig(apps.AppConfig):
    name = "bcsb"

    def ready(self):
        # noinspection PyUnresolvedReferences
        from . import methods
