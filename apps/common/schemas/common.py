from marshmallow import Schema, fields, EXCLUDE, INCLUDE


class VersionResponseSchema(Schema):
    version = fields.String()


class HelpResponseSchema(Schema):
    available_methods = fields.List(fields.String())


class EmptyRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class EmptyResponseSchema(Schema):
    class Meta:
        unknown = INCLUDE
