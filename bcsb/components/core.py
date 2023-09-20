from dataclasses import dataclass

from ..jsonrpc import EndpointSchema
from ..service import Component, EndpointRegistry, SchemaRegistry, StopToken
from ..version import VERSION


@dataclass
class VersionResult:
    version: str


@dataclass
class SchemaParams:
    endpoint: str


class Core(Component):
    def __init__(self, schemas: SchemaRegistry, token: StopToken) -> None:
        self._schemas = schemas
        self._token = token

    def register(self, endpoints: EndpointRegistry) -> None:
        endpoints.add("version", self.version, "Application version major.minor.patch")
        endpoints.add("registry", self.registry, "Available endpoints")
        endpoints.add("schema", self.schema, "Schema of given endpoint")
        endpoints.add("quit", self.quit, "Quit application")

    async def version(self) -> VersionResult:
        return VersionResult(VERSION)

    async def registry(self) -> list[str]:
        return self._schemas.methods

    async def schema(self, params: SchemaParams) -> EndpointSchema:
        return self._schemas.get(params.endpoint)

    async def quit(self) -> None:
        self._token.stop()
