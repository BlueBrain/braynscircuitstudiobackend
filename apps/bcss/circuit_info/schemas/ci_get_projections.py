from marshmallow import Schema, fields


class ProjectionsRequestSchema(Schema):
    path = fields.String()


class ProjectionsResponseSchema(Schema):
    projections = fields.List(fields.String())
