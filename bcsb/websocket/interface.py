from typing import Protocol


class ConnectionFailed(Exception):
    ...


class ConnectionClosed(Exception):
    ...


class Connection(Protocol):
    def __str__(self) -> str:
        return self.url

    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def host(self) -> str:
        ...

    @property
    def port(self) -> int:
        ...

    async def receive(self) -> bytes | str:
        ...

    async def send(self, data: bytes | str) -> None:
        ...


class ConnectionHandler(Protocol):
    async def handle(self, connection: Connection) -> None:
        ...


class Server(Protocol):
    @property
    def url(self) -> str:
        return f"{self.host}:{self.port}"

    @property
    def host(self) -> str:
        ...

    @property
    def port(self) -> int:
        ...

    async def run(self) -> None:
        ...
