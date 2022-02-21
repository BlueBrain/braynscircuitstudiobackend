from bcsb.allocations.models import Allocation
from bcsb.brayns.brayns_service import make_brayns_service
from bcsb.consumers import CircuitStudioConsumer
from jsonrpc.consumer import JSONRPCRequest


class ProgressNotifier:
    def __init__(self, request: JSONRPCRequest, consumer: CircuitStudioConsumer):
        self.consumer = consumer
        self.request = request

    async def log(self, message):
        await self.consumer.send_method_response(self.request, {"message": message})


@CircuitStudioConsumer.register_method()
async def start_brayns(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    brayns = make_brayns_service(request.scope["token"])
    progress_notifier = ProgressNotifier(request, consumer)
    allocation: Allocation = await brayns.start_brayns(progress_notifier=progress_notifier)

    return {
        "host": allocation.hostname,
        "port": allocation.port,
        "allocation_id": allocation.id,
    }


@CircuitStudioConsumer.register_method()
async def abort_all_jobs(request: JSONRPCRequest, consumer: CircuitStudioConsumer):
    brayns = make_brayns_service(request.scope["token"])
    await brayns.abort_all_jobs()
    return "OK"
