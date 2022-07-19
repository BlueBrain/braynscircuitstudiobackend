from common.jsonrpc.consumer import JSONRPCRequest


class ProgressNotifier:
    def __init__(self, request: JSONRPCRequest):
        self.request = request

    async def log(self, message):
        await self.request.consumer.send_method_response(self.request, {"log": message})
