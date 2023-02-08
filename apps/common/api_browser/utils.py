from django.conf import settings

from common.jsonrpc.base import BaseJSONRPCConsumer
from common.utils.imports import import_class


def get_menu():
    menu = []
    for re_path, consumer_class_path in settings.WEBSOCKET_ENTRYPOINTS:
        consumer_class = import_class(consumer_class_path)
        assert issubclass(consumer_class, BaseJSONRPCConsumer)
        consumer_menu = []

        for method_name in consumer_class.get_available_action_names():
            consumer_menu.append(consumer_class.get_action(method_name))

        menu.append(
            {
                "consumer": consumer_class,
                "menu_items": consumer_menu,
            }
        )

    return menu
