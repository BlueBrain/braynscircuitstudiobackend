import logging
from datetime import datetime
from http import HTTPStatus
from typing import List

from aiohttp import ClientResponse
from furl import furl
from pydash import get

from bcsb.unicore.schemas import (
    CreateJobSchema,
    dump_schema,
    JobStatusResponseSchema,
    load_schema,
    JobListResponseSchema,
)
from bcsb.unicore.unicore_service import UnicoreService
from utils.strings import equals_ignoring_case
from utils.uuid import UUID_LENGTH, extract_uuid_from_text

logger = logging.getLogger(__name__)


START = "start"
ABORT = "abort"
RESTART = "restart"
JOB_ACTIONS = {START, ABORT, RESTART}


class JobService:
    def __init__(self, unicore_service: UnicoreService):
        self._unicore_service = unicore_service

    def _get_job_id_from_create_job_response(self, response: ClientResponse):
        # https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/b7c5c49a-078e-4b2a-ac4d-0def93b70635
        location_url = response.headers["Location"]
        job_uuid = extract_uuid_from_text(location_url)
        assert isinstance(job_uuid, str) and len(job_uuid) == UUID_LENGTH
        return job_uuid

    async def get_jobs(self) -> List["UnicoreJob"]:
        response = await self._unicore_service.http_get_unicore("/jobs")
        assert response.status == HTTPStatus.OK
        schema = load_schema(JobListResponseSchema, await response.json())
        return [
            UnicoreJob(
                self,
                extract_uuid_from_text(job_url),
            )
            for job_url in get(schema, "jobs", [])
        ]

    async def get_job(self, job_id: str, check_exists: bool = True) -> "UnicoreJob":
        job = UnicoreJob(self, job_id)
        if check_exists:
            await job.get_current_status()
        return job

    async def create_job(
        self,
        project: str,
        name: str,
        have_clients_stage_in: bool = True,
        queue: str = "prod",
        nodes: int = 1,
        cpus_per_node: int = 72,
        runtime: str = "8h",
        node_constraints: str = "cpu",
        memory: str = "128G",
        tags: List[str] = None,
        exclusive: bool = True,
    ) -> "UnicoreJob":
        tags = tags or ["visualization"]
        payload = dump_schema(
            CreateJobSchema,
            {
                "project": project,
                "name": name,
                "have_client_stage_in": have_clients_stage_in,
                "tags": tags,
                "resources": {
                    "queue": queue,
                    "nodes": nodes,
                    "cpus_per_node": cpus_per_node,
                    "runtime": runtime,
                    "node_constraints": node_constraints,
                    "memory": memory,
                    "exclusive": exclusive,
                },
            },
        )
        response = await self._unicore_service.http_post_unicore("/jobs", payload=payload)
        assert (
            response.status == HTTPStatus.CREATED
        ), f"Unexpected response status: {response.status}"
        job_id = self._get_job_id_from_create_job_response(response)
        return UnicoreJob(self, job_id)

    async def get_job_status(self, job_id: str):
        response = await self._unicore_service.http_get_unicore(f"jobs/{job_id}")
        assert response.status == HTTPStatus.OK, f"Unexpected response status: {response.status}"
        logger.debug("Job status")
        return UnicoreJobStatus(await response.json())

    def get_unicore_file_url(self, job_id: str, file_path: str) -> furl:
        url = self._unicore_service.get_unicore_furl()
        url /= f"/storages/{job_id}-uspace/files/"
        url /= file_path
        return url

    async def download_file(self, job_id: str, file_path: str):
        file_url = self.get_unicore_file_url(job_id, file_path)
        download_file_headers = {
            "Accept": "application/octet-stream",
        }
        response = await self._unicore_service.make_unicore_http_request(
            "get", file_url.url, extra_headers=download_file_headers
        )
        return response

    async def upload_text_file(self, job_id: str, file_path: str, text_content: str):
        file_url = self.get_unicore_file_url(job_id, file_path)
        upload_file_headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "text/plain",
        }
        response = await self._unicore_service.make_unicore_http_request(
            "put", file_url.url, extra_headers=upload_file_headers
        )
        assert (
            response.status == HTTPStatus.NO_CONTENT
        ), f"Unexpected response status: {response.status}"
        return response

    def _get_job_action_url(self, job_id: str, action: str):
        url = self._unicore_service.get_unicore_furl()
        assert action in JOB_ACTIONS
        url /= f"jobs/{job_id}/actions/{action}"
        return url

    async def _run_job_action(self, job_id, action: str):
        return await self._unicore_service.http_post_unicore(
            self._get_job_action_url(job_id, action).url
        )

    async def start_job(self, job_id: str):
        return await self._run_job_action(job_id, START)

    async def abort_job(self, job_id: str):
        return await self._run_job_action(job_id, ABORT)

    async def restart_job(self, job_id: str):
        return await self._run_job_action(job_id, RESTART)


class UnicoreJob:
    _job_service: JobService

    def __init__(self, job_service: JobService, job_id):
        self._job_service = job_service
        self.job_id = job_id

    def __repr__(self):
        return f"Unicore Job {self.job_id}"

    async def start(self):
        return await self._job_service.start_job(job_id=self.job_id)

    async def restart(self):
        return await self._job_service.restart_job(job_id=self.job_id)

    async def abort(self):
        return await self._job_service.abort_job(job_id=self.job_id)

    async def get_current_status(self) -> "UnicoreJobStatus":
        return await self._job_service.get_job_status(job_id=self.job_id)

    async def download_file(self, file_path: str):
        return await self._job_service.download_file(self.job_id, file_path=file_path)

    async def upload_text_file(self, filename: str, content: str):
        return await self._job_service.upload_text_file(
            job_id=self.job_id, file_path=filename, text_content=content
        )


class UnicoreJobStatus:
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"

    def __init__(self, raw_data: dict):
        self._response_schema = load_schema(JobStatusResponseSchema, raw_data)

    @property
    def status(self):
        return get(self._response_schema, "status")

    @property
    def is_queued(self):
        return equals_ignoring_case(self.status, self.QUEUED)

    @property
    def is_successful(self):
        return equals_ignoring_case(self.status, self.SUCCESSFUL)

    @property
    def is_running(self):
        return equals_ignoring_case(self.status, self.RUNNING)

    @property
    def current_time(self) -> datetime:
        return get(self._response_schema, "current_time")

    @property
    def submission_time(self) -> datetime:
        return get(self._response_schema, "submission_time")
