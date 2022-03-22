import logging

from bcsb.auth.auth_service import authenticate_user
from bcsb.consumers import CircuitStudioConsumer
from bcsb.schemas import AuthenticateSchema
from jsonrpc.consumer import JSONRPCRequest
from utils.schemas import load_schema
from version import VERSION

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method("version", allow_anonymous_access=True)
async def get_version(*_):
    return {
        "version": VERSION,
    }


@CircuitStudioConsumer.register_method("help", allow_anonymous_access=True)
async def get_available_methods(*_):
    return {
        "available_methods": CircuitStudioConsumer.get_available_methods(),
    }


@CircuitStudioConsumer.register_method("authenticate", allow_anonymous_access=True)
async def authenticate(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    schema = load_schema(AuthenticateSchema, request.params)
    user = await authenticate_user(schema["token"], consumer.scope)
    return {
        "user": user,
    }
