from typing import Dict, Any
from uuid import UUID

from channels.generic.websocket import AsyncJsonWebsocketConsumer


class BaseJSONRPCConsumer(AsyncJsonWebsocketConsumer):
    title: str = "„"
    methods = {}
    is_authentication_required = True
    job_queue: Dict[UUID, Any] = None
