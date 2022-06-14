from asgiref.sync import sync_to_async
from django.contrib.auth.models import User
from django.db import models

from common.auth.auth_service import get_user_from_access_token
from common.utils.models.mixins import CreatedUpdatedMixin


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

    def __str__(self):
        return f"UnicoreJob #{str(self.job_id)[:8]}"

    @classmethod
    async def create_from_job_id(cls, job_id, token, status):
        user = await get_user_from_access_token(token)
        assert not user.is_anonymous, "Anonymous users cannot create jobs"
        return await sync_to_async(UnicoreJob.objects.create)(
            job_id=job_id,
            user=user,
            status=status,
        )

    @classmethod
    async def update_job(cls, job_id, status):
        def _perform_query():
            UnicoreJob.objects.filter(job_id=job_id).update(status=status)

        return await sync_to_async(_perform_query)()
