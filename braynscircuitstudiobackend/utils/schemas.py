from marshmallow import Schema


def dump_schema(schema: type(Schema), data: dict):
    return schema().dump(data)


def load_schema(schema: type(Schema), raw_data):
    return schema().load(raw_data)
