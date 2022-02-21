from django.contrib import admin

from bcsb.unicore.models import UnicoreJob


@admin.register(UnicoreJob)
class UnicoreJobAdmin(admin.ModelAdmin):
    list_display = [
        "user",
        "job_id",
        "created_at",
        "status",
    ]
    list_filter = [
        "user",
        "status",
    ]
    search_fields = [
        "job_id",
    ]
