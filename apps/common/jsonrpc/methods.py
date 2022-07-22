from types import FunctionType
from typing import Type, Union, Optional

from pydash import replace_end
from rest_framework import serializers

from common.serializers.common import (
    EmptyRequestSerializer,
    EmptyResponseSerializer,
)


class SchemaFieldDoc:
    field: Union[serializers.Field, serializers.Serializer]
    custom_field_name: str

    def __init__(
        self,
        field: Union[serializers.Field, serializers.Serializer],
        custom_field_name: str = None,
    ):
        self.field = field
        self.custom_field_name = custom_field_name

    @property
    def type(self) -> str:
        return replace_end(self.field.__class__.__name__, "Serializer", "")

    @property
    def name(self) -> str:
        return self.custom_field_name or self.field.field_name

    @property
    def is_required(self) -> bool:
        return self.field.required

    @property
    def is_list(self):
        return isinstance(
            self.field, (serializers.ListSerializer, serializers.ListField, serializers.DictField)
        )

    @property
    def get_nested_fields(self):
        nested_fields = []
        if isinstance(self.field, serializers.Serializer):
            for subfield_name, subfield in self.field.fields.items():
                nested_fields.append(SchemaFieldDoc(subfield))
        elif isinstance(self.field, serializers.ListSerializer) and isinstance(
            self.field.child, serializers.Serializer
        ):
            for subfield_name, subfield in self.field.child.fields.items():
                nested_fields.append(SchemaFieldDoc(subfield))
        return nested_fields

    @property
    def inner_field(self) -> Optional["SchemaFieldDoc"]:
        if isinstance(self.field, (serializers.ListField, serializers.DictField)):
            return SchemaFieldDoc(self.field.child)
        elif isinstance(self.field, serializers.ListSerializer):
            return SchemaFieldDoc(self.field.child)
        return


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
