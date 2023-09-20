from ..jsonrpc import Endpoint, EndpointSchema, InvalidParams


class SchemaRegistry:
    def __init__(self, endpoints: dict[str, Endpoint]) -> None:
        self._endpoints = endpoints

    @property
    def methods(self) -> list[str]:
        return list(self._endpoints.keys())

    def get(self, method: str) -> EndpointSchema:
        endpoint = self._endpoints.get(method)
        if endpoint is None:
            raise InvalidParams(f"No schema found for method '{method}'")
        return endpoint.schema
