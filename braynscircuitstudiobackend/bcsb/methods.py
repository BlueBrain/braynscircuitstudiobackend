import logging

from bcsb.consumers import CircuitStudioConsumer
from jsonrpc.consumer import JSONRPCRequest
from version import VERSION

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method("version")
async def get_version(request: JSONRPCRequest):
    return {
        "version": VERSION,
    }


@CircuitStudioConsumer.register_method("help")
async def get_available_methods(request: JSONRPCRequest):
    return {
        "available_methods": CircuitStudioConsumer.get_available_methods(),
    }
