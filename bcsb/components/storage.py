from dataclasses import dataclass

from ..jsonrpc import InvalidParams
from ..service import Component, EndpointRegistry


@dataclass
class GetParams:
    key: str


@dataclass
class GetResult:
    value: str


@dataclass
class SetParams:
    key: str
    value: str


class Storage(Component):
    def __init__(self) -> None:
        self._values = dict[str, str]()

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add("storage-session-get", self.get, "Retreive stored value")
        endpoints.add("storage-session-set", self.set, "Store value")

    async def get(self, params: GetParams) -> GetResult:
        value = self._values.get(params.key)
        if value is None:
            raise InvalidParams(f"No values for key '{params.key}'")
        return GetResult(value)

    async def set(self, params: SetParams) -> None:
        self._values[params.key] = params.value
