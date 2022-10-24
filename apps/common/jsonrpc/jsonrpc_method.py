from typing import Type

from pydash import kebab_case, replace_end, get
from rest_framework import serializers

from common.jsonrpc.base import BaseJSONRPCMethod, BaseJSONRPCRequest
from common.jsonrpc.schema_field_doc import SchemaFieldDoc


class JSONRPCMethod(BaseJSONRPCMethod):
    request: BaseJSONRPCRequest = None
    custom_method_name: str = None
    request_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    response_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    allow_anonymous_access: bool = False

    def prepare(self, request: BaseJSONRPCRequest = None):
        self.request = request

    @property
    def docstring(self):
        return self.__class__.__doc__

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

    def get_method_name(self):
        return self.custom_method_name or replace_end(
            kebab_case(self.__class__.__name__).lower(),
            "-method",
            "",
        )

    @property
    def name(self):
        return self.get_method_name()

    def get_request_param(self, param_path: str):
        return get(self.request.params, param_path)
