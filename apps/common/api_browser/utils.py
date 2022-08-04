from django.conf import settings

from common.utils.imports import import_class


def get_menu():
    menu = []
    for re_path, consumer_class_path in settings.WEBSOCKET_ENTRYPOINTS:
        consumer_class = import_class(consumer_class_path)
        consumer_menu = []

        for method_name in sorted(consumer_class.get_available_method_names()):
            consumer_menu.append(consumer_class.get_method(method_name))

        menu.append(
            {
                "consumer": consumer_class,
                "menu_items": consumer_menu,
            }
        )

    return menu
