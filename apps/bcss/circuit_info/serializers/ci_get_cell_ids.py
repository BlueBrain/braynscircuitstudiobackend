from rest_framework import serializers

from common.utils.serializers.fields import PathFileField


class CellIdsRequestSerializer(serializers.Serializer):
    path = PathFileField()
    targets = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


class CellIdsResponseSerializer(serializers.Serializer):
    gids = serializers.ListField(child=serializers.IntegerField())
