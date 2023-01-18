from django.contrib import admin

from bcsb.sessions.models import Session


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ["id", "session_uid", "created_at", "ready_at", "user"]
    list_filter = ["user"]
    search_fields = ["id", "session_uid"]
