import logging
import re
from asyncio import sleep
from typing import Optional

from channels.db import database_sync_to_async
from django.contrib.auth.models import User

from bcsb.allocations.models import Allocation
from bcsb.sessions.default_scripts import (
    BCSS_STARTUP_SCRIPT_FILEPATH,
    BRAYNS_STARTUP_SCRIPT_FILEPATH,
    get_bcss_startup_script,
    get_brayns_startup_script,
    get_main_startup_script,
)
from bcsb.sessions.models import Session
from bcsb.sessions.progress_notifier import ProgressNotifier
from bcsb.unicore.typing import UnicoreJobId
from bcsb.unicore.unicore_service import UnicoreService, UnicoreJobStatus

logger = logging.getLogger(__name__)


@database_sync_to_async
def make_new_session(user: User) -> Session:
    session = Session(user=user)
    session.save()
    return session


async def make_session_service(
    user: User,
    token: str,
    session_instance: Session = None,
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

    async def start(
        self,
        progress_notifier: ProgressNotifier,
        project: str,
    ):
        """
        Starting a job comprises running several scripts:

        1. Unicore raw script that runs the startup script
        2. We upload a startup script and set its contents to get_main_startup_script_content() result
        3. We upload application-related scripts to run both Brayns and BCSS

        UNICORE COMMAND --> RUNS A STARTUP SCRIPT --> RUNS APPLICATION SCRIPTS
        """
        logger.debug("Starting Brayns...")
        await progress_notifier.log(f"Starting Brayns session ({self.session.session_uid})")

        # Create a job with all necessary scripts and settings
        job_id: UnicoreJobId = await self.prepare_session_job(project=project)
        await progress_notifier.log(f"Registered new job = {job_id}")

        allocation = await self.create_new_allocation(
            job_id=job_id,
            project=project,
        )

        # Tell Unicore to actually start the job
        await self.unicore_service.start_job(job_id=job_id)

        # Check the status of the job until it's ready to use
        await self.report_job_ready(
            job_id=job_id,
            progress_notifier=progress_notifier,
            allocation=allocation,
        )

        # Return an Allocation instance once everything is ready to use
        # It's assumed that all required services up and running
        return allocation

    async def create_new_allocation(self, project: str, job_id: UnicoreJobId) -> Allocation:
        allocation = await Allocation.create_new_allocation_model(
            session=self.session,
            unicore_job_id=job_id,
            project=project,
        )
        return allocation

    async def prepare_session_job(self, project: str):
        # Register a new job in Unicore and retrieve the job id
        job_id: UnicoreJobId = await self.unicore_service.create_job(
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

        return job_id

    async def report_job_ready(
        self,
        job_id: UnicoreJobId,
        progress_notifier: ProgressNotifier,
        allocation: Allocation,
    ) -> None:
        job_status: UnicoreJobStatus = await self.unicore_service.get_job_status(job_id)

        while True:
            logger.debug(f"Waiting for jobs status... current status={job_status.status}")
            job_status = await self.unicore_service.get_job_status(job_id)
            if not job_status.is_queued:
                break
            await sleep(3)

        await progress_notifier.log(f"Job status = {job_status.status}")

        # Retrieve the hostname for the allocated node
        await self.update_allocation_envs(allocation)
        await progress_notifier.log(f"Hostname = {allocation.hostname}")

        stdout = await self.unicore_service.download_file(job_id, "stdout")
        stdout_text = await stdout.text()
        logger.debug(f"StdOut: {stdout_text}")
        await progress_notifier.log(f"Stdout: {stdout_text}")
        await allocation.update_stdout(stdout_text)

        stderr = await self.unicore_service.download_file(job_id, "stderr")
        stderr_text = await stderr.text()
        logger.debug(f"StdErr: {stderr_text}")
        await progress_notifier.log(f"Stderr: {stderr_text}")
        await allocation.update_stderr(stderr_text)

        # TODO we should check whether Brayns and BCSS are running on given ports (WS connection)

    async def update_allocation_envs(self, allocation: Allocation) -> None:
        while True:
            stdout = await self.unicore_service.download_file(allocation.unicore_job_id, "stdout")
            stdout_text = await stdout.text()
            hostname = self._get_variable_from_stdout("UNICORE_HOSTNAME", stdout_text)
            brayns_ws_url = self._get_variable_from_stdout("BRAYNS_WS_URL", stdout_text)
            bcss_ws_url = self._get_variable_from_stdout("BCSS_WS_URL", stdout_text)
            if hostname and brayns_ws_url and bcss_ws_url:
                await allocation.update_model(
                    {
                        "hostname": hostname,
                        "brayns_ws_url": brayns_ws_url,
                        "bcss_ws_url": bcss_ws_url,
                        "stdout": stdout_text,
                    }
                )
                break
            await sleep(3)

    @staticmethod
    def _get_variable_from_stdout(variable_name: str, stdout: str) -> Optional[str]:
        match = re.search(rf"^{variable_name}=(?P<{variable_name}>.+)\n", stdout, re.MULTILINE)
        logger.debug(f"Searching for variable in stdout... {variable_name}")
        if match:
            value = match.groupdict()[variable_name]
            logger.debug(f"Got hostname: {value}")
            return value
        return None

    async def abort_job(self, job_id: UnicoreJobId) -> None:
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
        return get_brayns_startup_script(
            tls_key_filepath="$UNICORE_PRIVATE_KEY_FILEPATH",
            tls_cert_filepath="$UNICORE_CERT_FILEPATH",
        )

    @staticmethod
    def get_bcss_startup_script_content() -> str:
        return get_bcss_startup_script(
            tls_key_filepath="$UNICORE_PRIVATE_KEY_FILEPATH",
            tls_cert_filepath="$UNICORE_CERT_FILEPATH",
        )
