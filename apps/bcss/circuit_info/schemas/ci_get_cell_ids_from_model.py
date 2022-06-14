from marshmallow import Schema, fields


class CellIdsFromModelRequestSchema(Schema):
    model_id = fields.Integer()


class CellIdsFromModelResponseSchema(Schema):
    gids = fields.List(fields.Integer())
