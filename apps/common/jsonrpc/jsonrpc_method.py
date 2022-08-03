from typing import Type

from pydash import kebab_case, replace_end
from rest_framework import serializers

from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.schema_field_doc import SchemaFieldDoc


class JSONRPCMethod:
    method_name: str = None
    request_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    response_serializer_class: Type[serializers.Serializer] = serializers.Serializer
    allow_anonymous_access: bool = False

    @property
    def docstring(self):
        return self.__class__.__doc__

    @classmethod
    def get_request_fields(cls):
        if not cls.request_serializer_class:
            return
        return cls.request_serializer_class().fields

    @classmethod
    def get_response_fields(cls):
        if not cls.response_serializer_class:
            return
        return cls.response_serializer_class().fields

    @classmethod
    def get_request_fields_docs(cls):
        return (
            [SchemaFieldDoc(field) for field in cls.request_serializer_class().fields.values()]
            if cls.request_serializer_class
            else None
        )

    @classmethod
    def get_response_fields_docs(cls):
        return (
            [SchemaFieldDoc(field) for field in cls.response_serializer_class().fields.values()]
            if cls.response_serializer_class
            else None
        )

    @classmethod
    def get_method_name(cls):
        return cls.method_name or replace_end(kebab_case(cls.__name__).lower(), "-method", "")

    @property
    def name(self):
        return self.get_method_name()

    async def run(self, request: JSONRPCRequest):
        raise NotImplementedError
