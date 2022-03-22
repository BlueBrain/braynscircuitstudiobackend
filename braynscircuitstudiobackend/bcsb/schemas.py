from marshmallow import Schema, fields


class VersionResponseSchema(Schema):
    version = fields.String()


class AuthenticateSchema(Schema):
    token = fields.String()
