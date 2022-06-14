from marshmallow import Schema, fields


class CellIdsRequestSchema(Schema):
    path = fields.String()
    targets = fields.List(fields.String(), load_default=[])


class CellIdsResponseSchema(Schema):
    gids = fields.List(fields.Integer())
