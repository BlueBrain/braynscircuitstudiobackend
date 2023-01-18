import logging

from channels.db import database_sync_to_async
from pydash import get

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
        session_id = get(self.request.params, "id")
        session_uid = get(self.request.params, "session_uid")

        params = {
            "user": self.request.user,
        }

        if session_id:
            params["id"] = session_id
        elif session_uid:
            params["session_uid"] = session_uid
        else:
            raise ValueError("id or session_uid are required")

        logger.debug(f"Get session {params=}")

        return Session.objects.prefetch_related("allocations").get(**params)

    async def run(self):
        session = await self.get_object()
        return session
