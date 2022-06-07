from marshmallow import Schema, fields


class StartBraynsRequestSchema(Schema):
    project = fields.String(default="proj3")


class StartBraynsResponseSchema(Schema):
    host = fields.String()
    port = fields.Integer()
    allocation_id = fields.Integer()


class AbortAllJobsResponseSchema(Schema):
    result = fields.String(default="OK")
