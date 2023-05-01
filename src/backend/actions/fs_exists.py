import logging
import os
from dataclasses import dataclass

from marshmallow import Schema, fields

from backend.config import BASE_DIR_PATH
from backend.filesystem.utils import get_safe_absolute_dir_path
from backend.jsonrpc.actions import Action
from backend.jsonrpc.exceptions import PathOutsideBaseDirectory

logger = logging.getLogger(__name__)


class FsExistsRequestSchema(Schema):
    path = fields.String(required=True)


class FsExistsResponseSchema(Schema):
    exists = fields.Boolean()
    type = fields.String(
        required=False,
        allow_none=True,
    )


@dataclass
class FilesystemObject:
    type: str = None

    @property
    def exists(self) -> bool:
        return self.type is not None


def check_filesystem_object(path: str) -> FilesystemObject:
    filesystem_object = FilesystemObject()

    if os.path.isdir(path):
        filesystem_object.type = "directory"
    if os.path.isfile(path):
        filesystem_object.type = "file"

    return filesystem_object


class FsExists(Action):
    request_schema = FsExistsRequestSchema
    response_schema = FsExistsResponseSchema

    async def run(self):
        absolute_path = get_safe_absolute_dir_path(self.request.params["path"])

        logger.debug(f"{BASE_DIR_PATH=}")
        logger.debug(f"{absolute_path=}")

        if not absolute_path.startswith(BASE_DIR_PATH):
            raise PathOutsideBaseDirectory

        filesystem_object = check_filesystem_object(absolute_path)

        # Try with a file
        if not filesystem_object.exists:
            path_without_slash = absolute_path.rstrip("/")
            logger.debug(f"{path_without_slash=}")
            filesystem_object = check_filesystem_object(path_without_slash)

        return filesystem_object
