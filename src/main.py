import argparse
import asyncio
import logging
import ssl

import sentry_sdk
from aiohttp import web
from aiohttp.web_runner import AppRunner
from sentry_sdk.integrations.aiohttp import AioHttpIntegration

from backend.config import APP_HOST, APP_PORT, USE_TLS, LOG_LEVEL, BASE_DIR, IS_SENTRY_ENABLED
from backend.main_websocket_handler import MainWebSocketHandler, ActionFinder
from backend.api_reference.request_handler import api_reference_view
from backend.storage.storage_service import StorageService

logger = logging.getLogger(__name__)

if IS_SENTRY_ENABLED:
    sentry_sdk.init(
        dsn="https://6f1453968134400b869602ae907947b3@o224246.ingest.sentry.io/4504645189435392",
        integrations=[
            AioHttpIntegration(),
        ],
        traces_sample_rate=1.0,
    )
else:
    logger.warning(
        "Sentry is disabled. Set `IS_SENTRY_ENABLED` environment variable to `1` to enable it."
    )


parser = argparse.ArgumentParser(description="BraynsCircuitStudio Backend AIOHTTP server")

parser.add_argument(
    "--port",
    dest="port",
    type=int,
    help="Port of the server",
    default=APP_PORT,
)

parser.add_argument(
    "--host",
    dest="host",
    type=str,
    help="Host of the server",
    default=APP_HOST,
)

storage_service = StorageService()

def setup_logging():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        level=LOG_LEVEL,
        handlers=[logging.StreamHandler()],
    )


def get_routes():
    routes = [
        web.get("/", MainWebSocketHandler(storage_service=storage_service).get_connection_handler),
        web.get("/docs", api_reference_view),
    ]
    return routes


async def start_server():
    setup_logging()

    args = parser.parse_args()

    logger.debug(f"BASE_DIR={BASE_DIR}")

    ActionFinder.autodiscover()

    routes = get_routes()

    # Create and setup app instance
    app = web.Application(logger=logger)
    app.router.add_routes(routes)

    if USE_TLS:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain(
            "/etc/tls/tls.crt",
            "/etc/tls/tls.key",
        )
    else:
        ssl_context = None

    app_runner = AppRunner(
        app,
        access_log=None,
    )
    await app_runner.setup()

    tcp_site = web.TCPSite(
        app_runner,
        host=args.host,
        port=args.port,
        ssl_context=ssl_context,
    )
    await tcp_site.start()
    logger.info(f"Server is listening on {args.host}:{args.port}")

    return app_runner, tcp_site


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    runner, site = loop.run_until_complete(start_server())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        loop.run_until_complete(runner.cleanup())
