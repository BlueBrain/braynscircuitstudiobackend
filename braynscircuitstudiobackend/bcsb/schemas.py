from marshmallow import Schema, fields


class VersionResponseSchema(Schema):
    version = fields.String()


class AuthenticateSchema(Schema):
    token = fields.String()


class ListGPFSDirectoryRequestSchema(Schema):
    path = fields.String(required=False, missing="/")


class DirContentItem(Schema):
    name = fields.String()
    size = fields.Integer()
    last_accessed = fields.DateTime()
    owner = fields.String()
    group = fields.String()


class ListGPFSDirectoryResponseSchema(Schema):
    dirs = fields.List(fields.Nested(DirContentItem()))
    files = fields.List(fields.Nested(DirContentItem()))
