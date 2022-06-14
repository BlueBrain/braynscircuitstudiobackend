from marshmallow import Schema, fields

from common.schemas.fields import ListOfStrings


class CircuitInfoGeneralInfoRequestSchema(Schema):
    path = fields.String()


class CircuitInfoGeneralInfoResponseSchema(Schema):
    cell_count = fields.Integer()
    cell_properties = ListOfStrings()
    m_types = ListOfStrings()
    e_types = ListOfStrings()
    targets = ListOfStrings()
    reports = ListOfStrings()
    spike_report = ListOfStrings()
