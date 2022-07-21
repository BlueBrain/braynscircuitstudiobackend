from rest_framework import serializers


class JSONRPCErrorSerializer(serializers.Serializer):
    code = serializers.IntegerField()
    name = serializers.CharField()
    message = serializers.CharField()


class JSONRPCResponseSerializer(serializers.Serializer):
    id = serializers.CharField()
    jsonrpc = serializers.CharField(default="2.0")
    error = JSONRPCErrorSerializer(required=False)
    result = serializers.DictField(required=False)
