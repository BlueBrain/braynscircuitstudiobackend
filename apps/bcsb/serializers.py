from rest_framework import serializers


class AuthenticateRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class AuthenticateResponseSerializer(serializers.Serializer):
    user = serializers.CharField()


class ListGPFSDirectoryRequestSerializer(serializers.Serializer):
    path = serializers.CharField(required=False, default="/")


class DirContentItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    last_accessed = serializers.DateTimeField()
    owner = serializers.CharField()
    group = serializers.CharField()


class ListGPFSDirectoryResponseSerializer(serializers.Serializer):
    dirs = serializers.ListField(child=DirContentItemSerializer())
    files = serializers.ListField(child=DirContentItemSerializer())
