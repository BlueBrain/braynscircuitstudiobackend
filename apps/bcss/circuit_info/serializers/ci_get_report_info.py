from rest_framework import serializers


class ReportInfoRequestSerializer(serializers.Serializer):
    path = serializers.CharField()
    report = serializers.CharField()


class ReportInfoResponseSerializer(serializers.Serializer):
    start_time = serializers.DecimalField(max_digits=20, decimal_places=5)
    end_time = serializers.DecimalField(max_digits=20, decimal_places=5)
    time_step = serializers.DecimalField(max_digits=20, decimal_places=5)
    data_unit = serializers.CharField()
    time_unit = serializers.CharField()
    frame_count = serializers.IntegerField()
    frame_size = serializers.IntegerField()
