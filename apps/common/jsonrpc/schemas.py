from marshmallow import fields

from common.schemas.common import NoNullSchema


class JSONRPCErrorObject(NoNullSchema):
    code = fields.Integer()
    name = fields.String()
    message = fields.String()


class JSONRPCResponseSchema(NoNullSchema):
    id = fields.String()
    jsonrpc = fields.String(default="2.0")
    error = fields.Nested(JSONRPCErrorObject(), required=False)
    result = fields.Dict(required=False)
