from rest_framework import serializers

from common.utils.serializers.fields import PathFileField


class ProjectionsRequestSerializer(serializers.Serializer):
    path = PathFileField()


class ProjectionsResponseSerializer(serializers.Serializer):
    projections = serializers.ListField(child=serializers.CharField())
