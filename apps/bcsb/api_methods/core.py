import logging

from common.auth.auth_service import authenticate_user
from bcsb.consumers import CircuitStudioConsumer
from bcsb.schemas import (
    AuthenticateRequestSchema,
    ListGPFSDirectoryRequestSchema,
    ListGPFSDirectoryResponseSchema,
    AuthenticateResponseSchema,
)
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.consumer import JSONRPCRequest
from common.schemas.common import VersionResponseSchema, HelpResponseSchema
from common.utils.schemas import load_schema, dump_schema
from version import VERSION

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method(
    "version",
    allow_anonymous_access=True,
    response_schema=VersionResponseSchema,
)
async def get_version(*_):
    """Returns current version of the backend."""
    return {
        "version": VERSION,
    }


@CircuitStudioConsumer.register_method(
    "help",
    allow_anonymous_access=True,
    response_schema=HelpResponseSchema,
)
async def get_available_methods(*_):
    return {
        "available_methods": CircuitStudioConsumer.get_available_method_names(),
    }


@CircuitStudioConsumer.register_method(
    "authenticate",
    allow_anonymous_access=True,
    request_schema=AuthenticateRequestSchema,
    response_schema=AuthenticateResponseSchema,
)
async def authenticate(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    """
    Logs a user in. You can also provide an access token while connecting to the backend.
    Use HTTP "Authorization" header with "Bearer <TOKEN>" as a value.
    """
    schema = load_schema(AuthenticateRequestSchema, request.params)
    user = await authenticate_user(schema["token"], consumer.scope)
    return {
        "user": user,
    }


@CircuitStudioConsumer.register_method(
    "list-dir",
    request_schema=ListGPFSDirectoryRequestSchema,
    response_schema=ListGPFSDirectoryResponseSchema,
)
async def list_gpfs_directory(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    """
    Provides list of files and directories in a given path.
    """
    schema = load_schema(ListGPFSDirectoryRequestSchema, request.params or {})
    unicore_service = UnicoreService(token=request.token)
    storage_response = await unicore_service.list_gpfs_storage(schema["path"])

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

    response_data = {
        "dirs": dirs,
        "files": files,
    }
    response = dump_schema(
        ListGPFSDirectoryResponseSchema,
        response_data,
    )

    return response
