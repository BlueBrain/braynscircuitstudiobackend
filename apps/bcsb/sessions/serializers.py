from rest_framework import serializers

from bcsb.allocations.serializers import AllocationSerializer
from bcsb.sessions.models import Session
from bcsb.unicore.serializers import JobStatusResponseSerializer
from common.utils.pagination.serializers import (
    BasePaginatedResultsSerializer,
    BasePaginatedRequestSerializer,
)


class SessionListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
            "ready_at",
        ]


class ListSessionsRequestSerializer(BasePaginatedRequestSerializer):
    pass


class ListSessionsResponseSerializer(BasePaginatedResultsSerializer):
    results = SessionListItemSerializer(many=True)


class GetSessionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class GetSessionResponseSerializer(serializers.ModelSerializer):
    allocations = AllocationSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
            "updated_at",
            "ready_at",
            "allocations",
        ]


class DeleteUserSessionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteUserSessionResponseSerializer(serializers.Serializer):
    sessions_deleted = serializers.IntegerField()


class AbortAllJobsResponseSerializer(serializers.Serializer):
    jobs = serializers.ListField(child=serializers.UUIDField())


class JobInfoSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()
    queue = serializers.CharField()
    status = serializers.CharField()
    resource_status = serializers.CharField()
    status_message = serializers.CharField(
        allow_blank=True,
    )
    current_time = serializers.DateTimeField()


class GetJobsResponseSerializer(serializers.Serializer):
    jobs = JobInfoSerializer(many=True)
