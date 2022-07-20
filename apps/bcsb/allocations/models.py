from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import models

from bcsb.sessions.models import Session
from bcsb.unicore.models import UnicoreJob
from common.utils.models.mixins import CreatedUpdatedMixin


class Allocation(CreatedUpdatedMixin):
    """
    Allocation keeps a reference to an allocated BB5 node and is the expected result of a Unicore job.
    """

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
    )
    unicore_job = models.ForeignKey(
        UnicoreJob,
        on_delete=models.CASCADE,
    )
    hostname = models.CharField(max_length=50)
    status = models.CharField(max_length=20)
    script = models.TextField(blank=True)
    stdout = models.TextField(blank=True)
    stderr = models.TextField(blank=True)

    @classmethod
    async def create_new_allocation_model(cls, session: Session, job_id: UUID, **kwargs):
        def _perform_query():
            unicore_job = UnicoreJob.objects.get(job_id=job_id, session=session)
            return Allocation.objects.create(session=session, unicore_job=unicore_job, **kwargs)

        return await sync_to_async(_perform_query)()
