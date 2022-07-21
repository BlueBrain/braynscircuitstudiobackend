from types import FunctionType
from typing import Type

from rest_framework import serializers

from common.serializers.common import (
    EmptyRequestSerializer,
    EmptyResponseSerializer,
)


class SchemaFieldDoc:
    def __init__(self, field):
        self.field: serializers.Field = field

    @property
    def type(self):
        return self.field.__class__.__name__

    @property
    def name(self):
        # fixme return self.field.name
        raise NotImplementedError

    @property
    def get_nested_fields(self):
        # fixme return (
        #     [SchemaFieldDoc(field) for field_name, field in self.field.inner.nested.fields.items()]
        #     if hasattr(self.field, "inner") and isinstance(self.field.inner, Nested)
        #     else None
        # )
        raise NotImplementedError

    @property
    def inner_field(self):
        return SchemaFieldDoc(self.field.inner) if hasattr(self.field, "inner") else None


class Method:
    name: str
    handler: FunctionType
    request_serializer: Type[serializers.Serializer]
    response_serializer: Type[serializers.Serializer]
    allow_anonymous_access: bool

    def __init__(
        self,
        name: str,
        handler: FunctionType,
        allow_anonymous_access: bool = False,
        request_serializer: Type[serializers.Serializer] = None,
        response_serializer: Type[serializers.Serializer] = None,
    ):
        self.name = name
        self.handler = handler
        self.allow_anonymous_access = allow_anonymous_access
        self.request_serializer = request_serializer or EmptyRequestSerializer
        self.response_serializer = response_serializer or EmptyResponseSerializer

    @property
    def docstring(self):
        return self.handler.__doc__

    def get_request_fields(self):
        if not self.request_serializer:
            return
        return self.request_serializer().fields

    def get_response_fields(self):
        if not self.response_serializer:
            return
        return self.response_serializer().fields

    def get_request_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.request_serializer().fields.values()]
            if self.request_serializer
            else None
        )

    def get_response_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.response_serializer().fields.values()]
            if self.response_serializer
            else None
        )
