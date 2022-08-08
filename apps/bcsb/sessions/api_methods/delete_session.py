import logging

from bcsb.sessions.serializers import (
    DeleteUserSessionRequestSerializer,
    DeleteUserSessionResponseSerializer,
)
from bcsb.sessions.utils import delete_user_session_by_id
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class DeleteSessionMethod(JSONRPCMethod):
    """
    Deletes a user session indicated by the id parameter.
    Only sessions that belong to the authenticated user can be deleted using this endpoint.
    """

    request_serializer_class = DeleteUserSessionRequestSerializer
    response_serializer_class = DeleteUserSessionResponseSerializer

    async def run(self):
        session_id = self.request.params["id"]
        sessions_deleted, _ = await delete_user_session_by_id(
            self.request.user, session_id=session_id
        )

        return {
            "session_deleted": sessions_deleted > 0,
        }
