from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.schema import GetSessionsResponseSchema

from bcsb.allocations.models import Allocation
from bcsb.brayns.schema import (
    StartBraynsRequestSchema,
    AbortAllJobsResponseSchema,
    StartBraynsResponseSchema,
)
from bcsb.consumers import CircuitStudioConsumer
from bcsb.sessions.session_service import make_session_service
from common.jsonrpc.consumer import JSONRPCRequest
from common.utils.schemas import load_schema


class ProgressNotifier:
    def __init__(self, request: JSONRPCRequest, consumer: CircuitStudioConsumer):
        self.consumer = consumer
        self.request = request

    async def log(self, message):
        await self.consumer.send_method_response(self.request, {"log": message})


@CircuitStudioConsumer.register_method(
    request_schema=StartBraynsRequestSchema,
    response_schema=StartBraynsResponseSchema,
)
async def start_new_session(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    session_service = await make_session_service(user=request.user, token=request.token)
    params = load_schema(StartBraynsRequestSchema, request.params)
    progress_notifier = ProgressNotifier(request, consumer)
    allocation: Allocation = await session_service.start(
        progress_notifier=progress_notifier,
        project=params["project"],
    )

    return {
        "host": allocation.hostname,
        "allocation_id": allocation.id,
    }


@CircuitStudioConsumer.register_method(response_schema=AbortAllJobsResponseSchema)
async def abort_all_jobs(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    session_service = await make_session_service(user=request.user, token=request.token)
    await session_service.abort_all_jobs()
    return {"result": "OK"}


@CircuitStudioConsumer.register_method(response_schema=GetSessionsResponseSchema)
def get_sessions():
    return {
        "sessions": [],
    }
