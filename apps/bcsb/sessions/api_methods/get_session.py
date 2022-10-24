import logging

from channels.db import database_sync_to_async

from bcsb.sessions.models import Session
from common.jsonrpc.jsonrpc_method import JSONRPCMethod
from bcsb.sessions.serializers import GetSessionRequestSerializer, GetSessionResponseSerializer

logger = logging.getLogger(__name__)


class GetSessionMethod(JSONRPCMethod):
    """
    Returns a Session object together with its allocations.
    """

    request_serializer_class = GetSessionRequestSerializer
    response_serializer_class = GetSessionResponseSerializer

    @database_sync_to_async
    def get_object(self):
        return Session.objects.prefetch_related("allocations").get(
            user=self.request.user, id=self.request.params["id"]
        )

    async def run(self):
        session = await self.get_object()
        return session
