from rest_framework import serializers

from common.utils.paths import PathFileValidator


class PathFileField(serializers.CharField):
    default_validators = [PathFileValidator()]
