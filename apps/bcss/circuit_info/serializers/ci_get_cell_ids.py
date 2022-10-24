from rest_framework import serializers

from common.utils.serializers.fields import FilePathField


class CellIdsRequestSerializer(serializers.Serializer):
    path = FilePathField()
    targets = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
        default=list,
    )


class CellIdsResponseSerializer(serializers.Serializer):
    gids = serializers.ListField(child=serializers.IntegerField())
