import json

from common.jsonrpc.base import BaseJSONRPCResponse
from common.jsonrpc.constants import JSONRPC_VERSION
from common.jsonrpc.exceptions import (
    MethodAndErrorNotAllowedTogether,
)


class JSONRPCResponse(BaseJSONRPCResponse):
    def __init__(
        self,
        request_id=None,
        result=None,
        error=None,
        method_name: str = None,
    ):
        self.id = request_id if method_name is None else None
        self.method_name = method_name
        assert self.id or self.method_name, "Response must contain either `id` or `method`"
        if result and error:
            raise MethodAndErrorNotAllowedTogether
        self.result = result
        self.error = error

    async def get_serialized_result(self):
        return json.dumps(
            await self.get_response_payload(),
        )

    async def get_response_payload(self) -> dict:
        payload = {
            "jsonrpc": JSONRPC_VERSION,
        }
        if self.id is not None:
            payload["id"] = self.id
        if self.error:
            payload["error"] = self.error
        if self.result:
            payload["result"] = self.result
        if self.method_name:
            payload["method"] = self.method_name
        return payload
