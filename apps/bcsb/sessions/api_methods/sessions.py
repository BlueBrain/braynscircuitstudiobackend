import logging

from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.brayns.schema import (
    StartBraynsRequestSchema,
    AbortAllJobsResponseSchema,
    StartBraynsResponseSchema,
)
from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.sessions.schema import GetSessionsResponseSchema
from bcsb.sessions.session_service import make_session_service
from common.jsonrpc.consumer import JSONRPCRequest
from common.utils.schemas import load_schema

logger = logging.getLogger(__name__)


@CircuitStudioConsumer.register_method(
    request_schema=StartBraynsRequestSchema,
    response_schema=StartBraynsResponseSchema,
)
async def start_new_session(request: JSONRPCRequest):
    session_service = await make_session_service(
        user=request.user,
        token=request.token,
    )
    params = load_schema(StartBraynsRequestSchema, request.params)
    progress_notifier = ProgressNotifier(request)
    allocation: Allocation = await session_service.start(
        progress_notifier=progress_notifier,
        project=params["project"],
    )

    return {
        "host": allocation.hostname,
        "allocation_id": allocation.id,
    }


@CircuitStudioConsumer.register_method(response_schema=AbortAllJobsResponseSchema)
async def abort_all_jobs(request: JSONRPCRequest):
    session_service = await make_session_service(user=request.user, token=request.token)
    await session_service.abort_all_jobs()
    return {"result": "OK"}


@database_sync_to_async
def get_session_list(user: User):
    return list(Session.objects.filter(user=user).values("id", "session_uid", "created_at"))


@CircuitStudioConsumer.register_method(response_schema=GetSessionsResponseSchema)
async def get_sessions(request: JSONRPCRequest):
    sessions = await get_session_list(user=request.user)
    logger.debug(f"Sessions: {sessions}")

    return {
        "sessions": sessions,
    }
