import pytest
from app.core.security import (
    hash_password,
    verify_password,
    generate_user_tokens,
    decode_jwt,
)


def test_hash_password():
    password = "mypassword"
    hashed_password = hash_password(password)
    assert verify_password(password, hashed_password) == True
    assert verify_password("wrongpassword", hashed_password) == False


def test_generate_user_tokens():
    user_id = 1
    user_role = "PI"
    tokens = generate_user_tokens(str(user_id), user_role)
    assert isinstance(tokens, dict)
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    access_token = tokens.get("access_token")
    access_token = decode_jwt(str(access_token))
    assert access_token.get("sub") == str(user_id)


@pytest.mark.asyncio
async def test_unauthenticated_request(client):
    response = await client.get("/api/flights/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/api/flights/", headers=headers)
    assert response.status_code == 401
