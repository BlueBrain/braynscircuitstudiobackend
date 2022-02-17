from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.db import models

from bcsb.auth.middleware import get_user_from_access_token
from utils.models.mixins import CreatedUpdatedMixin


class UnicoreJob(CreatedUpdatedMixin):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    job_id = models.UUIDField(
        unique=True,
    )
    status = models.CharField(
        max_length=30,
    )
    last_synced_at = models.DateTimeField(
        blank=True,
        null=True,
    )

    @classmethod
    async def create_from_job_id(cls, job_id, token, status):
        user = await get_user_from_access_token(token)
        assert not user.is_anonymous, "Anonymous users cannot create jobs"
        await sync_to_async(UnicoreJob.objects.create)(
            job_id=job_id,
            user=user,
            status=status,
        )
