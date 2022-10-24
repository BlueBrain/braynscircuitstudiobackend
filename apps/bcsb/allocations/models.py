from typing import Dict
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import models

from bcsb.sessions.models import Session
from common.utils.models.mixins import CreatedUpdatedMixin


class Allocation(CreatedUpdatedMixin):
    """
    Allocation keeps a reference to an allocated BB5 node and is the expected result of a Unicore job.
    """

    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name="allocations",
    )
    unicore_job_id = models.UUIDField(
        unique=True,
    )
    project = models.CharField(
        max_length=30,
    )
    hostname = models.CharField(
        max_length=50,
        blank=True,
    )
    status = models.CharField(
        max_length=20,
    )
    script = models.TextField(
        blank=True,
    )
    stdout = models.TextField(
        blank=True,
    )
    stderr = models.TextField(
        blank=True,
    )
    brayns_ws_url = models.URLField(blank=True)
    bcss_ws_url = models.URLField(blank=True)

    @classmethod
    async def create_new_allocation_model(cls, session: Session, unicore_job_id: UUID, **kwargs):
        def _perform_query():
            return Allocation.objects.create(
                session=session,
                unicore_job_id=unicore_job_id,
                **kwargs,
            )

        return await sync_to_async(_perform_query)()

    async def update_hostname(self, new_hostname: str):
        return await self.update_model({"hostname": new_hostname})

    async def update_stdout(self, new_stdout: str):
        return await self.update_model({"stdout": new_stdout})

    async def update_stderr(self, new_stderr: str):
        return await self.update_model({"stderr": new_stderr})

    @sync_to_async
    def update_model(self, data: Dict, save: bool = True):
        for field_name, value in data.items():
            setattr(self, field_name, value)
        if save:
            self.save()
        return self
