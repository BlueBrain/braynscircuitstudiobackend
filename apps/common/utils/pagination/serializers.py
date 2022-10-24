from rest_framework import serializers


class BasePaginatedRequestSerializer(serializers.Serializer):
    limit = serializers.IntegerField(
        required=False,
        allow_null=True,
        default=None,
        min_value=1,
    )
    offset = serializers.IntegerField(
        required=False,
        default=0,
        min_value=0,
    )


class BasePaginatedResultsSerializer(serializers.Serializer):
    total_count = serializers.IntegerField()
    limit = serializers.IntegerField()
    offset = serializers.IntegerField()
    next_offset = serializers.IntegerField(allow_null=True)
    prev_offset = serializers.IntegerField(allow_null=True)
    model_type = serializers.CharField(required=False)
