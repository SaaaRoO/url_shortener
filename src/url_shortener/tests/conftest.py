import pytest
from django.test import AsyncClient

@pytest.fixture
async def async_client():
    return AsyncClient()
