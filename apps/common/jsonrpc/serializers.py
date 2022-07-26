from rest_framework import serializers


class JSONRPCRequestSerializer(serializers.Serializer):
    id = serializers.CharField()
    jsonrpc = serializers.CharField(default="2.0")
    method = serializers.CharField()
    params = serializers.DictField(required=False)


class JSONRPCErrorSerializer(serializers.Serializer):
    name = serializers.CharField()
    data = serializers.DictField(required=False)
    code = serializers.IntegerField(required=False)
    message = serializers.CharField(required=False)


class JSONRPCResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    jsonrpc = serializers.CharField(default="2.0")
    error = JSONRPCErrorSerializer(required=False)
    result = serializers.DictField(required=False)
