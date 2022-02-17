import pytest
from django.contrib.auth.models import User

from bcsb.unicore.unicore_service import UnicoreService


@pytest.fixture
def TEST_TOKEN():
    return "ey--TEST-TOKEN--JhbGci...ldUIiwia"


@pytest.fixture
def unicore_service(TEST_TOKEN: str):
    return UnicoreService(token=TEST_TOKEN)


@pytest.fixture
def mock_user():
    return User(
        id=1,
        username="testuser",
        first_name="John",
        last_name="Smith",
    )
