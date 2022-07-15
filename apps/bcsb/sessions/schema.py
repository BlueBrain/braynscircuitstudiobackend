from marshmallow import Schema, fields


class SessionListItemSchema(Schema):
    id = fields.Integer()
    session_uid = fields.UUID()
    created_at = fields.DateTime()


class GetSessionsResponseSchema(Schema):
    sessions = fields.List(fields.Nested(SessionListItemSchema()))
