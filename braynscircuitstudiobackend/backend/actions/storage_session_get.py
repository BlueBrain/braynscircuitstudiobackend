from marshmallow import Schema, fields

from braynscircuitstudiobackend.backend.jsonrpc.actions import Action


class StorageSessionGetRequestSchema(Schema):
    key = fields.String(required=True)


class StorageSessionGetResponseSchema(Schema):
    value = fields.Raw(required=True)


class StorageSessionGet(Action):
    request_schema = StorageSessionGetRequestSchema
    response_schema = StorageSessionGetResponseSchema

    async def run(self):
        value = self.request.ws_handler.storage_service.get(self.request.params["key"])
        return {
            "value": value,
        }
