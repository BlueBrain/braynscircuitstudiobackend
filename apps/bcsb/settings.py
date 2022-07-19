from os import getenv
from os.path import join
from pathlib import Path

from django.core.management.utils import get_random_secret_key

from common.common_settings import *  # noqa

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = getenv("BCSB_DJANGO_SECRET_KEY", get_random_secret_key())
DEBUG = bool(int(getenv("BCSB_DJANGO_DEBUG", "0")))
ALLOWED_HOSTS = getenv("BCSB_DJANGO_ALLOWED_HOSTS", "").split(",")

DEV_ANONYMOUS_ACCESS = bool(int(getenv("DEV_ANONYMOUS_ACCESS", "0")))
DEV_TOKEN = getenv("DEV_TOKEN", "")
CHECK_ACCESS_TOKENS = not DEBUG or not DEV_ANONYMOUS_ACCESS

INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Brayns Circuit Studio Backend apps
    "common.auth.apps.AuthConfig",
    "bcsb.apps.BraynsCircuitStudioBackendConfig",
    "bcsb.unicore.apps.UnicoreConfig",
    "bcsb.allocations.apps.AllocationsConfig",
    "bcsb.brayns.apps.BraynsConfig",
    "bcsb.api_browser.apps.APIBrowserConfig",
    "bcsb.sessions.apps.SessionsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "bcsb.urls"

WSGI_APPLICATION = "bcsb.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": getenv("BCSB_DB_HOST"),
        "PORT": getenv("BCSB_DB_PORT"),
        "NAME": getenv("BCSB_DB_NAME"),
        "USER": getenv("BCSB_DB_USER"),
        "PASSWORD": getenv("BCSB_DB_PASSWORD"),
        "TEST": {
            "NAME": getenv("BCSB_DB_TEST", "bcsb_test"),
        },
    }
}

STATIC_URL = getenv("BCSB_DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = join(BASE_DIR, "staticfiles")

ASGI_APPLICATION = "bcsb.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                (getenv("BCSB_REDIS_HOST"), getenv("BCSB_REDIS_PORT")),
            ],
        },
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "bcsb_format": {
            "format": "BCSB:{levelname} {asctime} {module} {funcName}:{lineno} -> {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "bcsb_format",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": getenv("BCSB_LOG_LEVEL", "WARNING"),
        },
        "bcsb": {
            "handlers": ["console"],
            "level": getenv("BCSB_LOG_LEVEL", "WARNING"),
        },
    },
}
