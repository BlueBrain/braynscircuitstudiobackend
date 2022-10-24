from common.jsonrpc.base import BaseJSONRPCRequest


class ProgressNotifier:
    def __init__(self, request: BaseJSONRPCRequest):
        self.request = request

    async def log(self, message):
        await self.request.consumer.send_method_response(self.request, {"log": message})
