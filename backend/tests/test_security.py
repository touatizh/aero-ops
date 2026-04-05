import jwt
import pytest
from datetime import UTC, datetime, timedelta
from fastapi import HTTPException

from app.core.config import settings
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


def test_decode_jwt_expired_token():
    payload = {
        "sub": "test-user",
        "exp": datetime.now(UTC) - timedelta(minutes=1),
    }
    expired_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_jwt(expired_token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


def test_decode_jwt_tampered_signature():
    payload = {
        "sub": "test-user",
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    valid_token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY.get_secret_value(),
        algorithm=settings.JWT_ALGORITHM,
    )
    tampered_token = valid_token[:-8] + "XXXXXXXX"
    with pytest.raises(HTTPException) as exc_info:
        decode_jwt(tampered_token)
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"


@pytest.mark.asyncio
async def test_unauthenticated_request(client):
    response = await client.get("/api/flights/")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid_token(client):
    headers = {"Authorization": "Bearer invalidtoken"}
    response = await client.get("/api/flights/", headers=headers)
    assert response.status_code == 401
