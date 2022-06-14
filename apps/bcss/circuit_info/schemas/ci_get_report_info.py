from marshmallow import Schema, fields


class ReportInfoRequestSchema(Schema):
    path = fields.String()
    report = fields.String()


class ReportInfoResponseSchema(Schema):
    start_time = fields.Decimal()
    end_time = fields.Decimal()
    time_step = fields.Decimal()
    data_unit = fields.String()
    time_unit = fields.String()
    frame_count = fields.Integer()
    frame_size = fields.Integer()
