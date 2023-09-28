import asyncio
import sys
from logging import Formatter, Logger, StreamHandler
from ssl import PROTOCOL_TLS_SERVER, SSLContext

from .components import Circuit, Core, Filesystem, Memory, Sonata, Storage, Volume
from .jsonrpc import Endpoint, JsonRpcHandler
from .path import PathValidator
from .service import EndpointRegistry, SchemaRegistry, Service, TokenAdapter
from .settings import Settings
from .websocket import ServerMonitor, WebServer


def create_logger(level: int | str) -> Logger:
    logger = Logger("BCSB", level)
    handler = StreamHandler(sys.stdout)
    format = "[%(name)s][%(levelname)s] %(message)s"
    formatter = Formatter(format)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def create_ssl_context(settings: Settings) -> SSLContext | None:
    if not settings.secure:
        return None
    context = SSLContext(PROTOCOL_TLS_SERVER)
    context.load_cert_chain(settings.certificate, settings.key, settings.password)
    return context


def create_server(
    settings: Settings,
    handler: JsonRpcHandler,
    logger: Logger,
    monitor: ServerMonitor,
) -> WebServer:
    return WebServer(
        handler,
        monitor,
        logger,
        settings.host,
        settings.port,
        create_ssl_context(settings),
        settings.max_frame_size,
    )


def add_components(service: Service) -> None:
    components = [
        Circuit(service.path_validator, service.logger),
        Core(service.schemas, service.stop_token),
        Filesystem(service.path_validator),
        Memory(),
        Sonata(service.path_validator, service.logger),
        Storage(),
        Volume(service.path_validator, service.logger),
    ]
    for component in components:
        service.add(component)


async def create_service(settings: Settings) -> Service:
    logger = create_logger(settings.log_level)
    logger.debug("%s.", settings)
    endpoints = dict[str, Endpoint]()
    registry = EndpointRegistry(endpoints, logger)
    schemas = SchemaRegistry(endpoints)
    handler = JsonRpcHandler(endpoints, logger)
    future = asyncio.Future[None]()
    monitor = ServerMonitor(future)
    token = TokenAdapter(monitor)
    validator = PathValidator(settings.base_directory)
    server = create_server(settings, handler, logger, monitor)
    service = Service(server, token, registry, schemas, validator, logger)
    add_components(service)
    return service
