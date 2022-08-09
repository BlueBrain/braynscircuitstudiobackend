from rest_framework import serializers

from common.utils.serializers.fields import PathFileField


class CellDataRequestSerializer(serializers.Serializer):
    path = PathFileField()
    ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
    )
    properties = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )


class CellDataResponseSerializer(serializers.Serializer):
    mtypes = serializers.ListField(child=serializers.CharField())
    etypes = serializers.ListField(child=serializers.CharField())
    morphology_classes = serializers.ListField(child=serializers.CharField())
    layers = serializers.ListField(child=serializers.CharField())
    positions = serializers.ListField(
        child=serializers.DecimalField(max_digits=20, decimal_places=5)
    )
    orientations = serializers.ListField(
        child=serializers.DecimalField(max_digits=20, decimal_places=5)
    )
