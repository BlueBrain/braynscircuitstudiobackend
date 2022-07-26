from rest_framework import serializers


class UserInfoResponseSerializer(serializers.Serializer):
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
