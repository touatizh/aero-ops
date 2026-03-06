import pytest
from app.core.config import settings

@pytest.mark.asyncio
async def test_login_success(client, test_pilot):
    response = await client.post(
        "/api/auth/login",
        json={
            "username": test_pilot.username,
            "password": "password123",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data

@pytest.mark.asyncio
async def test_login_fail(client):
    response = await client.post(
        "/api/auth/login",
        json={
            "username": settings.FIRST_SUPERUSER_USERNAME,
            "password": "wrongpassword",
        },
    )
    assert response.status_code == 401
