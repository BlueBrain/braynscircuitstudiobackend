from os import getenv
from os.path import join
from pathlib import Path

from django.core.management.utils import get_random_secret_key

from common.common_settings import *  # noqa

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = bool(int(getenv("BCSS_DJANGO_DEBUG", "0")))
DEV_ANONYMOUS_ACCESS = bool(int(getenv("DEV_ANONYMOUS_ACCESS", "0")))
DEV_TOKEN = getenv("DEV_TOKEN", "")
CHECK_ACCESS_TOKENS = not DEBUG or not DEV_ANONYMOUS_ACCESS

ALLOWED_HOSTS = getenv("BCSS_DJANGO_ALLOWED_HOSTS", "" if DEBUG else "").split(",")
SECRET_KEY = getenv("BCSS_DJANGO_SECRET_KEY", get_random_secret_key() if DEBUG else None)

INSTALLED_APPS = [
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Brayns Circuit Studio Service apps
    "common.auth.apps.AuthConfig",
    "bcss.main.apps.MainConfig",
    "bcss.circuit_info.apps.CircuitInfoConfig",
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

ROOT_URLCONF = "bcss.urls"

WSGI_APPLICATION = "bcss.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": getenv("BCSS_DJANGO_DATABASE_NAME", "bcss_db.sqlite"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

STATIC_URL = getenv("BCSS_DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = join(BASE_DIR, "staticfiles")

ASGI_APPLICATION = "bcss.asgi.application"

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [
#                 (getenv("BCSS_REDIS_HOST"), getenv("BCSS_REDIS_PORT")),
#             ],
#         },
#     },
# }

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "bcss_format": {
            "format": "BCSS:{levelname} {asctime} {module} {funcName}:{lineno} -> {message}",
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
            "formatter": "bcss_format",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": getenv("BCSS_LOG_LEVEL", "WARNING"),
        },
        "bcss": {
            "handlers": ["console"],
            "level": getenv("BCSS_LOG_LEVEL", "WARNING"),
        },
    },
}
