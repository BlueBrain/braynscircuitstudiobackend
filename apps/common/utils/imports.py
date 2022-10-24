from importlib import import_module
from typing import Type, Any


def import_class(class_path: str) -> Type[Any]:
    class_path_parts = class_path.split(".")
    module_path = ".".join(class_path_parts[:-1])
    module = import_module(module_path)
    return getattr(module, class_path_parts[-1])
