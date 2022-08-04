from typing import Dict, Any
from uuid import UUID

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseJSONRPCConsumer(AsyncJsonWebsocketConsumer):
    title: str = ""
    methods = {}
    is_authentication_required = True
    request_queue: Dict[UUID, Any] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request_queue = {}

    @classmethod
    def get_available_method_names(cls):
        return list(cls.methods.keys())
