from rest_framework import serializers

from bcsb.allocations.serializers import AllocationSerializer
from bcsb.sessions.models import Session


class StartBraynsRequestSerializer(serializers.Serializer):
    project = serializers.CharField(default="proj3")


class NewSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
            "ready_at",
        ]


class StartBraynsResponseSerializer(serializers.Serializer):
    session = NewSessionSerializer()
    allocation = AllocationSerializer()
