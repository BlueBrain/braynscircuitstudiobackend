from typing import Protocol

from ..websocket import ServerMonitor


class StopToken(Protocol):
    def stop(self) -> None: ...


class TokenAdapter(StopToken):
    def __init__(self, monitor: ServerMonitor) -> None:
        self._monitor = monitor

    def stop(self) -> None:
        self._monitor.stop()
