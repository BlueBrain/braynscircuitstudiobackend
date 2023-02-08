from backend.jsonrpc.actions import Action

from marshmallow import Schema, fields

from backend.jsonrpc.jsonrpc_request import JSONRPCRequest


class VersionResponseSchema(Schema):
    version = fields.String()


class Version(Action):
    allow_anonymous_access = True
    response_schema = VersionResponseSchema

    async def run(self, request: JSONRPCRequest):
        return {
            "version": "1.0",
        }
