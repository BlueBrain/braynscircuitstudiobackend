from http import HTTPStatus
from typing import List

from aiohttp import ClientResponse

from unicore.jobs import UnicoreJob
from unicore.schemas import CreateJobSchema
from unicore.unicore_service import http_get_unicore, dump_schema, http_post_unicore
from utils.uuid import UUID_LENGTH, extract_uuid_from_text


def _get_job_id_from_create_job_response(response: ClientResponse):
    # https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/b7c5c49a-078e-4b2a-ac4d-0def93b70635
    location_url = response.headers["Location"]
    job_uuid = extract_uuid_from_text(location_url)
    assert isinstance(job_uuid, str) and len(job_uuid) == UUID_LENGTH
    return job_uuid


async def get_jobs():
    json_data = await http_get_unicore("/jobs")
    print(await json_data.json())


async def create_job(
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
) -> UnicoreJob:
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
    response = await http_post_unicore("/jobs", payload=payload)
    assert response.status == HTTPStatus.CREATED
    job_id = _get_job_id_from_create_job_response(response)
    return UnicoreJob(job_id)


async def upload_file():
    raise NotImplementedError


async def start_job():
    raise NotImplementedError


async def abort_job():
    raise NotImplementedError


async def restart_job():
    raise NotImplementedError
