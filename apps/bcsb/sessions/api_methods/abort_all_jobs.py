import logging

from bcsb.sessions.models import Session
from bcsb.sessions.serializers import AbortAllJobsResponseSerializer
from bcsb.sessions.session_service import make_session_service
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class AbortAllJobsMethod(JSONRPCMethod):
    """
    Returns a Session object together with its allocations.
    """

    response_serializer_class = AbortAllJobsResponseSerializer

    async def run(self):
        session_service = await make_session_service(
            user=self.request.user,
            token=self.request.token,
            session_instance=Session(user=self.request.user),
        )
        await session_service.abort_all_jobs()
        jobs = await session_service.unicore_service.get_jobs()
        return {
            "jobs": jobs,
        }
