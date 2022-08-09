from rest_framework import serializers

from common.utils.serializers.fields import PathFileField


class EfferentCellIdsRequestSerializer(serializers.Serializer):
    path = PathFileField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )


class EfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
