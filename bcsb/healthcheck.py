import asyncio
import ssl
import sys

from websockets.client import connect


async def _try_connect() -> None:
    if len(sys.argv) < 2:
        raise ValueError("No BCSB server URI specified")
    uri = sys.argv[1]
    ca = None
    if len(sys.argv) > 2:
        ca = sys.argv[2]
    context = None
    if uri.startswith("wss://"):
        context = ssl.create_default_context(cafile=ca)
    async with connect(uri, ssl=context):
        pass


def healthcheck() -> None:
    asyncio.run(_try_connect())
