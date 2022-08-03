from typing import Type

from pydash import kebab_case, replace_end
from rest_framework import serializers

from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.schema_field_doc import SchemaFieldDoc


class JSONRPCMethod:
    name: str = None
    request_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    response_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    allow_anonymous_access: bool = False

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

    async def run(self, request: JSONRPCRequest):
        raise NotImplementedError

    @classmethod
    def get_method_name(cls):
        return cls.name or replace_end(kebab_case(cls.__name__).lower(), "-method", "")
