from logging import getLogger

from django.contrib.auth.models import User

from jsonrpc.consumer import JSONRPCConsumer

logger = getLogger(__name__)


class CircuitStudioConsumer(JSONRPCConsumer):
    async def connect(self):
        await super(CircuitStudioConsumer, self).connect()
        await self.send_welcome_message()

    async def send_welcome_message(self):
        user: User = self.scope["user"]
        if not user.is_anonymous:
            await self.send_json(f"Welcome {user.first_name}!")
