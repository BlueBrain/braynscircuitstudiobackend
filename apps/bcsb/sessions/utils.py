from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.sessions.models import Session


@database_sync_to_async
def delete_user_session_by_id(user: User, session_id: int):
    return Session.objects.get(user=user, id=session_id).delete()
