import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def client():
    """Синхронный TestClient для простых тестов."""
    from starlette.testclient import TestClient
    return TestClient(app)


@pytest.fixture
async def async_client():
    """Асинхронный httpx-клиент для тестов с async endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
