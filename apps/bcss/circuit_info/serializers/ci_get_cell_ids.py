from rest_framework import serializers


class CellIdsRequestSerializer(serializers.Serializer):
    path = serializers.CharField()
    targets = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


class CellIdsResponseSerializer(serializers.Serializer):
    gids = serializers.ListField(child=serializers.IntegerField())
