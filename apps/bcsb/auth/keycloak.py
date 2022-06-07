from django.conf import settings
from keycloak import KeycloakOpenID

keycloak_openid = KeycloakOpenID(
    server_url=settings.BBP_KEYCLOAK_AUTH_URL,
    client_id=settings.BBP_KEYCLOAK_CLIENT_ID,
    realm_name=settings.BBP_KEYCLOAK_REALM_NAME,
)
