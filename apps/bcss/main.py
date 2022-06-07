import argparse
import logging
import ssl
from os import getenv

from aiohttp import web

from consumer import BCSSConsumer

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument("--path")
parser.add_argument("--port")

DEV = bool(int(getenv("BCSS_DEV", "1")))


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s %(message)s",
        datefmt="%Y/%m/%d %H:%M:%S",
        level=logging.DEBUG,
        handlers=[logging.StreamHandler()],
    )


def get_routes():
    routes = [
        web.get("/ws", BCSSConsumer().get_handler),
    ]
    return routes


def run_server():
    setup_logging()
    logger.info("Starting BraynsCircuitStudio Service...")
    routes = get_routes()

    # Create and setup app instance
    app = web.Application()
    app.add_routes(routes)

    args = parser.parse_args()

    if not DEV:
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        ssl_context.check_hostname = False
        ssl_context.load_cert_chain("/etc/tls/tls.crt", "/etc/tls/tls.key")
    else:
        ssl_context = None

    logger.info("Setup complete. Starting the web app...")
    web.run_app(app, path=args.path, port=args.port, ssl_context=ssl_context)


if __name__ == "__main__":
    run_server()
