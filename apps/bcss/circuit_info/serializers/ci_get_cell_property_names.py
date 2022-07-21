from rest_framework import serializers


class CellPropertyNamesRequestSerializer(serializers.Serializer):
    pass


class CellPropertyNamesResponseSerializer(serializers.Serializer):
    property_names = serializers.ListField(child=serializers.CharField())
