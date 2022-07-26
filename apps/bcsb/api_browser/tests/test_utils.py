from types import FunctionType

from bcsb.api_browser.utils import get_menu_items
from bcsb.consumers import CircuitStudioConsumer
from bcsb.serializers import (
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
)
from common.jsonrpc.methods import Method
from common.serializers.common import HelpResponseSerializer


def test_get_menu():
    menu_items = get_menu_items()
    assert isinstance(menu_items, list)
    assert len(menu_items) > 0, "There must be at least one method registered"
    assert isinstance(menu_items[0], Method)


def test_inspect_method_function():
    version_method = CircuitStudioConsumer.get_method("version")
    assert version_method.name == "version"
    assert isinstance(version_method.handler, FunctionType)
    assert version_method.docstring == "Returns current version of the backend."

    list_dir_method = CircuitStudioConsumer.get_method("list-dir")
    assert list_dir_method.request_serializer_class == ListGPFSDirectoryRequestSerializer
    assert list_dir_method.response_serializer_class == ListGPFSDirectoryResponseSerializer

    help_method = CircuitStudioConsumer.get_method("help")
    assert help_method.response_serializer_class == HelpResponseSerializer
