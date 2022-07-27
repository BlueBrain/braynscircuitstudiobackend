from typing import Union

from django.contrib.auth.models import User, AnonymousUser

from bcss.main.consumers import CircuitServiceConsumer
from common.auth.auth_service import authenticate_user
from common.auth.serializers import AuthenticateRequestSerializer, AuthenticateResponseSerializer
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


@CircuitServiceConsumer.register_method(
    "authenticate",
    allow_anonymous_access=True,
    request_serializer_class=AuthenticateRequestSerializer,
    response_serializer_class=AuthenticateResponseSerializer,
)
async def authenticate(request: JSONRPCRequest):
    """
    Logs a user in. You can also provide an access token while connecting to the backend.
    Use HTTP "Authorization" header with "Bearer <TOKEN>" as a value.
    """
    user: Union[User, AnonymousUser] = await authenticate_user(
        request.params["token"],
        request.scope,
    )

    return {
        "user": user,
    }
