from marshmallow import Schema, fields


class CellPropertyNamesRequestSchema(Schema):
    pass


class CellPropertyNamesResponseSchema(Schema):
    property_names = fields.List(fields.String())
