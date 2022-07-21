from rest_framework import serializers


class CellIdsFromModelRequestSerializer(serializers.Serializer):
    model_id = serializers.IntegerField()


class CellIdsFromModelResponseSerializer(serializers.Serializer):
    gids = serializers.ListField(child=serializers.IntegerField())
