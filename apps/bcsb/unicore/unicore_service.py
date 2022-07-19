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

from bcsb.sessions.models import Session
from bcsb.unicore.models import UnicoreJob
from bcsb.unicore.schemas import (
    CreateJobSchema,
    JobStatusResponseSchema,
    JobListResponseSchema,
    UnicoreStorageResponseSchema,
)
from common.utils.schemas import load_schema, dump_schema
from common.utils.strings import equals_ignoring_case
from common.utils.uuid import extract_uuid_from_text

logger = logging.getLogger(__name__)

START = "start"
ABORT = "abort"
RESTART = "restart"
JOB_ACTIONS = {START, ABORT, RESTART}
DEFAULT_COMMENT = "certs"


class UnicoreService:
    GPFS_STORAGE_BASE_PATH = "/storages/gpfs/files/"
    ALLOWED_HTTP_METHODS = ("post", "get", "put", "delete")
    DEFAULT_STARTUP_SCRIPT_FILENAME = "start.sh"
    _token: str = None

    def __init__(self, token: str = None):
        self.set_token(token)

    def get_startup_script_filename(self) -> str:
        return self.DEFAULT_STARTUP_SCRIPT_FILENAME

    def set_token(self, token: str):
        self._token = token

    def get_unicore_request_headers(self, extra_headers: dict = None):
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    @staticmethod
    def get_unicore_furl() -> furl:
        url = furl(settings.BBP_UNICORE_URL)
        url /= settings.BBP_UNICORE_CORE_PATH
        return url

    def get_endpoint_furl(self, endpoint: str) -> furl:
        return self.get_unicore_furl() / endpoint

    async def make_unicore_http_request(
        self,
        http_method_name: str,
        path: str,
        json_payload=None,
        data_payload=None,
        extra_headers: dict = None,
    ) -> ClientResponse:
        url: furl = self.get_endpoint_furl(path)
        logger.debug(f"Make Unicore {http_method_name.upper()} request: {url.url}")
        request_headers = self.get_unicore_request_headers(extra_headers)
        assert http_method_name.lower() in self.ALLOWED_HTTP_METHODS
        async with ClientSession() as client_session:
            method = getattr(client_session, http_method_name)
            async with method(
                url.url,
                headers=request_headers,
                json=json_payload,
                data=data_payload,
            ) as response:
                response: ClientResponse
                logger.debug(f"Response status: {response.status}")
                await response.read()
        return response

    async def http_get_unicore(self, endpoint: str) -> ClientResponse:
        return await self.make_unicore_http_request(
            "get",
            endpoint,
        )

    async def http_post_unicore(self, endpoint: str, json_payload=None) -> ClientResponse:
        return await self.make_unicore_http_request(
            "post",
            endpoint,
            json_payload=json_payload,
        )

    async def http_delete_unicore(self, endpoint: str) -> ClientResponse:
        return await self.make_unicore_http_request("delete", endpoint)

    @staticmethod
    def _get_job_id_from_create_job_response(response: ClientResponse) -> UUID:
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
        session: Session,
        project: str,
        name: str,
        have_clients_stage_in: bool = True,
        queue: str = "prod",
        nodes: int = 1,
        runtime: str = "8h",
        node_constraints: str = "cpu",
        memory: str = "0",
        comment: str = None,
        tags: List[str] = None,
        exclusive: bool = True,
    ) -> UUID:
        tags = tags or ["visualization"]
        comment = comment or DEFAULT_COMMENT
        payload = dump_schema(
            CreateJobSchema,
            {
                "project": project,
                "name": name,
                "have_client_stage_in": have_clients_stage_in,
                "tags": tags,
                "executable": self.get_executable_command(),
                "resources": {
                    "queue": queue,
                    "nodes": nodes,
                    "runtime": runtime,
                    "node_constraints": node_constraints,
                    "memory": memory,
                    "exclusive": exclusive,
                    "comment": comment,
                },
            },
        )
        response = await self.http_post_unicore("/jobs", json_payload=payload)
        assert (
            response.status == HTTPStatus.CREATED
        ), f"Unexpected response status: {response.status}"
        job_id = self._get_job_id_from_create_job_response(response)
        await self._create_job_model(session=session, job_id=job_id)
        return job_id

    def get_executable_command(self):
        return f"""#!/bin/bash
        sh {self.get_startup_script_filename()}
        """

    async def _create_job_model(self, job_id, session: Session):
        return await UnicoreJob.create_from_job_id(
            session=session,
            job_id=job_id,
            token=self._token,
            status=UnicoreJobStatus.UNKNOWN,
        )

    @staticmethod
    async def update_job_model(job_id, status: str):
        return await UnicoreJob.update_job(job_id, status=status)

    async def get_job_status(self, job_id: UUID) -> "UnicoreJobStatus":
        response = await self.http_get_unicore(f"/jobs/{job_id}")
        assert response.status == HTTPStatus.OK, f"Unexpected response status: {response.status}"
        return UnicoreJobStatus(await response.json())

    @staticmethod
    def get_file_url_path(job_id: UUID, filepath: str) -> furl:
        if not isinstance(filepath, str):
            raise ValueError(f"Unexpectedly filepath was: {type(filepath)}")
        url = furl(f"/storages/{job_id}-uspace/files/")
        url /= filepath
        return url

    async def download_file(self, job_id: UUID, filepath: str):
        file_url = self.get_file_url_path(job_id, filepath)
        download_file_headers = {
            "Accept": "application/octet-stream",
        }
        response = await self.make_unicore_http_request(
            "get", file_url.url, extra_headers=download_file_headers
        )
        return response

    async def upload_text_file(self, job_id: UUID, filepath: str, text_content: str):
        file_url = self.get_file_url_path(job_id, filepath)
        upload_file_headers = {
            "Accept": "application/octet-stream",
            "Content-Type": "text/plain",
        }
        response = await self.make_unicore_http_request(
            "put",
            file_url.url,
            extra_headers=upload_file_headers,
            data_payload=text_content,
        )
        assert (
            response.status == HTTPStatus.NO_CONTENT
        ), f"Unexpected response status: {response.status}"
        return response

    async def upload_startup_script_file(self, job_id: UUID, text_content: str):
        """
        Here you can pass the contents of the script that will be run in the first row by Unicore
        when starting the job.
        """
        return await self.upload_text_file(
            job_id=job_id,
            text_content=text_content,
            filepath=self.get_startup_script_filename(),
        )

    @staticmethod
    def _get_job_action_furl(job_id: UUID, action: str) -> furl:
        assert action in JOB_ACTIONS
        url = furl(f"/jobs/{job_id}/actions/{action}")
        return url

    @staticmethod
    def _get_job_furl(job_id: UUID) -> furl:
        return furl(f"/jobs/{job_id}")

    async def _run_job_action(self, job_id: UUID, action: str):
        return await self.http_post_unicore(
            self._get_job_action_furl(job_id, action).url,
            json_payload={},
        )

    async def start_job(self, job_id: UUID):
        return await self._run_job_action(job_id, START)

    async def abort_job(self, job_id: UUID):
        return await self._run_job_action(job_id, ABORT)

    async def restart_job(self, job_id: UUID):
        return await self._run_job_action(job_id, RESTART)

    async def delete_job(self, job_id: UUID):
        return await self.http_delete_unicore(self._get_job_furl(job_id=job_id).url)

    def _get_gpfs_storage_furl(self, path: str) -> furl:
        url = furl(self.GPFS_STORAGE_BASE_PATH)
        url /= path
        return url

    async def list_gpfs_storage(self, path: str):
        response = await self.http_get_unicore(self._get_gpfs_storage_furl(path).url)

        return load_schema(
            UnicoreStorageResponseSchema,
            await response.json(),
        )


class UnicoreJobStatus:
    UNKNOWN = "UNKNOWN"
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
