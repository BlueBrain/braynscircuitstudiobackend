from dataclasses import dataclass

from marshmallow import Schema, fields
import os
from backend.jsonrpc.actions import Action


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

        filesystem_object = FilesystemObject()

        if os.path.isdir(absolute_path):
            filesystem_object.type = "directory"
        if os.path.isfile(absolute_path):
            filesystem_object.type = "file"

        return filesystem_object
