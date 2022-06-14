from marshmallow import fields


def ListOfStrings():
    return fields.List(fields.String())


def ListOfIntegers():
    return fields.List(fields.Integer())
