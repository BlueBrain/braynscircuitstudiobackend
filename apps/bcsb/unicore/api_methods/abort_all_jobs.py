import logging

from bcsb.sessions.serializers import AbortAllJobsResponseSerializer
from bcsb.sessions.session_service import cleanup_empty_sessions
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class AbortAllJobsMethod(JSONRPCMethod):
    """
    Aborts all Unicore jobs of a user and deletes all related
    session/allocation objects from the database.
    """

    response_serializer_class = AbortAllJobsResponseSerializer

    async def run(self):
        unicore_service = UnicoreService(token=self.request.token)
        await unicore_service.abort_all_jobs()
        await cleanup_empty_sessions(user=self.request.user)
        jobs = await unicore_service.get_jobs()
        return {
            "jobs": jobs,
        }
