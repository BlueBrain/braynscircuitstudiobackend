from bcsb.main.consumers import CircuitStudioConsumer


def get_menu_items():
    consumer = CircuitStudioConsumer
    menu_list = []

    for method_name in sorted(consumer.get_available_method_names()):
        menu_list.append(consumer.get_method(method_name))

    return menu_list
