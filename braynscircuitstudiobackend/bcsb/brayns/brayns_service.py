from asyncio import sleep
from uuid import UUID

from bcsb.allocations.models import Allocation
from bcsb.unicore.unicore_service import UnicoreService, UnicoreJobStatus

import logging

logger = logging.getLogger(__name__)


def make_brayns_service(token: str) -> "BraynsService":
    unicore_service = UnicoreService(token=token)
    return BraynsService(unicore_service=unicore_service)


class BraynsService:
    DEFAULT_BRAYNS_STARTUP_SCRIPT = """#!/bin/bash
echo $(hostname -f) > hostname

source /etc/profile.d/bb5.sh
# module load unstable brayns/2.0.0

BRAYNS_ROOT=/gpfs/bbp.cscs.ch/home/acfleury/src/spack/opt/spack/linux-rhel7-x86_64/gcc-9.3.0/brayns-devbuildtest-xo6qcu/bin/
${BRAYNS_ROOT}braynsService \
    --uri 0.0.0.0:5000 \
    --plugin braynsCircuitExplorer \
    --plugin braynsCircuitInfo \
    --sandbox-path /gpfs/bbp.cscs.ch
"""
    _unicore_service: UnicoreService

    def __init__(self, unicore_service: UnicoreService):
        self._unicore_service = unicore_service

    async def start_brayns(self, progress_notifier):
        logger.debug("Starting Brayns...")
        await progress_notifier.log("Starting Brayns...")

        job_id = await self._unicore_service.start_job_with_script(
            project="proj3",
            name="Circuit visualization",
            memory="0",
            runtime="8h",
            exclusive=True,
            script_content=self.get_startup_script(),
        )
        await progress_notifier.log(f"Registered new job = {job_id}")

        job_status: UnicoreJobStatus = await self._unicore_service.get_job_status(job_id)
        while job_status.is_queued:
            logger.debug(f"Waiting for jobs status... current status={job_status.status}")
            await sleep(3)
            job_status = await self._unicore_service.get_job_status(job_id)

        await self._unicore_service.update_job_model(job_id, job_status.status)
        await progress_notifier.log(f"Job status = {job_status}")

        hostname_file = await self._unicore_service.download_file(job_id, "hostname")
        hostname = await hostname_file.text()

        while hostname == "":
            logger.debug(f"Waiting for the hostname file... response={hostname_file.status}")
            await sleep(3)
            hostname_file = await self._unicore_service.download_file(job_id, "hostname")
            hostname = await hostname_file.text()

        logger.debug(f"Got hostname = {hostname}")
        await progress_notifier.log(f"Hostname = {hostname}")

        stdout = await self._unicore_service.download_file(job_id, "stdout")
        stdout_text = await stdout.text()
        logger.debug(f"StdOut: {stdout_text}")
        await progress_notifier.log(f"Stdout: {stdout_text}")
        allocation = await Allocation.create_new_allocation_model(
            job_id=job_id,
            status=job_status.status,
            hostname=hostname,
            stdout=stdout_text,
            port=5000,
        )
        return allocation

    def get_startup_script(self):
        return self.DEFAULT_BRAYNS_STARTUP_SCRIPT

    async def abort_job(self, job_id: UUID):
        await self._unicore_service.abort_job(job_id)
        await self._unicore_service.delete_job(job_id)
        logger.debug(f"Abort job = {job_id}")

    async def abort_all_jobs(self):
        for job_id in await self._unicore_service.get_jobs():
            await self.abort_job(job_id)
