from marshmallow import Schema, fields


class CircuitGeneralInfoRequestSchema(Schema):
    path = fields.String()


class CircuitGeneralInfoResponseSchema(Schema):
    cell_count = fields.Integer()
    cell_properties = fields.List(fields.String())
    mtypes = fields.List(fields.String())
    etypes = fields.List(fields.String())
    targets = fields.List(fields.String())
    reports = fields.List(fields.String())
    spike_report = fields.List(fields.String())
