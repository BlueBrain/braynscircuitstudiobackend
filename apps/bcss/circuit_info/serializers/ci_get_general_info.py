from rest_framework import serializers


class CircuitGeneralInfoRequestSerializer(serializers.Serializer):
    path = serializers.CharField()


class CircuitGeneralInfoResponseSerializer(serializers.Serializer):
    cell_count = serializers.IntegerField()
    cell_properties = serializers.ListField(child=serializers.CharField())
    mtypes = serializers.ListField(child=serializers.CharField())
    etypes = serializers.ListField(child=serializers.CharField())
    targets = serializers.ListField(child=serializers.CharField())
    reports = serializers.ListField(child=serializers.CharField())
    spike_reports = serializers.ListField(child=serializers.CharField())
