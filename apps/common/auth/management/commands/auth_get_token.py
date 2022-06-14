from getpass import getpass
from os import getenv

from django.core.management import BaseCommand

from common.auth.keycloak import keycloak_openid


class Command(BaseCommand):
    def handle(self, *args, **options):
        env_username = getenv("USER")
        username = input(f"Enter your username (default: '{env_username}'")
        password = getpass()
        # print("code challenge", code_challenge)
        # print(sso_url)
        token = keycloak_openid.token(username, password)
        print(token["access_token"])
