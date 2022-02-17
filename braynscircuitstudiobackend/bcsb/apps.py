from django import apps


class BraynCircuitStudioBackendConfig(apps.AppConfig):
    name = "bcsb"

    def ready(self):
        from bcsb import methods  # noqa
