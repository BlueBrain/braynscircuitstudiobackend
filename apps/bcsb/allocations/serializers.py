from rest_framework import serializers

from .models import Allocation


class AllocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Allocation
        fields = [
            "id",
            "created_at",
            "updated_at",
            "unicore_job_id",
            "project",
            "hostname",
            "status",
            "brayns_ws_url",
            "bcss_ws_url",
        ]
