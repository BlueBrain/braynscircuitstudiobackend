from bcss.main.consumers import CircuitServiceConsumer
from common.jsonrpc.consumer import JSONRPCRequest
from common.serializers.common import HelpResponseSerializer, VersionResponseSerializer
from version import VERSION


@CircuitServiceConsumer.register_method(
    "version",
    allow_anonymous_access=True,
    response_serializer_class=VersionResponseSerializer,
)
async def get_version(request: JSONRPCRequest):
    """Returns current version of the backend."""
    return {
        "version": VERSION,
    }


@CircuitServiceConsumer.register_method(
    "help",
    allow_anonymous_access=True,
    response_serializer_class=HelpResponseSerializer,
)
async def get_available_methods(request: JSONRPCRequest):
    return {
        "available_methods": CircuitServiceConsumer.get_available_method_names(),
    }
