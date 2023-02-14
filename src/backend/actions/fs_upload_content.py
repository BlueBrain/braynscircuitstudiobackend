import base64
import os

from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action


class FsUploadContentRequestSchema(Schema):
    path = fields.String(required=True)
    content = fields.String(required=True)
    base64 = fields.Boolean(required=True)


class FsUploadContent(Action):
    request_schema = FsUploadContentRequestSchema

    async def run(self):
        path = self.request.params["path"]
        path = os.path.abspath(path)
        is_base64 = self.request.params["base64"]
        content = self.request.params["content"]
        if is_base64:
            with open(path, "wb") as file:
                file.write(base64.b64decode(content))
        else:
            with open(path, "w") as file:
                file.write(content)
        return {}
