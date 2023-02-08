from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action


class VersionResponseSchema(Schema):
    version = fields.String()


class Version(Action):
    allow_anonymous_access = True
    response_schema = VersionResponseSchema

    async def run(self):
        return {
            "version": "1.0",
        }
