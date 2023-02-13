from marshmallow import Schema, fields

from backend.jsonrpc.actions import Action
from version import VERSION


class VersionResponseSchema(Schema):
    version = fields.String(metadata={"ex": "123"})


class Version(Action):
    """Returns the current version of the backend service."""

    allow_anonymous_access = True
    response_schema = VersionResponseSchema

    async def run(self):
        return {
            "version": VERSION,
        }
