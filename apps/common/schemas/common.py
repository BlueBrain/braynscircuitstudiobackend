from marshmallow import Schema, fields


class VersionResponseSchema(Schema):
    version = fields.String()


class HelpResponseSchema(Schema):
    available_methods = fields.List(fields.String())
