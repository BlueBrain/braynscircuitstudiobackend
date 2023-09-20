from dataclasses import dataclass
from typing import Any

JSON_RPC_VERSION = "2.0"

JsonRpcId = int | str | None


@dataclass
class JsonRpcRequest:
    method: str
    params: Any = None
    id: JsonRpcId = None
    jsonrpc: str = JSON_RPC_VERSION


@dataclass
class JsonRpcReply:
    result: Any
    id: JsonRpcId = None
    jsonrpc: str = JSON_RPC_VERSION


@dataclass
class JsonRpcErrorInfo:
    code: int
    message: str
    data: Any = None


@dataclass
class JsonRpcError:
    error: JsonRpcErrorInfo
    id: JsonRpcId = None
    jsonrpc: str = JSON_RPC_VERSION


@dataclass
class Request:
    message: JsonRpcRequest
    binary: bytes = b""

    @property
    def id(self) -> JsonRpcId:
        return self.message.id

    @property
    def method(self) -> str:
        return self.message.method

    @property
    def params(self) -> Any:
        return self.message.params

    @property
    def version(self) -> str:
        return self.message.jsonrpc


@dataclass
class Reply:
    message: JsonRpcReply
    binary: bytes = b""

    @property
    def id(self) -> JsonRpcId:
        return self.message.id

    @property
    def result(self) -> Any:
        return self.message.result
