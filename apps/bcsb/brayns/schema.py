from marshmallow import Schema, fields


class StartBraynsRequestSchema(Schema):
    project = fields.String(load_default="proj3")


class StartBraynsResponseSchema(Schema):
    host = fields.String()
    allocation_id = fields.Integer()


class AbortAllJobsResponseSchema(Schema):
    result = fields.String(default="OK")
