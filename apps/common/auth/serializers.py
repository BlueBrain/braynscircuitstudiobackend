from rest_framework import serializers


class AuthenticateRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class AuthenticateResponseUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_authenticated = serializers.BooleanField()


class AuthenticateResponseSerializer(serializers.Serializer):
    user = AuthenticateResponseUserSerializer()


class KeycloakUserInfoResponseSerializer(serializers.Serializer):
    sub = serializers.CharField()
    email_verified = serializers.BooleanField()
    name = serializers.CharField()
    location = serializers.CharField(required=False)
    preferred_username = serializers.CharField()
    given_name = serializers.CharField()
    family_name = serializers.CharField()
    email = serializers.EmailField()


class InvalidTokenResponseSerializer(serializers.Serializer):
    error = serializers.CharField()
    error_description = serializers.CharField()
