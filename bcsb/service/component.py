from logging import Logger
from typing import Protocol

from ..jsonrpc import Endpoint
from .introspection import Handler, create_endpoint


class EndpointRegistry:
    def __init__(self, endpoints: dict[str, Endpoint], logger: Logger) -> None:
        self._endpoints = endpoints
        self._logger = logger

    def add(self, method: str, handler: Handler, description: str = "") -> None:
        self._logger.info("Registering endpoint '%s'.", method)
        if method in self._endpoints:
            raise ValueError(f"Method '{method}' already registered")
        endpoint = create_endpoint(method, description, handler, self._logger)
        self._endpoints[method] = endpoint


class Component(Protocol):
    def register(self, endpoints: EndpointRegistry) -> None: ...
