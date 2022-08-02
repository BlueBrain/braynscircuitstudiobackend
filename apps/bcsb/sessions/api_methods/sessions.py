import logging

from bcsb.allocations.models import Allocation
from bcsb.brayns.serializers import (
    StartBraynsRequestSerializer,
    StartBraynsResponseSerializer,
    AbortAllJobsResponseSerializer,
)
from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.sessions.serializers import (
    DeleteUserSessionRequestSerializer,
    DeleteUserSessionResponseSerializer,
    PaginatedResultsSerializer,
)
from bcsb.sessions.session_service import make_session_service
from bcsb.sessions.utils import delete_user_session_by_id
from common.jsonrpc.consumer import JSONRPCRequest
from common.utils.pagination import get_paginated_queryset_results

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method(
    request_serializer_class=StartBraynsRequestSerializer,
    response_serializer_class=StartBraynsResponseSerializer,
)
async def start_new_session(request: JSONRPCRequest):
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


@CircuitStudioConsumer.register_method(response_serializer_class=AbortAllJobsResponseSerializer)
async def abort_all_jobs(request: JSONRPCRequest):
    session_service = await make_session_service(user=request.user, token=request.token)
    await session_service.abort_all_jobs()
    return {"result": "OK"}


@CircuitStudioConsumer.register_method(
    response_serializer_class=PaginatedResultsSerializer,
)
async def get_sessions(request: JSONRPCRequest):
    queryset = (
        Session.objects.filter(user=request.user)
        .order_by("-created_at")
        .values("id", "session_uid", "created_at")
    )

    return await get_paginated_queryset_results(queryset)


@CircuitStudioConsumer.register_method(
    request_serializer_class=DeleteUserSessionRequestSerializer,
    response_serializer_class=DeleteUserSessionResponseSerializer,
)
async def delete_session(request: JSONRPCRequest):
    """
    Deletes a user session indicated by the id parameter.
    Only sessions that belong to the authenticated user can be deleted using this endpoint.
    """
    session_id = request.params["id"]
    sessions_deleted, _ = await delete_user_session_by_id(request.user, session_id=session_id)

    return {
        "session_deleted": sessions_deleted > 0,
    }
