import logging

from django import apps

logger = logging.getLogger(__name__)


class BraynsCircuitStudioBackendConfig(apps.AppConfig):
    name = "bcsb"
