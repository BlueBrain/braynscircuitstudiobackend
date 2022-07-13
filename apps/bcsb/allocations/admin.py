from django.contrib import admin

from bcsb.allocations.models import Allocation


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = [
        "hostname",
        "created_at",
    ]
    search_fields = ["hostname"]
    date_hierarchy = "created_at"
