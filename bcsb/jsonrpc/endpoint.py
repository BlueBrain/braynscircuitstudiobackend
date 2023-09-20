from dataclasses import dataclass
from typing import Any, Protocol

from ..json import JsonSchema


@dataclass
class EndpointParams:
    message: Any
    binary: bytes


@dataclass
class EndpointResult:
    message: Any
    binary: bytes


@dataclass
class EndpointSchema:
    method: str
    description: str
    params: JsonSchema
    result: JsonSchema


class EndpointHandler(Protocol):
    async def handle(self, params: EndpointParams) -> EndpointResult:
        ...


@dataclass
class Endpoint:
    schema: EndpointSchema
    handler: EndpointHandler
