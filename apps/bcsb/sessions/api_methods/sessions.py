import logging

from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.brayns.serializers import (
    StartBraynsRequestSerializer,
    StartBraynsResponseSerializer,
    AbortAllJobsResponseSerializer,
)
from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.sessions.serializers import GetSessionsResponseSerializer
from bcsb.sessions.session_service import make_session_service
from common.jsonrpc.consumer import JSONRPCRequest

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method(
    request_serializer=StartBraynsRequestSerializer,
    response_serializer=StartBraynsResponseSerializer,
)
async def start_new_session(request: JSONRPCRequest):
    session_service = await make_session_service(
        user=request.user,
        token=request.token,
    )

    request_serializer = StartBraynsRequestSerializer(data=request.params)
    request_serializer.is_valid(raise_exception=True)
    params = request_serializer.validated_data

    progress_notifier = ProgressNotifier(request)
    allocation: Allocation = await session_service.start(
        progress_notifier=progress_notifier,
        project=params["project"],
    )

    return {
        "host": allocation.hostname,
        "allocation_id": allocation.id,
    }


@CircuitStudioConsumer.register_method(response_serializer=AbortAllJobsResponseSerializer)
async def abort_all_jobs(request: JSONRPCRequest):
    session_service = await make_session_service(user=request.user, token=request.token)
    await session_service.abort_all_jobs()
    return {"result": "OK"}


@database_sync_to_async
def get_session_list(user: User):
    return (
        Session.objects.filter(user=user)
        .order_by("-created_at")
        .values("id", "session_uid", "created_at")[:100]
    )


@CircuitStudioConsumer.register_method(response_serializer=GetSessionsResponseSerializer)
async def get_sessions(request: JSONRPCRequest):
    sessions = await get_session_list(user=request.user)
    logger.debug(f"Sessions: {sessions}")

    return {
        "sessions": sessions,
    }
