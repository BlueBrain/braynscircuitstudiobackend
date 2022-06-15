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

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
