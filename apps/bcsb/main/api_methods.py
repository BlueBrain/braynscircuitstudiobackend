import logging

from bcsb.serializers import (
    ListGPFSDirectoryRequestSerializer,
    ListGPFSDirectoryResponseSerializer,
    GetUserInfoResponseSerializer,
)
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.utils.serializers import load_via_serializer

logger = logging.getLogger(__name__)


class GetUserInfoMethod(JSONRPCMethod):
    allow_anonymous_access = True
    response_serializer_class = GetUserInfoResponseSerializer

    async def run(self):
        return {
            "user": self.request.user,
        }


class ListGPFSDirectory(JSONRPCMethod):
    """
    Provides list of files and directories in a given path.
    """

    custom_method_name = "get-directory-contents"
    request_serializer_class = ListGPFSDirectoryRequestSerializer
    response_serializer_class = ListGPFSDirectoryResponseSerializer

    @staticmethod
    def filter_requested_path(value: str) -> str:
        new_value = value
        if new_value.startswith("/gpfs/bbp.cscs.ch"):
            new_value = new_value[17:]
        return new_value

    async def run(self):
        request_data = load_via_serializer(
            self.request.params or {}, ListGPFSDirectoryRequestSerializer
        )
        unicore_service = UnicoreService(token=self.request.token)
        request_path = self.filter_requested_path(request_data["path"])
        logger.debug(f"{request_path=}")
        storage_response = await unicore_service.list_gpfs_storage(request_path)

        directories = []
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
                "group": content["group"],
            }
            if content["is_directory"]:
                directories.append(item_data)
            else:
                files.append(item_data)

        return {
            "path": request_path,
            "directories": directories,
            "files": files,
        }
