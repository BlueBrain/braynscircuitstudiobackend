from marshmallow import Schema, fields

from common.schemas.fields import ListOfStrings


class VersionResponseSchema(Schema):
    version = fields.String()


class HelpResponseSchema(Schema):
    available_methods = ListOfStrings()
