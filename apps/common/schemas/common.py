from marshmallow import Schema, fields, EXCLUDE, INCLUDE, post_dump


class NoNullSchema(Schema):
    # Based on https://stackoverflow.com/questions/55108696/json-serialization-using-marshmallow-skip-none-attributes
    @post_dump
    def remove_skip_values(self, data, **kwargs):
        return {key: value for key, value in data.items() if value is not None}


class VersionResponseSchema(Schema):
    version = fields.String()


class HelpResponseSchema(Schema):
    available_methods = fields.List(fields.String())


class EmptyRequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE


class EmptyResponseSchema(Schema):
    class Meta:
        unknown = INCLUDE
