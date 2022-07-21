from rest_framework import serializers


class VersionResponseSerializer(serializers.Serializer):
    version = serializers.CharField()


class HelpResponseSerializer(serializers.Serializer):
    available_methods = serializers.ListField(child=serializers.CharField())


class EmptyRequestSerializer(serializers.Serializer):
    pass


class EmptyResponseSerializer(serializers.Serializer):
    pass
