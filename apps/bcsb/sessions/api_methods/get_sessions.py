import logging

from bcsb.sessions.serializers import ListSessionsRequestSerializer
from bcsb.sessions.serializers import (
    ListSessionsResponseSerializer,
)
from bcsb.sessions.utils import get_sessions_with_allocations
from common.jsonrpc.list_jsonrpc_method import ListJSONRPCMethod

logger = logging.getLogger(__name__)


class GetSessionsMethod(ListJSONRPCMethod):
    """
    Returns a list of all user sessions
    """

    request_serializer_class = ListSessionsRequestSerializer
    response_serializer_class = ListSessionsResponseSerializer

    def get_queryset(self):
        return get_sessions_with_allocations(user=self.request.user)
