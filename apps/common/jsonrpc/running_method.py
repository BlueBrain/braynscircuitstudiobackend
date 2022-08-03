import asyncio
from threading import Thread
from uuid import uuid4, UUID

from django.utils.timezone import now

from common.jsonrpc.base_jsonrpc_consumer import BaseJSONRPCConsumer
from common.jsonrpc.jsonrpc_request import JSONRPCRequest


class RunningMethod:
    id: UUID
    request: JSONRPCRequest
    thread: Thread
    started_at = None
    consumer: BaseJSONRPCConsumer

    def __init__(
        self,
        consumer: BaseJSONRPCConsumer,
        request: JSONRPCRequest,
    ):
        self.id = uuid4()
        self.consumer = consumer
        self.request = request
        self.thread = Thread(
            target=asyncio.run,
            args=(self.run_method(),),
        )

    async def run_method(self):
        await self.consumer.process_method_handler(self.request)
        # Let the consumer know that the method has finished
        self.consumer.dequeue_job(self.id)

    def start(self):
        self.consumer.queue_job(self)
        self.started_at = now()
        return self.thread.start()

    def is_alive(self):
        return self.thread.is_alive()

    @property
    def request_id(self):
        return self.request.id

    @property
    def method_name(self):
        return self.request.method_name

    @property
    def uptime(self):
        if self.started_at is None:
            return 0
        return (now() - self.started_at).total_seconds()
