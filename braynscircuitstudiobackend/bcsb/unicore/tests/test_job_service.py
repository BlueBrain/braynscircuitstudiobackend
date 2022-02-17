from datetime import datetime
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock

import pytest
from pytest_mock import MockerFixture
from pytz import UTC

from bcsb.unicore.job_service import (
    UnicoreJobStatus,
    UnicoreJob,
    JobService,
)
from bcsb.unicore.unicore_service import UnicoreService, ClientResponse

MOCK_JOB_LIST_RESPONSE = {
    "_links": {
        "self": {"href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs?offset=0&num=200"}
    },
    "jobs": [
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/e57c4fe1-f9dc-4b67-830f-375594b7d73c",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/31fc04e5-4d78-4d66-b377-0b348262866a",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/31a580c5-7d48-41d6-bcd2-3cc3dcef330b",
    ],
}


@pytest.fixture
def job_service(unicore_service: UnicoreService):
    return JobService(unicore_service=unicore_service)


@pytest.mark.asyncio
async def test_get_jobs(mocker, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.OK
    mock_response.json.return_value = MOCK_JOB_LIST_RESPONSE
    mock_get: MagicMock = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.http_get_unicore",
        return_value=mock_response,
    )
    jobs = await job_service.get_jobs()
    assert len(jobs) == 3
    assert all(isinstance(job, UnicoreJob) for job in jobs)

    job: UnicoreJob = jobs[2]
    assert job.job_id == "31a580c5-7d48-41d6-bcd2-3cc3dcef330b"
    assert str(job) == "Unicore Job 31a580c5-7d48-41d6-bcd2-3cc3dcef330b"


@pytest.mark.asyncio
async def test_create_job(mocker, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.CREATED
    mock_response.json.return_value = ""
    mock_response.headers = {
        "Location": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/31a580c5-7d48-41d6-bcd2-3cc3dcef330b"
    }

    mock_post = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.http_post_unicore",
        return_value=mock_response,
    )

    unicore_job = await job_service.create_job(
        project="proj3",
        name="My Visualization",
        memory="128G",
        runtime="4h",
    )

    mock_post.assert_called()

    assert unicore_job.job_id == "31a580c5-7d48-41d6-bcd2-3cc3dcef330b"


MOCK_JOB_RESPONSE = {
    "owner": "CN=naskret, O=Ecole polytechnique federale de Lausanne (EPFL), L=Lausanne, ST=Vaud, C=CH",
    "submissionPreferences": {"UC_OAUTH_BEARER_TOKEN": ["ey...JQ"]},
    "log": [
        "Mon Jan 24 16:07:26 CET 2022: Created with ID fb82eb95-04eb-4fca-9b7e-2650c499ca45",
        "Mon Jan 24 16:07:26 CET 2022: Created with type 'JSDL'",
        "Mon Jan 24 16:07:26 CET 2022: Client: Name: CN=naskret,O=Ecole polytechnique federale de Lausanne (EPFL),L=Lausanne,ST=Vaud,C=CH\nXlogin: uid: [naskret], gids: [addingOSgroups: true]\nRole: user: role from attribute source\nSecurity tokens: User name: CN=naskret,O=Ecole polytechnique federale de Lausanne (EPFL),L=Lausanne,ST=Vaud,C=CH\nDelegation to consignor status: true, core delegation status: false\nMessage signature status: UNCHECKED\nClient's original IP: 128.179.254.207",
        "Mon Jan 24 16:07:27 CET 2022: Using default execution environment.",
        "Mon Jan 24 16:07:27 CET 2022: No staging in needed.",
        "Mon Jan 24 16:07:27 CET 2022: Status set to READY.",
        "Mon Jan 24 16:07:27 CET 2022: Status set to PENDING.",
        "Mon Jan 24 16:07:27 CET 2022: No application to execute, changing action status to POSTPROCESSING",
        "Mon Jan 24 16:07:27 CET 2022: Status set to DONE.",
        "Mon Jan 24 16:07:27 CET 2022: Result: Success.",
        "Mon Jan 24 16:07:27 CET 2022: Total: 0.28 sec., Stage-in: 0.00 sec., Stage-out: 0.00 sec., Datamovement: 1 %",
    ],
    "_links": {
        "action:start": {
            "description": "Start",
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/start",
        },
        "action:restart": {
            "description": "Restart",
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/restart",
        },
        "workingDirectory": {
            "description": "Working directory",
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/storages/fb82eb95-04eb-4fca-9b7e-2650c499ca45-uspace",
        },
        "self": {
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45"
        },
        "action:abort": {
            "description": "Abort",
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/abort",
        },
        "parentTSS": {
            "description": "Parent TSS",
            "href": "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/sites/800e4953-0c70-4e86-a331-c8515f463df1",
        },
    },
    "acl": [],
    "submissionTime": "2022-01-24T16:07:27+0100",
    "statusMessage": "",
    "tags": [],
    "currentTime": "2022-01-24T16:07:48+0100",
    "resourceStatus": "READY",
    "terminationTime": "2022-02-23T16:07:26+0100",
    "name": "UNICORE_Job",
    "queue": "N/A",
    "status": "SUCCESSFUL",
}


@pytest.mark.asyncio
async def test_get_job_status(mocker, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.OK
    mock_response.json.return_value = MOCK_JOB_RESPONSE
    mock_get: MagicMock = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.http_get_unicore",
        return_value=mock_response,
    )

    job_status = await job_service.get_job_status("fb82eb95-04eb-4fca-9b7e-2650c499ca45")
    mock_get.assert_called_once()

    assert isinstance(job_status, UnicoreJobStatus)

    assert job_status.status == "SUCCESSFUL"
    assert job_status.is_successful
    assert not job_status.is_queued
    assert not job_status.is_running

    # Original time was +0100 but we can check it using UTC reference by subtracting 1 hour
    assert job_status.current_time == datetime(2022, 1, 24, 15, 7, 48, tzinfo=UTC)
    assert job_status.submission_time == datetime(2022, 1, 24, 15, 7, 27, tzinfo=UTC)


@pytest.mark.asyncio
def test_get_unicore_file_url(job_service: JobService):
    assert (
        job_service.get_unicore_file_url("fb82eb95-04eb-4fca-9b7e-2650c499ca45", "hostname").url
        == "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/storages/fb82eb95-04eb-4fca-9b7e-2650c499ca45-uspace/files/hostname"
    )


@pytest.mark.asyncio
async def test_download_file(mocker: MockerFixture, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.__aenter__.return_value.status = HTTPStatus.OK
    mock_response.__aenter__.return_value.content.read.return_value = b"Hello there"

    mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.make_unicore_http_request",
        return_value=mock_response,
    )

    mock_get_response = AsyncMock(ClientResponse)
    mock_get_response.status = HTTPStatus.OK
    mock_get_response.json.return_value = {}
    mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.http_get_unicore",
        return_value=mock_get_response,
    )

    job = await job_service.get_job("fb82eb95-04eb-4fca-9b7e-2650c499ca45")

    async with await job.download_file("my_file.txt") as job_file_response:
        assert job_file_response.status == HTTPStatus.OK
        file_content = await job_file_response.content.read()

    assert file_content == b"Hello there"


@pytest.mark.asyncio
async def test_upload_text_file(mocker: MockerFixture, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.NO_CONTENT
    mock_http_request = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.make_unicore_http_request",
        return_value=mock_response,
    )

    job = await job_service.get_job("fb82eb95-04eb-4fca-9b7e-2650c499ca45", check_exists=False)
    response = await job.upload_text_file("my_file.txt", "Hello")
    extra_headers = {
        "Accept": "application/octet-stream",
        "Content-Type": "text/plain",
    }

    mock_http_request.assert_called_once_with(
        "put",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/storages/fb82eb95-04eb-4fca-9b7e-2650c499ca45-uspace/files/my_file.txt",
        extra_headers=extra_headers,
    )

    assert response.status == HTTPStatus.NO_CONTENT


@pytest.mark.asyncio
async def test_start_job(mocker: MockerFixture, job_service: JobService):
    mock_response = AsyncMock(ClientResponse)
    mock_response.status = HTTPStatus.NO_CONTENT
    mock_http_request = mocker.patch(
        "bcsb.unicore.unicore_service.UnicoreService.make_unicore_http_request",
        return_value=mock_response,
    )

    job = await job_service.get_job("fb82eb95-04eb-4fca-9b7e-2650c499ca45", check_exists=False)
    await job.start()

    mock_http_request.assert_called_once_with(
        "post",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/start",
        None,
    )

    mock_http_request.reset_mock()

    await job.restart()

    mock_http_request.assert_called_once_with(
        "post",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/restart",
        None,
    )
    mock_http_request.reset_mock()

    await job.abort()

    mock_http_request.assert_called_once_with(
        "post",
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/fb82eb95-04eb-4fca-9b7e-2650c499ca45/actions/abort",
        None,
    )
    mock_http_request.reset_mock()
