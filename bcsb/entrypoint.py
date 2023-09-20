from .factory import create_service
from .settings import parse_argv


def run() -> None:
    settings = parse_argv()
    service = create_service(settings)
    service.run()
