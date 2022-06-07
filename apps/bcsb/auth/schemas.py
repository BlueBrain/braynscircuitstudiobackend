from marshmallow import Schema, fields, EXCLUDE


class UserInfoResponseSchema(Schema):
    """
    Expected format:

    {
        "sub": "<SUBJECT IDENTIFIER>",
        "email_verified": true,
        "name": "<FIRST NAME> <LAST NAME>",
        "location": "<OFFICE LOCATION>",
        "preferred_username": "<USERNAME>",
        "given_name": "<FIRST NAME>",
        "family_name": "<LAST NAME>",
        "email": "<EMAIL>"
    }
    """

    sub = fields.String()
    email_verified = fields.Boolean()
    name = fields.String()
    location = fields.String()
    preferred_username = fields.String()
    given_name = fields.String()
    family_name = fields.String()
    email = fields.Email()

    class Meta:
        unknown = EXCLUDE


class InvalidTokenResponseSchema(Schema):
    """
    {
        "error": "invalid_token",
        "error_description": "Token verification failed"
    }
    """

    error = fields.String()
    error_description = fields.String()

    class Meta:
        unknown = EXCLUDE
