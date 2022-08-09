from rest_framework import serializers

from common.utils.serializers.fields import PathFileField


class CircuitGeneralInfoRequestSerializer(serializers.Serializer):
    path = PathFileField()


class CircuitGeneralInfoResponseSerializer(serializers.Serializer):
    cell_count = serializers.IntegerField()
    cell_properties = serializers.ListField(child=serializers.CharField())
    mtypes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    etypes = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    targets = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    reports = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
    spike_reports = serializers.ListField(
        child=serializers.CharField(),
        required=False,
    )
