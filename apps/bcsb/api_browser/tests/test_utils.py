from types import FunctionType
from typing import Type

from bcsb.api_browser.utils import get_menu_items
from bcsb.main.consumers import CircuitStudioConsumer
from bcsb.serializers import (
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.serializers.common import HelpResponseSerializer


def test_get_menu():
    menu_items = get_menu_items()
    assert isinstance(menu_items, list)
    assert len(menu_items) > 0, "There must be at least one method registered"
    assert issubclass(menu_items[0], JSONRPCMethod)


def test_inspect_method_function():
    version_method_class: Type[JSONRPCMethod] = CircuitStudioConsumer.get_method("version")
    assert issubclass(version_method_class, JSONRPCMethod)
    version_method = version_method_class()
    assert version_method.name == "version"
    assert isinstance(version_method_class.run, FunctionType)
    assert version_method.docstring == "Returns current version of the backend."

    list_dir_method = CircuitStudioConsumer.get_method("list-dir")
    assert list_dir_method.request_serializer_class == ListGPFSDirectoryRequestSerializer
    assert list_dir_method.response_serializer_class == ListGPFSDirectoryResponseSerializer

    help_method = CircuitStudioConsumer.get_method("help")
    assert help_method.response_serializer_class == HelpResponseSerializer
