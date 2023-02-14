from marshmallow import Schema, fields
import os
from backend.jsonrpc.actions import Action


class FsExistsRequestSchema(Schema):
    path = fields.String(required=True)


class FsExists(Action):
    request_schema = FsExistsRequestSchema

    async def run(self):
        path = self.request.params["path"]
        absolute_path = os.path.abspath(path)

        if os.path.isdir(absolute_path):
            return {"type": "directory"}
        if os.path.isfile(absolute_path):
            return {"type": "file"}
        return {"type": "none"}
