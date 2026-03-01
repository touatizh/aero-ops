import uuid
from passlib.context import CryptContext
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(
    schemes=["argon2"],
    default="argon2",
    deprecated="auto",
    argon2__type=settings.ARGON2__TYPE,
    argon2__time_cost=settings.ARGON2__TIME_COST,
    argon2__memory_cost=settings.ARGON2__MEMORY_COST,
    argon2__parallelism=settings.ARGON2__PARALLELISM,
    argon2__hash_len=settings.ARGON2__HASH_LEN,
    argon2__salt_len=settings.ARGON2__SALT_LEN,
)


def hash_password(password: str) -> str:
    """Hash a password using Argon2."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def decode_jwt(token: str, options: dict = None) -> dict:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY.get_secret_value() ,
            algorithms=[settings.JWT_ALGORITHM],
            options=options if options else {},
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def generate_user_tokens(
    user_id: int | str, user_role: str) -> dict[str, str | int]:
    """Generate access and refresh tokens for a user."""
    access_token, access_exp = _get_access_token(user_id, user_role)
    refresh_token, refresh_exp, jti = _get_refresh_token(user_id)
    return {
        "access_token": access_token,
        "access_expires_at": access_exp,
        "refresh_token": refresh_token,
        "refresh_expires_at": refresh_exp, "refresh_token_jti": jti, 
    }


def _get_access_token(user_id: int | str, user_role: str) -> tuple[str, int]:
    """Generate an access token for the user."""
    now = datetime.now(UTC)
    exp = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE)
    payload = {"jti": str(uuid.uuid4()), "sub": str(user_id), "role": user_role, "exp": exp, "iat": now}
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM
    )
    token = token if isinstance(token, str) else token.decode("utf-8")
    return token, int(exp.timestamp())


def _get_refresh_token(user_id: int | str) -> tuple[str, int, str]:
    """Generate a refresh token for the user."""
    now = datetime.now(UTC)
    exp = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE)
    jti = str(uuid.uuid4())
    payload = {"jti": jti, "sub": str(user_id), "exp": exp, "iat": now}
    token = jwt.encode(
        payload, settings.JWT_SECRET_KEY.get_secret_value(), algorithm=settings.JWT_ALGORITHM
    )
    token = token if isinstance(token, str) else token.decode("utf-8")

    return token, int(exp.timestamp()), jti

