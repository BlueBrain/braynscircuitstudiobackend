from backend.jsonrpc.actions import Action


class FsGetRoot(Action):
    async def run(self):
        raise NotImplementedError
