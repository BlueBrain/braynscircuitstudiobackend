from rest_framework import serializers


class AfferentCellIdsRequestSerializer(serializers.Serializer):
    path = serializers.CharField()
    sources = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )


class AfferentCellIdsResponseSerializer(serializers.Serializer):
    ids = serializers.ListField(child=serializers.IntegerField())
