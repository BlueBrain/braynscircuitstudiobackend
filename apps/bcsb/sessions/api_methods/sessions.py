import logging

from bcsb.allocations.models import Allocation
from bcsb.brayns.serializers import (
    StartBraynsRequestSerializer,
    StartBraynsResponseSerializer,
    AbortAllJobsResponseSerializer,
)
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.sessions.serializers import (
    DeleteUserSessionRequestSerializer,
    DeleteUserSessionResponseSerializer,
    PaginatedResultsSerializer,
)
from bcsb.sessions.session_service import make_session_service
from bcsb.sessions.utils import delete_user_session_by_id
from common.jsonrpc.jsonrpc_consumer import JSONRPCRequest
from common.jsonrpc.methods import JSONRPCMethod
from common.utils.pagination import get_paginated_queryset_results

logger = logging.getLogger(__name__)


class StartNewSessionMethod(JSONRPCMethod):
    """
    Starts a full new Brayns/BCSS session on a new node.
    """

    request_serializer_class = StartBraynsRequestSerializer
    response_serializer_class = StartBraynsResponseSerializer

    async def run(self, request: JSONRPCRequest):
        session_service = await make_session_service(
            user=request.user,
            token=request.token,
        )
        params = request.params
        progress_notifier = ProgressNotifier(request)
        allocation: Allocation = await session_service.start(
            progress_notifier=progress_notifier,
            project=params["project"],
        )

        return {
            "host": allocation.hostname,
            "allocation_id": allocation.id,
        }


class AbortAllJobsMethod(JSONRPCMethod):
    response_serializer_class = AbortAllJobsResponseSerializer

    async def run(self, request: JSONRPCRequest):
        session_service = await make_session_service(user=request.user, token=request.token)
        await session_service.abort_all_jobs()
        return {
            "result": "OK",
        }


class GetSessionsMethod(JSONRPCMethod):
    response_serializer_class = PaginatedResultsSerializer

    async def get_sessions(self, request: JSONRPCRequest):
        queryset = (
            Session.objects.filter(user=request.user)
            .order_by("-created_at")
            .values("id", "session_uid", "created_at")
        )

        return await get_paginated_queryset_results(queryset)


class DeleteSessionMethod(JSONRPCMethod):
    """
    Deletes a user session indicated by the id parameter.
    Only sessions that belong to the authenticated user can be deleted using this endpoint.
    """

    request_serializer_class = DeleteUserSessionRequestSerializer
    response_serializer_class = DeleteUserSessionResponseSerializer

    async def run(self, request: JSONRPCRequest):
        session_id = request.params["id"]
        sessions_deleted, _ = await delete_user_session_by_id(request.user, session_id=session_id)

        return {
            "session_deleted": sessions_deleted > 0,
        }
