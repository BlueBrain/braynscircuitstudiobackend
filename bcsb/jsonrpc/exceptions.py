from dataclasses import dataclass
from typing import Any

PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INVALID_PARAMS = -32602
INTERNAL_ERROR = -32603


@dataclass
class JsonRpcException(Exception):
    message: str
    code: int
    data: Any = None


class ParseError(JsonRpcException):
    def __init__(self, error: str) -> None:
        super().__init__(
            message=f"Failed to parse JSON: {error}",
            code=PARSE_ERROR,
        )


class InvalidRequest(JsonRpcException):
    def __init__(self, error: str) -> None:
        super().__init__(
            message=f"Invalid request: {error}",
            code=INVALID_REQUEST,
        )


class MethodNotFound(JsonRpcException):
    def __init__(self, method: str) -> None:
        super().__init__(
            message=f"Method not found: '{method}'",
            code=METHOD_NOT_FOUND,
        )


class InvalidParams(JsonRpcException):
    def __init__(self, error: str) -> None:
        super().__init__(
            message=f"Invalid params: {error}",
            code=INVALID_PARAMS,
        )


class InternalError(JsonRpcException):
    def __init__(self, message: str, data: Any = None) -> None:
        super().__init__(
            message=f"Internal error: {message}",
            code=INTERNAL_ERROR,
            data=data,
        )


def unexpected(e: Exception) -> JsonRpcException:
    return InternalError(str(e))
