from rest_framework import serializers


class ProjectionEfferentCellIdsRequestSerializer(serializers.Serializer):
    path = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )
    projection = serializers.CharField()


class ProjectionEfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
