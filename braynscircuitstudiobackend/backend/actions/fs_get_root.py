from braynscircuitstudiobackend.backend.config import BASE_DIR_PATH
from braynscircuitstudiobackend.backend.jsonrpc.actions import Action


class FsGetRoot(Action):
    async def run(self):
        return BASE_DIR_PATH
