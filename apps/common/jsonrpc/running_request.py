import asyncio
from threading import Thread
from typing import Callable
from uuid import uuid4, UUID

from django.utils.timezone import now

from common.jsonrpc.base import BaseJSONRPCRequest


class RunningRequest:
    id: UUID
    request: BaseJSONRPCRequest
    thread: Thread
    started_at = None
    process_method_handler: Callable
    queue_request: Callable
    dequeue_request: Callable

    def __init__(
        self,
        request: BaseJSONRPCRequest,
        process_method_handler: Callable,
        queue_request: Callable,
        dequeue_request: Callable,
    ):
        self.id = uuid4()
        self.request = request
        self.process_method_handler = process_method_handler
        self.queue_request = queue_request
        self.dequeue_request = dequeue_request
        self.thread = Thread(
            target=asyncio.run,
            args=(self.run_method(),),
        )

    async def run_method(self):
        await self.process_method_handler(self.request)
        # Let the consumer know that the method has finished
        self.dequeue_request(self.id)

    def start(self):
        self.queue_request(self)
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
