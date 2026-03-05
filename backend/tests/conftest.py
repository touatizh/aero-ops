import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.db.session import engine  # Import the global engine


@pytest.fixture(scope="function")
async def client():
    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Teardown: Dispose the engine to close connections
    await engine.dispose()
