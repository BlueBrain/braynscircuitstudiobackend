from marshmallow import Schema, fields


class AfferentCellIdsRequestSchema(Schema):
    path = fields.String()
    sources = fields.List(fields.Integer(), load_default=[])


class AfferentCellIdsResponseSchema(Schema):
    ids = fields.List(fields.Integer())
