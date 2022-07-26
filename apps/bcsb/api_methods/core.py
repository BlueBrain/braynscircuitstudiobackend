import logging
from typing import Union

from django.contrib.auth.models import AnonymousUser, User

from common.auth.auth_service import authenticate_user
from bcsb.consumers import CircuitStudioConsumer
from bcsb.serializers import (
    AuthenticateResponseSerializer,
    AuthenticateRequestSerializer,
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
    GetUserInfoResponseSerializer,
)
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.consumer import JSONRPCRequest
from common.serializers.common import (
    VersionResponseSerializer,
    HelpResponseSerializer,
)
from common.utils.serializers import load_via_serializer
from version import VERSION

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method(
    "version",
    allow_anonymous_access=True,
    response_serializer_class=VersionResponseSerializer,
)
async def get_version(*_):
    """Returns current version of the backend."""
    return {
        "version": VERSION,
    }


@CircuitStudioConsumer.register_method(
    "help",
    allow_anonymous_access=True,
    response_serializer_class=HelpResponseSerializer,
)
async def get_available_methods(*_):
    return {
        "available_methods": CircuitStudioConsumer.get_available_method_names(),
    }


@CircuitStudioConsumer.register_method(
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
        "is_authenticated": user.is_authenticated,
    }


@CircuitStudioConsumer.register_method(
    allow_anonymous_access=True,
    response_serializer_class=GetUserInfoResponseSerializer,
)
async def get_user_info(request: JSONRPCRequest):
    user = None
    is_authenticated = request.user.is_authenticated
    if is_authenticated:
        user = request.user

    return {
        "user": user,
        "is_authenticated": is_authenticated,
    }


@CircuitStudioConsumer.register_method(
    "list-dir",
    request_serializer_class=ListGPFSDirectoryRequestSerializer,
    response_serializer_class=ListGPFSDirectoryResponseSerializer,
)
async def list_gpfs_directory(request: JSONRPCRequest):
    """
    Provides list of files and directories in a given path.
    """
    request_data = load_via_serializer(request.params or {}, ListGPFSDirectoryRequestSerializer)
    unicore_service = UnicoreService(token=request.token)
    storage_response = await unicore_service.list_gpfs_storage(request_data["path"])

    dirs = []
    files = []

    for child_name in storage_response["children"]:
        content = storage_response["content"][child_name]

        name = child_name
        if name.endswith("/"):
            name = name[:-1]
        name = name.split("/")[-1]

        item_data = {
            "name": name,
            "owner": content["owner"],
            "size": content["size"],
            "last_accessed": content["last_accessed"],
        }
        if content["is_directory"]:
            dirs.append(item_data)
        else:
            files.append(item_data)

    return {
        "dirs": dirs,
        "files": files,
    }
