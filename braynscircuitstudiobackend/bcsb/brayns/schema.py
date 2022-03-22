from marshmallow import Schema, fields


class StartBraynsRequestSchema(Schema):
    project = fields.String(default="proj3")
