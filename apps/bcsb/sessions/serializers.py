from rest_framework import serializers

from bcsb.allocations.models import Allocation
from bcsb.sessions.models import Session
from common.utils.pagination.serializers import (
    BasePaginatedResultsSerializer,
    BasePaginatedRequestSerializer,
)


class MainAllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = [
            "id",
            "project",
            "hostname",
            "bcss_ws_url",
            "brayns_ws_url",
            "unicore_job_id",
        ]


class SessionListItemSerializer(serializers.ModelSerializer):
    allocations = MainAllocationSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
            "ready_at",
            "allocations",
        ]


class ListSessionsRequestSerializer(BasePaginatedRequestSerializer):
    pass


class ListSessionsResponseSerializer(BasePaginatedResultsSerializer):
    results = SessionListItemSerializer(many=True)


class GetSessionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    session_uid = serializers.UUIDField(required=False)


class GetSessionResponseSerializer(serializers.ModelSerializer):
    allocations = MainAllocationSerializer(many=True)

    class Meta:
        model = Session
        fields = [
            # "id",
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
