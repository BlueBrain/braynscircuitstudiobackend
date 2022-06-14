from marshmallow import fields


def ListOfStrings():
    return fields.List(fields.String())
