from marshmallow import Schema, fields


class CircuitInfoGeneralInfoRequestSchema(Schema):
    path = fields.String()


class CircuitInfoGeneralInfoResponseSchema(Schema):
    cell_count = fields.Integer()
    cell_properties = fields.List(fields.String())
    m_types = fields.List(fields.String())
    e_types = fields.List(fields.String())
    targets = fields.List(fields.String())
    reports = fields.List(fields.String())
    spike_report = fields.List(fields.String())
