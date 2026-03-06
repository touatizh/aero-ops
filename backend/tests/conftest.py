import pytest
from sqlmodel import SQLModel
from httpx import AsyncClient, ASGITransport
from app.db.base import init_db
from app.main import app
from app.db.session import engine, SessionLocal
from app.schemas import UserCreate
from app.services.user_service import create_user
from app.models import Role


@pytest.fixture(scope="function")
async def client():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
    await init_db()

    transport = ASGITransport(app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    # Teardown: Dispose the engine to close connections
    await engine.dispose()


@pytest.fixture(scope="function")
async def test_pilot():
    """Creates a test pilot and returns the user object."""
    async with SessionLocal() as session:
        user_in = UserCreate(username="test_pilot", password="password123")
        user = await create_user(session, user_in, Role.PI)
        yield user

@pytest.fixture(scope="function")
async def test_ops():
    """Creates a test ops user and returns the user object."""
    async with SessionLocal() as session:
        user_in = UserCreate(username="test_ops", password="password123")
        user = await create_user(session, user_in, Role.OPS)
        yield user


@pytest.fixture
async def auth_headers(client):
    async def _auth(user):
        res = await client.post("/api/auth/login", json={
            "username": user.username,
            "password": "password123"
        })
        return {"Authorization": f"Bearer {res.json()['access_token']}"}
    return _auth
