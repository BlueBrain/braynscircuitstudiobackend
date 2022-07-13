import logging
from asyncio import sleep
from uuid import UUID

from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.sessions.default_scripts import (
    DEFAULT_BRAYNS_STARTUP_SCRIPT,
    DEFAULT_BCSS_STARTUP_SCRIPT,
    NODE_HOSTNAME_FILENAME,
    DEFAULT_MAIN_STARTUP_SCRIPT,
    BCSS_STARTUP_SCRIPT_FILENAME,
    BRAYNS_STARTUP_SCRIPT_FILENAME,
)
from bcsb.sessions.models import Session
from bcsb.unicore.unicore_service import UnicoreService, UnicoreJobStatus

logger = logging.getLogger(__name__)


@database_sync_to_async
def make_new_session(user: User) -> Session:
    session = Session(user=user)
    session.save()
    return session


async def make_session_service(
    user: User, token: str, session_instance: Session = None
) -> "SessionService":
    if session_instance is None:
        session_instance = await make_new_session(user=user)
    unicore_service = UnicoreService(token=token)
    return SessionService(
        unicore_service=unicore_service,
        session_instance=session_instance,
    )


class SessionService:
    _unicore_service: UnicoreService
    session: Session

    def __init__(self, unicore_service: UnicoreService, session_instance: Session = None):
        self.session = session_instance
        self._unicore_service = unicore_service

    @property
    def user(self):
        return self.session.user

    async def start(self, progress_notifier, project: str):
        logger.debug("Starting Brayns...")
        await progress_notifier.log(f"Starting Brayns session ({self.session.session_uid})")

        job_id = await self._create_and_start_session_job(
            project=project,
        )
        await progress_notifier.log(f"Registered new job = {job_id}")

        job_status: UnicoreJobStatus = await self._unicore_service.get_job_status(job_id)
        while job_status.is_queued:
            logger.debug(f"Waiting for jobs status... current status={job_status.status}")
            await sleep(3)
            job_status = await self._unicore_service.get_job_status(job_id)

        await self._unicore_service.update_job_model(job_id, job_status.status)
        await progress_notifier.log(f"Job status = {job_status}")

        hostname_file = await self._unicore_service.download_file(job_id, NODE_HOSTNAME_FILENAME)
        hostname = await hostname_file.text()

        while hostname == "":
            logger.debug(
                f"Waiting for the hostname file ({NODE_HOSTNAME_FILENAME})... response={hostname_file.status}"
            )
            await sleep(3)
            hostname_file = await self._unicore_service.download_file(
                job_id, NODE_HOSTNAME_FILENAME
            )
            hostname = await hostname_file.text()

        hostname = hostname.replace("\n", "")

        logger.debug(f"Got hostname = {hostname}")
        await progress_notifier.log(f"Hostname = {hostname}")

        stdout = await self._unicore_service.download_file(job_id, "stdout")
        stdout_text = await stdout.text()
        logger.debug(f"StdOut: {stdout_text}")
        await progress_notifier.log(f"Stdout: {stdout_text}")
        allocation = await Allocation.create_new_allocation_model(
            session=self.session,
            job_id=job_id,
            status=job_status.status,
            hostname=hostname,
            stdout=stdout_text,
        )
        return allocation

    async def _create_and_start_session_job(
        self,
        project: str,
    ):
        job_id = await self._unicore_service.create_job(
            session=self.session,
            project=project,
            name="Circuit visualization",
            memory="0",
            runtime="8h",
            exclusive=True,
        )

        # Upload scripts that start Brayns and BCSS
        await self._unicore_service.upload_text_file(
            job_id=job_id,
            file_path=BRAYNS_STARTUP_SCRIPT_FILENAME,
            text_content=self._get_brayns_startup_script_content(),
        )
        await self._unicore_service.upload_text_file(
            job_id=job_id,
            file_path=BCSS_STARTUP_SCRIPT_FILENAME,
            text_content=self._get_bcss_startup_script_content(),
        )

        # Upload the final startup script that will run them all
        await self._unicore_service.upload_text_file(
            job_id=job_id,
            file_path=self._unicore_service.START_SCRIPT_NAME,
            text_content=self._get_main_startup_script_content(),
        )

        # Finally actually start the created job
        await self._unicore_service.start_job(job_id=job_id)

        return job_id

    async def abort_job(self, job_id: UUID) -> None:
        await self._unicore_service.abort_job(job_id)
        await self._unicore_service.delete_job(job_id)
        logger.debug(f"Abort job = {job_id}")

    async def abort_all_jobs(self) -> None:
        for job_id in await self._unicore_service.get_jobs():
            await self.abort_job(job_id)

    def _get_main_startup_script_content(self) -> str:
        return DEFAULT_MAIN_STARTUP_SCRIPT

    def _get_brayns_startup_script_content(self) -> str:
        return DEFAULT_BRAYNS_STARTUP_SCRIPT

    def _get_bcss_startup_script_content(self) -> str:
        return DEFAULT_BCSS_STARTUP_SCRIPT
