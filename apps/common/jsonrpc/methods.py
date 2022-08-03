from types import FunctionType
from typing import Type

from rest_framework import serializers

from common.jsonrpc.schema_field_doc import SchemaFieldDoc
from common.serializers.common import (
    EmptyRequestSerializer,
    EmptyResponseSerializer,
)


class Method:
    name: str
    handler: FunctionType
    request_serializer_class: Type[serializers.Serializer]
    response_serializer_class: Type[serializers.Serializer]
    allow_anonymous_access: bool

    def __init__(
        self,
        name: str,
        handler: FunctionType,
        allow_anonymous_access: bool = False,
        request_serializer_class: Type[serializers.Serializer] = None,
        response_serializer_class: Type[serializers.Serializer] = None,
    ):
        self.name = name
        self.handler = handler
        self.allow_anonymous_access = allow_anonymous_access
        self.request_serializer_class = request_serializer_class or EmptyRequestSerializer
        self.response_serializer_class = response_serializer_class or EmptyResponseSerializer

    @property
    def docstring(self):
        return self.handler.__doc__

    def get_request_fields(self):
        if not self.request_serializer_class:
            return
        return self.request_serializer_class().fields

    def get_response_fields(self):
        if not self.response_serializer_class:
            return
        return self.response_serializer_class().fields

    def get_request_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.request_serializer_class().fields.values()]
            if self.request_serializer_class
            else None
        )

    def get_response_fields_docs(self):
        return (
            [SchemaFieldDoc(field) for field in self.response_serializer_class().fields.values()]
            if self.response_serializer_class
            else None
        )
