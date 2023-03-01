class WebSocketHandlerStorageService:
    def get(self, key: str, default_value=None):
        raise NotImplementedError

    def set(self, key: str, value):
        raise NotImplementedError


class WebSocketHandler:
    storage_service: WebSocketHandlerStorageService
