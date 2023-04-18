import inspect
import json
import logging
import os
from importlib import import_module
from json import JSONDecodeError
from pkgutil import iter_modules
from uuid import UUID

from aiohttp import WSMessage, WSMsgType
from aiohttp.web_request import Request
from aiohttp.web_ws import WebSocketResponse
from marshmallow import ValidationError
from pydash import get

from backend.jsonrpc.exceptions import (
    ActionNotFound,
    MethodNotAsynchronous,
    ActionAlreadyRegistered,
    UnsupportedMessageType,
    JSONRPCException,
    JSONRPC_PARSE_ERROR,
    VALIDATION_ERROR,
)
from .config import APP_DIR, JSON_TEXT_MESSAGE_OFFSET_BYTES
from .jsonrpc.actions import Action
from .jsonrpc.jsonrpc_request import JSONRPCRequest
from .jsonrpc.running_request import RunningRequest
from .websockets import WebSocketHandler, WebSocketHandlerStorageService

logger = logging.getLogger(__name__)


class MainWebSocketHandler(WebSocketHandler):
    initial_request: Request
    ws: WebSocketResponse
    request_queue = None
    storage_service: WebSocketHandlerStorageService

    def __init__(self, storage_service):
        self.request_queue = {}
        self.storage_service = storage_service

    async def get_connection_handler(self, web_request: Request) -> WebSocketResponse:
        self.initial_request = web_request
        self.ws = WebSocketResponse()
        await self.ws.prepare(web_request)

        logger.info(f"New connection established: {self.ws.status} from {web_request.remote}")

        async for message in self.ws:
            message: WSMessage
            try:
                await self.handle_incoming_message(web_request, message)
            except JSONRPCException as exception:
                await self.handle_error(message, exception)
            except ValidationError as exception:
                await self.handle_validation_exception(message, exception)

        logger.info(f"Connection closed with code: {self.ws.close_code}")
        return self.ws

    async def handle_incoming_message(self, web_request: Request, message: WSMessage):
        payload = await self._get_message_payload(message)

        request = JSONRPCRequest.create(
            payload=payload,
            ws_handler=self,
            ws_message=message,
        )
        action_class = ActionFinder.get_action(request.method_name)
        action: Action = action_class(request=request)
        request.params = action.validate_request(data=request.params)

        running_request = RunningRequest(
            action=action,
            request=request,
            process_action_handler=self.process_method_handler,
            process_error_handler=self.handle_error,
            queue_request=self.queue_request,
            dequeue_request=self.dequeue_request,
        )
        running_request.start()

    async def _get_message_payload(self, message):
        if message.type == WSMsgType.BINARY:
            text_data = message.data[JSON_TEXT_MESSAGE_OFFSET_BYTES:].decode()
            payload = json.loads(text_data)
        elif message.type == WSMsgType.TEXT:
            try:
                payload = message.json()
            except JSONDecodeError as exception:
                return await self.handle_json_error(exception)
        else:
            raise UnsupportedMessageType
        return payload

    async def process_method_handler(self, action: Action, request: JSONRPCRequest):
        raw_result = await action.run()
        result = action.validate_response(raw_result)
        method_result = {
            "id": request.id,
            "method": request.method_name,
            "result": result,
        }
        logger.debug(f"{method_result=}")
        await self.ws.send_json(method_result)

    async def handle_json_error(self, exception: JSONDecodeError):
        exception_response = {
            "error": {
                "name": "Invalid JSON",
                "code": JSONRPC_PARSE_ERROR,
                "data": {"message": exception.msg},
            }
        }
        await self.ws.send_json(exception_response)

    async def handle_validation_exception(
        self,
        message: WSMessage,
        exception: JSONRPCException,
    ):
        message_json = await self._get_message_payload(message)
        exception_response = {
            "id": get(message_json, "id"),
            "error": {
                "name": exception.__class__.__name__,
                "code": VALIDATION_ERROR,
                "messages": exception.messages,
            },
        }
        await self.ws.send_json(exception_response)

    async def handle_error(
        self,
        message: WSMessage,
        exception: JSONRPCException,
    ):
        exception_name = get(exception, "name") or get(exception, "__class__.__name__")
        exception_code = get(exception, "code", 500)
        exception_message = get(exception, "message", str(exception))
        message_json = await self._get_message_payload(message)
        exception_response = {
            "id": get(message_json, "id"),
            "error": {
                "name": exception_name,
                "code": exception_code,
                "data": {
                    "message": exception_message,
                },
            },
        }
        logger.debug(f"Sending error response {exception_response}")
        await self.ws.send_json(exception_response)

    def queue_request(self, running_request: RunningRequest):
        logger.debug(f"Queue request {running_request.id}")
        self.request_queue[running_request.id] = running_request

    def dequeue_request(self, request_id: UUID):
        logger.debug(f"Dequeue request {request_id}")
        del self.request_queue[request_id]
        logger.debug(f"Remaining request: {self.request_queue}")


class ActionFinder:
    actions: dict[str, type[Action]] = {}

    @classmethod
    def autodiscover(cls):
        logger.debug(f"Autodiscover actions...")
        for module_info in iter_modules([os.path.join(APP_DIR, "actions")]):
            logger.debug(f"Loading module: {module_info}")
            module_path = f"backend.actions.{module_info.name}"
            try:
                module = import_module(module_path)
                logger.debug(f"Loaded consumer methods module: {module.__package__}")
            except ModuleNotFoundError:
                # Having API methods package/module is not compulsory, so we can ignore it
                logger.warning("Encountered ModuleNotFoundError - continuing...")
                continue
            except ImportError:
                # We want to be notified of any import errors here (at the app startup)
                logger.warning(f"Encountered ImportError: {module_path}")
                raise

            method_classes = [
                action_class
                for name, action_class in module.__dict__.items()
                if isinstance(action_class, type)
                and issubclass(action_class, Action)
                and action_class not in [Action]
            ]

            # Register encountered actions in the consumer
            for action_class in method_classes:
                cls.add_action_to_register(action_class)

        registered_actions = []
        for action_name in cls.get_available_action_names():
            registered_actions.append(action_name)
        registered_actions.sort()
        logger.debug(
            f"Registered actions:\n"
            + "\n".join([f"{i + 1}. {name}" for i, name in enumerate(registered_actions)])
        )

    @classmethod
    def add_action_to_register(cls, action_class: type[Action]):
        action_name = action_class.name

        if action_name in cls.actions:
            raise ActionAlreadyRegistered(
                f"Action `{action_name}` is already registered as {cls.actions[action_name]}"
            )

        if not inspect.iscoroutinefunction(action_class.run):
            raise MethodNotAsynchronous(
                f"The run() method must be a coroutine function in {cls.__name__}. "
                f"Try using `async def run(...)` instead."
            )

        logger.debug(f"Registering {action_class=} as `{action_name}`")
        cls.actions[action_name] = action_class

    @classmethod
    def get_action(cls, name: str) -> type[Action]:
        try:
            return cls.actions[name]
        except KeyError:
            logger.debug(f"Get method {name=}")
            raise ActionNotFound(f"Action `{name}` could not be found")

    @classmethod
    def get_actions(cls):
        return cls.actions

    @classmethod
    def get_available_action_names(cls):
        return sorted(list(cls.actions.keys()))
