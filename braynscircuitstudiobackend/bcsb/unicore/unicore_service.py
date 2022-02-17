import logging
from datetime import datetime
from http import HTTPStatus
from typing import List
from uuid import UUID

from aiohttp import ClientResponse
from aiohttp import ClientSession
from django.conf import settings
from furl import furl
from pydash import get

from bcsb.unicore.schemas import (
    CreateJobSchema,
    dump_schema,
    JobStatusResponseSchema,
    load_schema,
    JobListResponseSchema,
)
from utils.strings import equals_ignoring_case
from utils.uuid import extract_uuid_from_text

START = "start"
ABORT = "abort"
RESTART = "restart"
JOB_ACTIONS = {START, ABORT, RESTART}


logger = logging.getLogger(__name__)


class UnicoreService:
    _token: str = None

    def __init__(self, token: str = None):
        self.set_token(token)

    def set_token(self, token: str):
        self._token = token

    async def get_unicore_request_headers(self, extra_headers: dict = None):
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def get_unicore_furl(self) -> furl:
        url = furl(settings.BBP_UNICORE_URL)
        url /= settings.BBP_UNICORE_CORE_PATH
        return url

    def get_unicore_endpoint_furl(self, endpoint: str) -> furl:
        return self.get_unicore_furl() / endpoint

    async def make_unicore_http_request(
        self,
        http_method_name: str,
        path: str,
        payload=None,
        extra_headers: dict = None,
    ) -> ClientResponse:
        url: furl = self.get_unicore_endpoint_furl(path)
        request_headers = await self.get_unicore_request_headers(extra_headers)
        async with ClientSession() as session:
            assert http_method_name.lower() in ("post", "get", "put")
            method = getattr(session, http_method_name)
            response = await method(
                url.url,
                headers=request_headers,
                data=payload,
            )
        return response

    async def http_get_unicore(self, endpoint: str) -> ClientResponse:
        return await self.make_unicore_http_request(
            "get",
            endpoint,
        )

    async def http_post_unicore(self, endpoint: str, payload=None) -> ClientResponse:
        return await self.make_unicore_http_request(
            "post",
            endpoint,
            payload,
        )

    def _get_job_id_from_create_job_response(self, response: ClientResponse):
        # https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/b7c5c49a-078e-4b2a-ac4d-0def93b70635
        location_url = response.headers["Location"]
        job_uuid = extract_uuid_from_text(location_url)
        assert isinstance(job_uuid, UUID)
        return job_uuid

    async def get_jobs(self) -> List[UUID]:
        response = await self.http_get_unicore("/jobs")
        assert response.status == HTTPStatus.OK
        schema = load_schema(JobListResponseSchema, await response.json())
        return [extract_uuid_from_text(job_url) for job_url in get(schema, "jobs", [])]

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
    ) -> UUID:
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
        response = await self.http_post_unicore("/jobs", payload=payload)
        assert (
            response.status == HTTPStatus.CREATED
        ), f"Unexpected response status: {response.status}"
        job_id = self._get_job_id_from_create_job_response(response)
        return job_id

    async def get_job_status(self, job_id: UUID):
        response = await self.http_get_unicore(f"jobs/{job_id}")
        assert response.status == HTTPStatus.OK, f"Unexpected response status: {response.status}"
        logger.debug("Job status")
        return UnicoreJobStatus(await response.json())

    def get_unicore_file_url(self, job_id: UUID, file_path: str) -> furl:
        url = self.get_unicore_furl()
        url /= f"/storages/{job_id}-uspace/files/"
        url /= file_path
        return url

    async def download_file(self, job_id: UUID, file_path: str):
        file_url = self.get_unicore_file_url(job_id, file_path)
        download_file_headers = {
            "Accept": "application/octet-stream",
        }
        response = await self.make_unicore_http_request(
            "get", file_url.url, extra_headers=download_file_headers
        )
        return response

    async def upload_text_file(self, job_id: UUID, file_path: str, text_content: str):
        file_url = self.get_unicore_file_url(job_id, file_path)
        upload_file_headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "text/plain",
        }
        response = await self.make_unicore_http_request(
            "put", file_url.url, extra_headers=upload_file_headers
        )
        assert (
            response.status == HTTPStatus.NO_CONTENT
        ), f"Unexpected response status: {response.status}"
        return response

    def _get_job_action_url(self, job_id: UUID, action: str):
        url = self.get_unicore_furl()
        assert action in JOB_ACTIONS
        url /= f"jobs/{job_id}/actions/{action}"
        return url

    async def _run_job_action(self, job_id: UUID, action: str):
        return await self.http_post_unicore(self._get_job_action_url(job_id, action).url)

    async def start_job(self, job_id: UUID):
        return await self._run_job_action(job_id, START)

    async def abort_job(self, job_id: UUID):
        return await self._run_job_action(job_id, ABORT)

    async def restart_job(self, job_id: UUID):
        return await self._run_job_action(job_id, RESTART)


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
