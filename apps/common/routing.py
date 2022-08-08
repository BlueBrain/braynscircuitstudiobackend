import logging
from typing import Iterable

from django.urls import re_path

from common.jsonrpc.base import BaseJSONRPCConsumer
from common.utils.imports import import_class

logger = logging.getLogger(__name__)


def prepare_websocket_routing_configuration(entrypoints: Iterable):
    config = []

    for path_regex, class_path in entrypoints:
        consumer_class = import_class(class_path)
        assert issubclass(consumer_class, BaseJSONRPCConsumer)
        config.append(
            re_path(path_regex, consumer_class.as_asgi()),
        )
        logger.debug(f"Registered entrypoint at: {path_regex} for {consumer_class}")

    return config
