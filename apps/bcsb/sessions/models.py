from uuid import uuid4

from django.contrib.auth.models import User
from django.db import models

from common.utils.models.mixins import CreatedUpdatedMixin


class Session(CreatedUpdatedMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    session_uid = models.UUIDField(
        default=uuid4,
        db_index=True,
    )
    ready_at = models.DateTimeField(
        blank=True,
        null=True,
    )
