import asyncio

from .factory import create_service
from .settings import Settings, parse_argv


async def serve(settings: Settings) -> None:
    service = await create_service(settings)
    await service.run()


def run() -> None:
    settings = parse_argv()
    asyncio.run(serve(settings))
