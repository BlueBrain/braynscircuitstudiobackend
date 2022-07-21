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


class GetSessionsResponseSerializer(serializers.Serializer):
    sessions = SessionListItemSerializer(many=True)
