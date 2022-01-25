import pytest

from unicore.unicore_service import UnicoreService


@pytest.fixture
def unicore_service():
    return UnicoreService(token="eyJhbGciOiJSUzI1N...iIsInR5cCIgOiAiSldUIiwia")
