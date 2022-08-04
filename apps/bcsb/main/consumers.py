from logging import getLogger

from django.contrib.auth.models import User

from common.jsonrpc.jsonrpc_consumer import JSONRPCConsumer

logger = getLogger(__name__)


class CircuitStudioConsumer(JSONRPCConsumer):
    title = "Brayns Circuit Studio Backend"

    async def connect(self):
        await super().connect()
        await self.send_welcome_message()

    async def send_welcome_message(self):
        user: User = self.scope["user"]
        if not user.is_anonymous:
            await self.send_json({"message": f"Welcome {user.first_name}!"})
