from typing import Type

from rest_framework import serializers


def load_via_serializer(
    data,
    serializer_class: Type[serializers.Serializer],
    raise_exception: bool = True,
):
    serializer_instance = serializer_class(data=data)
    serializer_instance.is_valid(raise_exception=raise_exception)
    return serializer_instance.validated_data
