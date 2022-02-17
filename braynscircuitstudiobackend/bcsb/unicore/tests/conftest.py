import pytest

from bcsb.unicore.unicore_service import UnicoreService


@pytest.fixture
def TEST_TOKEN():
    return "eyJhbGciOiJSUzI1N...iIsInR5cCIgOiAiSldUIiwia"


@pytest.fixture
def unicore_service(TEST_TOKEN: str):
    return UnicoreService(token=TEST_TOKEN)
