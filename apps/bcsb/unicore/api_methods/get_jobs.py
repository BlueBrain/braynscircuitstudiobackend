import logging

from bcsb.sessions.serializers import GetJobsResponseSerializer
from bcsb.unicore.unicore_service import UnicoreService
from common.jsonrpc.jsonrpc_method import JSONRPCMethod

logger = logging.getLogger(__name__)


class GetJobsMethod(JSONRPCMethod):
    """
    Retrieves all Unicore jobs of a user.
    """

    response_serializer_class = GetJobsResponseSerializer

    async def run(self):
        unicore_service = UnicoreService(token=self.request.token)
        jobs = []
        for job_id in await unicore_service.get_jobs():
            job_data = await unicore_service.get_job_status(job_id)
            jobs.append(job_data)

        return {
            "jobs": jobs,
        }
