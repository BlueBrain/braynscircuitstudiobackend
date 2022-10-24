from rest_framework import serializers

from common.utils.serializers.fields import FilePathField


class ProjectionEfferentCellIdsRequestSerializer(serializers.Serializer):
    path = FilePathField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )
    projection = serializers.CharField()


class ProjectionEfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
