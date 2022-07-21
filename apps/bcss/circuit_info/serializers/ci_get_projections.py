from rest_framework import serializers


class ProjectionsRequestSerializer(serializers.Serializer):
    path = serializers.CharField()


class ProjectionsResponseSerializer(serializers.Serializer):
    projections = serializers.ListField(child=serializers.CharField())
