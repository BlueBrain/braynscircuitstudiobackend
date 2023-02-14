from os import getenv
from pathlib import Path

APP_HOST = getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(getenv("APP_PORT", 8000))
USE_TLS = bool(int(getenv("USE_TLS", "0")))
LOG_LEVEL = getenv("LOG_LEVEL", "INFO")
BASE_DIR = Path(__file__).resolve().parent
IS_SENTRY_ENABLED = bool(int(getenv("IS_SENTRY_ENABLED", "1")))
