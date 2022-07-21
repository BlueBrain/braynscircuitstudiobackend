from rest_framework import serializers


class EfferentCellIdsRequestSerializer(serializers.Serializer):
    path = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )


class EfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
