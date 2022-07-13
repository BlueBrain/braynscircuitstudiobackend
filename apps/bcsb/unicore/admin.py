from django.contrib import admin

from bcsb.unicore.models import UnicoreJob


@admin.register(UnicoreJob)
class UnicoreJobAdmin(admin.ModelAdmin):
    list_display = [
        "job_id",
        "session",
        "created_at",
        "status",
    ]
    list_filter = [
        "status",
    ]
    search_fields = [
        "job_id",
    ]
