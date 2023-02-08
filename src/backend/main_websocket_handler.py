import inspect
import logging
import os
from importlib import import_module
from json import JSONDecodeError
from pkgutil import iter_modules
from typing import Type, Dict

from aiohttp import WSMessage, WSMsgType
from aiohttp.web_request import Request
from aiohttp.web_ws import WebSocketResponse
from pydash import get

from .config import BASE_DIR
from .exceptions import (
    ActionNotFound,
    MethodNotAsynchronous,
    ActionAlreadyRegistered,
    UnsupportedMessageType,
    JSONRPCException,
    JSONRPC_PARSE_ERROR,
)
from .jsonrpc.actions import Action
from .jsonrpc.jsonrpc_request import JSONRPCRequest

logger = logging.getLogger(__name__)


class MainWebSocketHandler:
    initial_request: Request
    ws: WebSocketResponse

    async def get_connection_handler(self, web_request: Request) -> WebSocketResponse:
        self.initial_request = web_request
        self.ws = ws = WebSocketResponse()
        await ws.prepare(web_request)

        logger.info(f"New connection established: {ws.status} from {web_request.remote}")

        async for message in ws:
            message: WSMessage
            try:
                await self.handle_message(web_request, message)
            except JSONRPCException as exception:
                await self.handle_error(message, exception)

        logger.info(f"Connection closed with code: {ws.close_code}")
        return ws

    async def handle_message(self, web_request: Request, message: WSMessage):
        if message.type == WSMsgType.TEXT:
            try:
                payload = message.json()
            except JSONDecodeError as exception:
                return await self.handle_json_error(exception)
        else:
            raise UnsupportedMessageType

        method_name = get(payload, "method")
        action_class = ActionFinder.get_action(method_name)
        action: Action = action_class()

        request = JSONRPCRequest.create(payload, self)

        raw_result = await action.run(request=request)

        result = action.validate_response(raw_result)

        await self.ws.send_json(
            {
                "id": request.id,
                "method": request.method_name,
                "result": result,
            }
        )

    async def handle_json_error(self, exception: JSONDecodeError):
        exception_response = {
            "error": {
                "name": "Invalid JSON",
                "code": JSONRPC_PARSE_ERROR,
                "data": {"message": exception.msg},
            }
        }
        await self.ws.send_json(exception_response)

    async def handle_error(self, message: WSMessage, exception: JSONRPCException):
        message_json = message.json()

        exception_response = {
            "id": get(message_json, "id"),
            "error": {
                "name": exception.name,
                "code": exception.code,
                "data": {
                    "message": exception.message,
                },
            },
        }
        logger.debug(f"Sending error response {exception_response}")
        await self.ws.send_json(exception_response)


class ActionFinder:
    actions: Dict[str, Type[Action]] = {}

    @classmethod
    def autodiscover(cls):
        logger.debug(f"Autodiscover actions...")
        for module_info in iter_modules([os.path.join(BASE_DIR, "actions")]):
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
    def add_action_to_register(cls, action_class: Type[Action]):
        action_name = action_class().name

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
    def get_action(cls, name: str) -> Type[Action]:
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
