from rest_framework import serializers

from common.utils.serializers.fields import FilePathField


class CellIdsFromModelRequestSerializer(serializers.Serializer):
    path = FilePathField()
    model_id = serializers.IntegerField()


class CellIdsFromModelResponseSerializer(serializers.Serializer):
    gids = serializers.ListField(child=serializers.IntegerField())
