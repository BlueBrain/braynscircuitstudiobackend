from rest_framework import serializers

from bcsb.sessions.models import Session


class SessionListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = [
            "id",
            "session_uid",
            "created_at",
        ]


class PaginatedResultsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    model_type = serializers.CharField(required=False)
    results = SessionListItemSerializer(many=True)


class GetSessionsResponseSerializer(serializers.Serializer):
    sessions = SessionListItemSerializer(many=True)


class DeleteUserSessionRequestSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class DeleteUserSessionResponseSerializer(serializers.Serializer):
    sessions_deleted = serializers.IntegerField()
