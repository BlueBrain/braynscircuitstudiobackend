import logging

from bcsb.sessions.models import Session
from bcsb.sessions.serializers import (
    PaginatedResultsSerializer,
)
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from common.utils.pagination import get_paginated_queryset_results

logger = logging.getLogger(__name__)


class GetSessionMethod(JSONRPCMethod):
    response_serializer_class = PaginatedResultsSerializer

    async def run(self):
        queryset = (
            Session.objects.filter(user=self.request.user)
            .order_by("-created_at")
            .values("id", "session_uid", "created_at")
        )

        return await get_paginated_queryset_results(queryset)
