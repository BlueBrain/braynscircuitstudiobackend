from typing import Union, Optional

from pydash import replace_end
from rest_framework import serializers


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
