from rest_framework import serializers

from common.utils.serializers.fields import FilePathField


class AfferentCellIdsRequestSerializer(serializers.Serializer):
    path = FilePathField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )


class AfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
