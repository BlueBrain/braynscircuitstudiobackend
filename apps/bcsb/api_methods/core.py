import logging
from typing import Union

from django.contrib.auth.models import AnonymousUser, User

from bcsb.consumers import CircuitStudioConsumer
from bcsb.serializers import (
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
    GetUserInfoResponseSerializer,
    JobQueueResponseSerializer,
)
from bcsb.unicore.unicore_service import UnicoreService
from common.auth.auth_service import authenticate_user
from common.auth.serializers import AuthenticateRequestSerializer, AuthenticateResponseSerializer
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.methods import JSONRPCMethod
from common.serializers.common import (
    VersionResponseSerializer,
    HelpResponseSerializer,
)
from common.utils.serializers import load_via_serializer
from version import VERSION

logger = logging.getLogger(__name__)


class VersionMethod(JSONRPCMethod):
    """
    Returns current version of the backend.
    """

    allow_anonymous_access = True
    response_serializer_class = VersionResponseSerializer

    async def run(self, request: JSONRPCRequest):
        return {
            "version": VERSION,
        }


class HelpMethod(JSONRPCMethod):
    allow_anonymous_access = True
    response_serializer_class = HelpResponseSerializer

    async def run(self, request: JSONRPCRequest):
        return {
            "available_methods": CircuitStudioConsumer.get_available_method_names(),
        }


class AuthenticateMethod(JSONRPCMethod):
    """
    Logs a user in. You can also provide an access token while connecting to the backend.
    Use HTTP "Authorization" header with "Bearer <TOKEN>" as a value.
    """

    allow_anonymous_access = True
    request_serializer_class = AuthenticateRequestSerializer
    response_serializer_class = AuthenticateResponseSerializer

    async def run(self, request: JSONRPCRequest):
        user: Union[User, AnonymousUser] = await authenticate_user(
            request.params["token"],
            request.scope,
        )

        return {
            "user": user,
        }


class GetUserInfoMethod(JSONRPCMethod):
    allow_anonymous_access = True
    response_serializer_class = GetUserInfoResponseSerializer

    async def run(self, request: JSONRPCRequest):
        return {
            "user": request.user,
        }


class ListGPFSDirectory(JSONRPCMethod):
    """
    Provides list of files and directories in a given path.
    """

    name = "list-dir"
    request_serializer_class = ListGPFSDirectoryRequestSerializer
    response_serializer_class = ListGPFSDirectoryResponseSerializer

    async def run(self, request: JSONRPCRequest):
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


class GetJobQueueMethod(JSONRPCMethod):
    """
    Returns requests that are currently being processed (jobs).

    Every JSONRPC request to the consumer is processed in a separate thread. These threads are kept record of
    in form of a "job queue". This way we can check whether the server is currently busy i.e.
    processing heavier and or longer tasks.
    """

    allow_anonymous_access = True
    response_serializer_class = JobQueueResponseSerializer

    async def run(self, request: JSONRPCRequest):
        jobs = request.consumer.job_queue
        job_count = len(jobs)

        return {
            "job_count": job_count,
            "job_queue": request.consumer.job_queue,
        }
