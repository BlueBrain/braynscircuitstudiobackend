from pydash import get

from braynscircuitstudiobackend.backend.websockets import WebSocketHandlerStorageService


class StorageService(WebSocketHandlerStorageService):
    _data: dict

    def __init__(self):
        self._data = {}

    def set(self, key: str, value):
        self._data[key] = value

    def get(self, key, default_value=None):
        return get(self._data, key, default_value)
