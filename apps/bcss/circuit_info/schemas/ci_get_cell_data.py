from marshmallow import Schema, fields


class CellDataRequestSchema(Schema):
    path = fields.String()
    ids = fields.List(fields.Integer(), load_default=[])
    properties = fields.List(fields.String(), load_default=[])


class CellDataResponseSchema(Schema):
    mtypes = fields.List(fields.String())
    etypes = fields.List(fields.String())
    morphology_classes = fields.List(fields.String())
    layers = fields.List(fields.String())
    positions = fields.List(fields.Decimal())
    orientations = fields.List(fields.Decimal())
