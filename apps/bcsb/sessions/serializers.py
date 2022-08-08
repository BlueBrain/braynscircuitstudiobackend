from rest_framework import serializers

from bcsb.sessions.models import Session
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
    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
            "ready_at",
        ]


class DeleteUserSessionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteUserSessionResponseSerializer(serializers.Serializer):
    sessions_deleted = serializers.IntegerField()
