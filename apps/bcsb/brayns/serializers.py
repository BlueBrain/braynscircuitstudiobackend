from rest_framework import serializers


class StartBraynsRequestSerializer(serializers.Serializer):
    project = serializers.CharField(default="proj3")


class StartBraynsResponseSerializer(serializers.Serializer):
    host = serializers.CharField()
    allocation_id = serializers.IntegerField()


class AbortAllJobsResponseSerializer(serializers.Serializer):
    result = serializers.CharField(default="OK")
