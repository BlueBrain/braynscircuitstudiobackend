from django.contrib.auth.models import User

from common.jsonrpc.jsonrpc_consumer import JSONRPCConsumer


class CircuitServiceConsumer(JSONRPCConsumer):
    # All methods in BCSS don't require authentication by default
    title = "Brayns Circuit Studio Service"
    is_authentication_required = False

    async def connect(self):
        await super(CircuitServiceConsumer, self).connect()
        await self.send_welcome_message()

    async def send_welcome_message(self):
        user: User = self.scope["user"]
        if not user.is_anonymous:
            await self.send_json({"message": f"Welcome {user.first_name}!"})
        else:
            await self.send_json({"message": "Welcome to BCSS"})
