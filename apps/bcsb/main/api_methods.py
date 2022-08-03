import logging

from bcsb.serializers import (
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
    GetUserInfoResponseSerializer,
)
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.utils.serializers import load_via_serializer

logger = logging.getLogger(__name__)


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

    method_name = "list-dir"
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
