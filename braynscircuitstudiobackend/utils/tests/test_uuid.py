from uuid import UUID

from utils.uuid import extract_uuid_from_text


def test_extract_uuid_from_text():
    assert extract_uuid_from_text("b0d59816-f4d1-4949-a38d-6d558cc2d342") == UUID(
        "b0d59816-f4d1-4949-a38d-6d558cc2d342"
    )

    assert extract_uuid_from_text(
        "https://bbpunicore.epfl.ch:8080/BB5-CSCS/rest/core/jobs/0c048254-4a54-4085-85b3-a2727d865fa0"
    ) == UUID("0c048254-4a54-4085-85b3-a2727d865fa0")

    assert extract_uuid_from_text(
        "some-string-0c048254-4a54-4085-85b3-a2727d865fa0-that-contains-uuid"
    ) == UUID("0c048254-4a54-4085-85b3-a2727d865fa0")

    assert extract_uuid_from_text("this-string-has-no-uuid") is None
