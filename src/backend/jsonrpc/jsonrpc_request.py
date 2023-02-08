from typing import Union, Any, Dict

from pydash import get


class JSONRPCRequest:
    id: Union[str, int]
    params: Dict[str, Any]
    method_name: str

    def __init__(self, request_id: Union[str, int], method_name: str, params, ws_handler=None):
        self.id = request_id
        self.method_name = method_name
        self.ws_handler = ws_handler
        self.method_name = method_name
        self.params = params

    @classmethod
    def create(cls, payload, ws_handler) -> "JSONRPCRequest":
        request_id = get(payload, "id")
        method_name = get(payload, "method")
        params = get(payload, "params", {})
        return JSONRPCRequest(
            request_id=request_id,
            method_name=method_name,
            params=params,
            ws_handler=ws_handler,
        )
