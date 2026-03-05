import pytest
from app.core.config import settings
from app.services.user_service import create_user
from app.schemas.user import UserCreate
from app.db.session import SessionLocal

@pytest.mark.asyncio
async def test_login_success(client):
    async with SessionLocal() as session:
        test_user: UserCreate = UserCreate(
            username="test user",
            password="testpassword123",
        )
        await create_user(session=session, user=test_user)

    response = await client.post(
        "/api/auth/login",
        json={
            "username": test_user.username,
            "password": test_user.password,
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
