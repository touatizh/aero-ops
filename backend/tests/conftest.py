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
async def test_pilot(client):
    """Creates a test pilot and returns the user object."""
    async with SessionLocal() as session:
        user_in = UserCreate(username="test_pilot", password="password123")
        user = await create_user(session, user_in, Role.PI)
        yield user


@pytest.fixture(scope="function")
async def test_pilot_2(client):
    async with SessionLocal() as session:
        user_in = UserCreate(username="test_pilot_2", password="password123")
        user = await create_user(session, user_in, Role.PI)
        return user


@pytest.fixture(scope="function")
async def test_ops(client):
    """Creates a test ops user and returns the user object."""
    async with SessionLocal() as session:
        user_in = UserCreate(username="test_ops", password="password123")
        user = await create_user(session, user_in, Role.OPS)
        yield user


@pytest.fixture
async def auth_headers(client):
    async def _auth(user):
        res = await client.post(
            "/api/auth/login",
            json={"username": user.username, "password": "password123"},
        )
        return {"Authorization": f"Bearer {res.json()['access_token']}"}

    return _auth


@pytest.fixture(scope="function")
async def pending_flight(client, test_pilot, auth_headers):
    headers = await auth_headers(test_pilot)
    flight = await client.post(
        "/api/flights/",
        json={
            "dof": "2026-03-13T03:51:31.575",
            "duration_min": 100,
            "aircraft_category": "Helicopter",
            "notes": "STD NVG TRAINING",
        },
        headers=headers,
    )
    return flight.json()


@pytest.fixture(scope="function")
async def pending_flight_pilot_2(client, test_pilot_2, auth_headers):
    headers = await auth_headers(test_pilot_2)
    flight = await client.post(
        "/api/flights/",
        json={
            "dof": "2026-03-14T13:51:31.575",
            "duration_min": 115,
            "aircraft_category": "Helicopter",
            "notes": "STD TAC TRAINING",
        },
        headers=headers,
    )
    return flight.json()


@pytest.fixture(scope="function")
async def approved_flight(client, auth_headers, test_ops, pending_flight):
    headers = await auth_headers(test_ops)
    approved = await client.post(
        f"/api/flights/{pending_flight.get('id')}/approve",
        json={},
        headers=headers,
    )
    return approved.json()


@pytest.fixture(scope="function")
async def voided_flight(client, auth_headers, test_ops, pending_flight):
    headers = await auth_headers(test_ops)
    voided = await client.post(
        f"/api/flights/{pending_flight.get('id')}/void",
        json={"void_reason": "Wrong flight date"},
        headers=headers,
    )
    return voided.json()
