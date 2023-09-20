import asyncio
from logging import Logger

from ..path import PathValidator
from ..websocket import Server
from .component import Component, EndpointRegistry
from .schemas import SchemaRegistry
from .token import StopToken


class Service:
    def __init__(
        self,
        server: Server,
        stop_token: StopToken,
        endpoints: EndpointRegistry,
        schemas: SchemaRegistry,
        path_validator: PathValidator,
        loop: asyncio.AbstractEventLoop,
        logger: Logger,
    ) -> None:
        self._server = server
        self._stop_token = stop_token
        self._endpoints = endpoints
        self._schemas = schemas
        self._path_validator = path_validator
        self._loop = loop
        self._logger = logger
        self._components = list[Component]()

    @property
    def host(self) -> str:
        return self._server.host

    @property
    def port(self) -> int:
        return self._server.port

    @property
    def stop_token(self) -> StopToken:
        return self._stop_token

    @property
    def schemas(self) -> SchemaRegistry:
        return self._schemas

    @property
    def path_validator(self) -> PathValidator:
        return self._path_validator

    @property
    def logger(self) -> Logger:
        return self._logger

    def add(self, component: Component) -> None:
        name = component.__class__.__name__
        self._logger.info("Registering component %s.", name)
        component.register(self._endpoints)
        self._components.append(component)

    def run(self) -> None:
        try:
            self._logger.info("Starting service.")
            self._loop.run_until_complete(self._server.run())
        except Exception as e:
            self._logger.critical("Service crashed while running: %s.", e)
