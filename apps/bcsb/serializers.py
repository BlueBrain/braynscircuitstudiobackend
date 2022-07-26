from django.contrib.auth.models import User
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


class ListGPFSDirectoryRequestSerializer(serializers.Serializer):
    path = serializers.CharField(required=False, default="/")


class UserInfoSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()
    is_staff = serializers.BooleanField()
    is_authenticated = serializers.BooleanField()

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "is_active",
            "is_staff",
            "is_authenticated",
        ]


class GetUserInfoResponseSerializer(serializers.Serializer):
    user = UserInfoSerializer(required=False)


class DirContentItemSerializer(serializers.Serializer):
    name = serializers.CharField()
    size = serializers.IntegerField()
    last_accessed = serializers.DateTimeField()
    owner = serializers.CharField()
    group = serializers.CharField()


class ListGPFSDirectoryResponseSerializer(serializers.Serializer):
    dirs = DirContentItemSerializer(many=True)
    files = DirContentItemSerializer(many=True)
