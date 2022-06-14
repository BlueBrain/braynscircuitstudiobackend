from marshmallow import Schema, fields


class EfferentCellIdsRequestSchema(Schema):
    path = fields.String()
    sources = fields.List(fields.Integer(), load_default=[])


class EfferentCellIdsResponseSchema(Schema):
    ids = fields.List(fields.Integer())
