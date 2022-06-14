from os import getenv
from os.path import join
from pathlib import Path

from django.core.management.utils import get_random_secret_key


BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = bool(int(getenv("DJANGO_DEBUG", "0")))
DEV_ANONYMOUS_ACCESS = bool(int(getenv("DEV_ANONYMOUS_ACCESS", "0")))
CHECK_ACCESS_TOKENS = not DEBUG or not DEV_ANONYMOUS_ACCESS

ALLOWED_HOSTS = getenv("DJANGO_ALLOWED_HOSTS", "" if DEBUG else None).split(",")
SECRET_KEY = getenv("DJANGO_SECRET_KEY", get_random_secret_key() if DEBUG else None)

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

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "bcss.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "TEST": {
            "NAME": ":memory:",
        },
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

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Europe/Zurich"

USE_I18N = True

USE_L10N = True

USE_TZ = True

STATIC_URL = getenv("DJANGO_STATIC_URL", "/static/")
STATIC_ROOT = join(BASE_DIR, "staticfiles")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

ASGI_APPLICATION = "bcss.asgi.application"

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels_redis.core.RedisChannelLayer",
#         "CONFIG": {
#             "hosts": [
#                 (getenv("DJANGO_REDIS_HOST"), getenv("DJANGO_REDIS_PORT")),
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
            "level": "DEBUG",
        },
        "bcss": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
    },
}

API_METHODS_PACKAGE_NAME = "api_methods"

BBP_UNICORE_URL = "https://bbpunicore.epfl.ch:8080"
BBP_UNICORE_CORE_PATH = "/BB5-CSCS/rest/core"
BBP_KEYCLOAK_AUTH_URL = "https://bbpauth.epfl.ch/auth/"
BBP_KEYCLOAK_CLIENT_ID = "bbp-braynscircuitstudio"
BBP_KEYCLOAK_REALM_NAME = "BBP"
BBP_KEYCLOAK_SSO_URL = "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/auth"
BBP_KEYCLOAK_AUTH_TOKEN_URL = (
    "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/token"
)
BBP_KEYCLOAK_USER_INFO_URL = (
    "https://bbpauth.epfl.ch/auth/realms/BBP/protocol/openid-connect/userinfo"
)
BBP_KEYCLOAK_HOST = "bbpauth.epfl.ch"
