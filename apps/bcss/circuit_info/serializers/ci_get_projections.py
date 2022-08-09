from rest_framework import serializers

from common.utils.serializers.fields import FilePathField


class ProjectionsRequestSerializer(serializers.Serializer):
    path = FilePathField()


class ProjectionsResponseSerializer(serializers.Serializer):
    projections = serializers.ListField(child=serializers.CharField())
