from typing import Union, Any, Dict

from aiohttp import WSMessage
from pydash import get

from backend.websockets import WebSocketHandler


class JSONRPCRequest:
    id: Union[str, int]
    params: Dict[str, Any]
    method_name: str
    ws_handler: WebSocketHandler
    ws_message: WSMessage

    def __init__(
        self,
        request_id: Union[str, int],
        method_name: str,
        params,
        ws_message: WSMessage,
        ws_handler=None,
    ):
        self.id = request_id
        self.method_name = method_name
        self.ws_handler = ws_handler
        self.method_name = method_name
        self.params = params
        self.ws_message = ws_message

    @classmethod
    def create(
        cls,
        payload,
        ws_handler: WebSocketHandler,
        ws_message: WSMessage,
    ) -> "JSONRPCRequest":
        request_id = get(payload, "id")
        method_name = get(payload, "method")
        params = get(payload, "params", {})
        return JSONRPCRequest(
            request_id=request_id,
            method_name=method_name,
            params=params,
            ws_handler=ws_handler,
            ws_message=ws_message,
        )
