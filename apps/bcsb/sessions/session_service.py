import logging
from asyncio import sleep
from uuid import UUID

from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.sessions.default_scripts import (
    NODE_HOSTNAME_FILENAME,
    BCSS_STARTUP_SCRIPT_FILEPATH,
    BRAYNS_STARTUP_SCRIPT_FILEPATH,
    get_bcss_startup_script,
    get_brayns_startup_script,
    get_main_startup_script,
)
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
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
    unicore_service: UnicoreService
    session: Session

    def __init__(self, unicore_service: UnicoreService, session_instance: Session = None):
        self.session = session_instance
        self.unicore_service = unicore_service

    @property
    def user(self):
        return self.session.user

    async def start(self, progress_notifier, project: str):
        logger.debug("Starting Brayns...")
        await progress_notifier.log(f"Starting Brayns session ({self.session.session_uid})")

        # Here we create and start the job with all the scripts etc.
        job_id = await self.create_and_start_session_job(
            project=project,
        )
        await progress_notifier.log(f"Registered new job = {job_id}")

        # Then, we check the status of the job until it's ready to use
        allocation = await self.report_job_ready(job_id, progress_notifier)

        return allocation

    async def report_job_ready(
        self, job_id: UUID, progress_notifier: ProgressNotifier
    ) -> Allocation:
        job_status: UnicoreJobStatus = await self.unicore_service.get_job_status(job_id)
        while job_status.is_queued:
            logger.debug(f"Waiting for jobs status... current status={job_status.status}")
            await sleep(3)
            job_status = await self.unicore_service.get_job_status(job_id)

        await self.unicore_service.update_job_model(job_id, job_status.status)
        await progress_notifier.log(f"Job status = {job_status}")

        # Here we expect to get the hostname of the node
        hostname_file = await self.unicore_service.download_file(job_id, NODE_HOSTNAME_FILENAME)
        hostname = await hostname_file.text()

        while hostname == "":
            logger.debug(
                f"Waiting for the hostname file ({NODE_HOSTNAME_FILENAME})... response={hostname_file.status}"
            )
            await sleep(3)
            hostname_file = await self.unicore_service.download_file(job_id, NODE_HOSTNAME_FILENAME)
            hostname = await hostname_file.text()

        hostname = hostname.replace("\n", "")

        logger.debug(f"Got hostname = {hostname}")
        await progress_notifier.log(f"Hostname = {hostname}")

        stdout = await self.unicore_service.download_file(job_id, "stdout")
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

        # TODO we should check whether Brayns and BCSS are running on given ports (WS connection)

        return allocation

    async def create_and_start_session_job(
        self,
        project: str,
    ):
        """
        Starting a job comprises running several scripts:

        1. Unicore raw script that runs the startup script
        2. We upload a startup script and set its contents to get_main_startup_script_content() result
        3. We upload application-related scripts to run both Brayns and BCSS

        UNICORE COMMAND --> RUNS A STARTUP SCRIPT --> RUNS APPLICATION SCRIPTS
        """
        job_id = await self.unicore_service.create_job(
            session=self.session,
            project=project,
            name="Circuit visualization",
            memory="0",
            runtime="8h",
            exclusive=True,
        )

        # Upload scripts that will start Brayns and BCSS
        brayns_startup_script = self.get_brayns_startup_script_content()
        logger.debug(f"Brayns startup script:\n{brayns_startup_script}")
        await self.unicore_service.upload_text_file(
            job_id=job_id,
            filepath=BRAYNS_STARTUP_SCRIPT_FILEPATH,
            text_content=brayns_startup_script,
        )

        bcss_startup_script = self.get_bcss_startup_script_content()
        logger.debug(f"BCSS startup script:\n{bcss_startup_script}")
        await self.unicore_service.upload_text_file(
            job_id=job_id,
            filepath=BCSS_STARTUP_SCRIPT_FILEPATH,
            text_content=bcss_startup_script,
        )

        # Upload the final startup script that will run them all
        main_startup_script = self.get_main_startup_script_content()
        logger.debug(f"Main startup script:\n{main_startup_script}")
        await self.unicore_service.upload_startup_script_file(
            job_id=job_id,
            text_content=main_startup_script,
        )

        # Finally, actually start the created job
        await self.unicore_service.start_job(job_id=job_id)

        return job_id

    async def abort_job(self, job_id: UUID) -> None:
        await self.unicore_service.abort_job(job_id)
        await self.unicore_service.delete_job(job_id)
        logger.debug(f"Abort job = {job_id}")

    async def abort_all_jobs(self) -> None:
        for job_id in await self.unicore_service.get_jobs():
            await self.abort_job(job_id)

    @staticmethod
    def get_main_startup_script_content() -> str:
        return get_main_startup_script()

    @staticmethod
    def get_brayns_startup_script_content() -> str:
        # TODO tls paths should be retrieved from the Unicore job
        return get_brayns_startup_script(
            tls_key_filepath="",
            tls_cert_filepath="",
        )

    @staticmethod
    def get_bcss_startup_script_content() -> str:
        # TODO tls paths should be retrieved from the Unicore job
        return get_bcss_startup_script(
            tls_key_filepath="",
            tls_cert_filepath="",
        )
