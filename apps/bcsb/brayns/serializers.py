from rest_framework import serializers

from bcsb.allocations.serializers import AllocationSerializer
from bcsb.sessions.serializers import SessionListItemSerializer


class StartBraynsRequestSerializer(serializers.Serializer):
    project = serializers.CharField(default="proj3")


class StartBraynsResponseSerializer(serializers.Serializer):
    session = SessionListItemSerializer()
    allocation = AllocationSerializer()
