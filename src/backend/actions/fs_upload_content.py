import base64
import os

from marshmallow import Schema, fields

from backend.config import BASE_DIR_PATH
from backend.jsonrpc.actions import Action
from backend.jsonrpc.exceptions import PathOutsideBaseDirectory


class FsUploadContentRequestSchema(Schema):
    path = fields.String(required=True)
    content = fields.String(required=True)
    base64 = fields.Boolean(required=True)


class FsUploadContent(Action):
    request_schema = FsUploadContentRequestSchema

    async def run(self):
        path = self.request.params["path"]
        absolute_path = os.path.abspath(path)

        if not absolute_path.startswith(BASE_DIR_PATH):
            raise PathOutsideBaseDirectory

        is_base64 = self.request.params["base64"]
        content = self.request.params["content"]

        if is_base64:
            with open(absolute_path, "wb") as file:
                file.write(base64.b64decode(content))
        else:
            with open(absolute_path, "w") as file:
                file.write(content)

        return {}
