from marshmallow import Schema, fields


class ProjectionEfferentCellIdsRequestSchema(Schema):
    path = fields.String()
    sources = fields.List(fields.Integer(), load_default=[])
    projection = fields.String()


class ProjectionEfferentCellIdsResponseSchema(Schema):
    ids = fields.List(fields.Integer())
