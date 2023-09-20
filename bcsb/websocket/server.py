import asyncio
from logging import Logger
from ssl import SSLContext

from websockets.exceptions import ConnectionClosedError, ConnectionClosedOK
from websockets.server import WebSocketServer, WebSocketServerProtocol, serve

from .interface import (
    Connection,
    ConnectionClosed,
    ConnectionFailed,
    ConnectionHandler,
    Server,
)


class WebSocketConnection(Connection):
    def __init__(self, websocket: WebSocketServerProtocol, logger: Logger) -> None:
        self._websocket = websocket
        self._logger = logger
        self._host = self._websocket.local_address[0]
        self._port = self._websocket.local_address[1]

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    async def receive(self) -> bytes | str:
        self._logger.info("Waiting for messages from %s.", self)
        try:
            data = await self._websocket.recv()
        except (ConnectionClosedOK, ConnectionClosedError) as e:
            self._logger.info("Connection from %s closed in receive.", self)
            self._logger.info("Close reason: %s.", e)
            raise ConnectionClosed(str(e))
        label = _label(data)
        self._logger.info("Received %s from %s (%d bytes).", label, self, len(data))
        self._logger.debug("Frame content: %s.", data)
        return data

    async def send(self, data: bytes | str) -> None:
        label = _label(data)
        self._logger.info("Sending %s to %s (%d bytes).", label, self, len(data))
        self._logger.debug("Frame content: %s.", data)
        try:
            await self._websocket.send(data)
        except (ConnectionClosedOK, ConnectionClosedError) as e:
            self._logger.info("Connection from %s closed while sending.", self)
            self._logger.info("Close reason: %s.", e)
            raise ConnectionClosed(str(e))
        self._logger.info("Frame sent.")


class ServerMonitor:
    def __init__(self, future: asyncio.Future[None]) -> None:
        self._future = future

    def stop(self) -> None:
        self._future.set_result(None)

    async def wait(self) -> None:
        await self._future


class WebServer(Server):
    def __init__(
        self,
        handler: ConnectionHandler,
        monitor: ServerMonitor,
        logger: Logger,
        host: str,
        port: int,
        ssl: SSLContext | None,
        max_frame_size: int,
    ) -> None:
        self._handler = handler
        self._monitor = monitor
        self._logger = logger
        self._host = host
        self._port = port
        self._ssl = ssl
        self._max_frame_size = max_frame_size

    @property
    def host(self) -> str:
        return self._host

    @property
    def port(self) -> int:
        return self._port

    async def run(self) -> None:
        async with await self._start():
            self._logger.info("Server running on %s.", self.url)
            await self._monitor.wait()

    async def _start(self) -> WebSocketServer:
        self._logger.info("Starting server on %s.", self.url)
        try:
            return await serve(
                self._handle,
                self._host,
                self._port,
                ssl=self._ssl,
                max_size=self._max_frame_size,
                ping_interval=None,
            )
        except Exception as e:
            self._logger.error("Failed to start server: %s.", e)
            raise ConnectionFailed(str(e))

    async def _handle(self, websocket: WebSocketServerProtocol) -> None:
        connection = WebSocketConnection(websocket, self._logger)
        self._logger.info("New connection from %s.", connection)
        await self._handler.handle(connection)


def _label(data: bytes | str) -> str:
    return "binary" if isinstance(data, bytes) else "text"
