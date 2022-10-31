from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.sessions.models import Session


@database_sync_to_async
def delete_user_session_by_id(user: User, session_id: int):
    return Session.objects.get(user=user, id=session_id).delete()


@database_sync_to_async
def get_main_session_allocation(session_id: int):
    last_allocation = (
        Allocation.objects.filter(session_id=session_id).order_by("-created_at").first()
    )
    return last_allocation


def get_sessions_with_allocations(user: User):
    return (
        Session.objects.filter(
            user=user,
            allocations__isnull=False,
        )
        .prefetch_related("allocations")
        .order_by("-created_at")
    )
