import logging
import os
from dataclasses import dataclass

from marshmallow import Schema, fields

from backend.config import BASE_DIR_PATH
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


class FsExists(Action):
    request_schema = FsExistsRequestSchema
    response_schema = FsExistsResponseSchema

    async def run(self):
        path = self.request.params["path"]
        absolute_path = os.path.abspath(path)

        logger.debug(f"{BASE_DIR_PATH=}")
        logger.debug(f"{path=}")
        logger.debug(f"{absolute_path=}")

        if not absolute_path.startswith(BASE_DIR_PATH):
            raise PathOutsideBaseDirectory

        filesystem_object = FilesystemObject()

        if os.path.isdir(absolute_path):
            filesystem_object.type = "directory"
        if os.path.isfile(absolute_path):
            filesystem_object.type = "file"

        return filesystem_object
