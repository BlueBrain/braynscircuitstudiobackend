from types import FunctionType
from typing import Type

from marshmallow import Schema
from marshmallow.fields import Field, Nested


class SchemaFieldDoc:
    def __init__(self, field):
        self.field: Field = field

    @property
    def type(self):
        return self.field.__class__.__name__

    @property
    def name(self):
        return self.field.name

    @property
    def get_nested_fields(self):
        return (
            [SchemaFieldDoc(field) for field_name, field in self.field.inner.nested.fields.items()]
            if hasattr(self.field, "inner") and isinstance(self.field.inner, Nested)
            else None
        )

    @property
    def inner_field(self):
        return SchemaFieldDoc(self.field.inner) if hasattr(self.field, "inner") else None


class Method:
    name: str
    handler: FunctionType
    request_schema: Type[Schema]
    response_schema: Type[Schema]
    allow_anonymous_access: bool

    def __init__(
        self,
        name: str,
        handler: FunctionType,
        allow_anonymous_access: bool = False,
        request_schema: Type[Schema] = None,
        response_schema: Type[Schema] = None,
    ):
        self.name = name
        self.handler = handler
        self.allow_anonymous_access = allow_anonymous_access
        self.request_schema = request_schema
        self.response_schema = response_schema

    @property
    def docstring(self):
        return self.handler.__doc__

    def get_request_fields(self):
        if not self.request_schema:
            return
        return self.request_schema().fields

    def get_response_fields(self):
        if not self.response_schema:
            return
        return self.response_schema().fields

    def get_request_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.request_schema().fields.values()]
            if self.request_schema
            else None
        )

    def get_response_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.response_schema().fields.values()]
            if self.response_schema
            else None
        )
