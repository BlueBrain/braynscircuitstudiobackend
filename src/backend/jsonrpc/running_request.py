import asyncio
import logging
from datetime import datetime
from threading import Thread
from typing import Callable
from uuid import uuid4, UUID

from pytz import utc

from .actions import Action
from .exceptions import JSONRPCException
from .jsonrpc_request import JSONRPCRequest

logger = logging.getLogger(__name__)


def now():
    return datetime.utcnow().replace(tzinfo=utc)


class RunningRequest:
    id: UUID
    action: Action
    request: JSONRPCRequest
    thread: Thread
    started_at = None
    process_action_handler: Callable
    process_error_handler: Callable
    queue_request: Callable
    dequeue_request: Callable

    def __init__(
        self,
        action: Action,
        request: JSONRPCRequest,
        process_action_handler: Callable,
        process_error_handler: Callable,
        queue_request: Callable,
        dequeue_request: Callable,
    ):
        self.id = uuid4()
        self.action = action
        self.request = request
        self.process_action_handler = process_action_handler
        self.process_error_handler = process_error_handler
        self.queue_request = queue_request
        self.dequeue_request = dequeue_request
        self.thread = Thread(
            target=asyncio.run,
            args=(self.run_action(),),
        )

    async def run_action(self):
        try:
            await self.process_action_handler(self.action, self.request)
        except JSONRPCException as exception:
            await self.process_error_handler(
                message=self.request.ws_message,
                exception=exception,
            )

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
