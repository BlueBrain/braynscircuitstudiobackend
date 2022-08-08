import logging

from bcsb.sessions.models import Session
from bcsb.sessions.serializers import ListSessionsRequestSerializer
from bcsb.sessions.serializers import (
    ListSessionsResponseSerializer,
)
from common.jsonrpc.jsonrpc_method import ListJSONRPCMethod

logger = logging.getLogger(__name__)


class ListSessionsMethod(ListJSONRPCMethod):
    request_serializer_class = ListSessionsRequestSerializer
    response_serializer_class = ListSessionsResponseSerializer

    def get_queryset(self):
        return (
            Session.objects.filter(user=self.request.user)
            .order_by("-created_at")
            .values("id", "session_uid", "created_at", "ready_at")
        )
