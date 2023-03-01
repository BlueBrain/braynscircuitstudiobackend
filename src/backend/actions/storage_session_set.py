from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action


class StorageSessionSetRequestSchema(Schema):
    key = fields.String(required=True)
    value = fields.Raw(required=True)


class StorageSessionSet(Action):
    request_schema = StorageSessionSetRequestSchema

    async def run(self):
        self.request.ws_handler.storage_service.set(
            self.request.params["key"],
            self.request.params["value"],
        )
        return {"ok": True}
