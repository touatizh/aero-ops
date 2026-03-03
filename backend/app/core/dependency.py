from uuid import UUID

from fastapi import Depends
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import decode_jwt
from app.db.dependency import DbSession
from app.models.user import User
from app.services.user_service import get_user_by_id


async def get_current_user(
    session: DbSession,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
) -> User:
    token = credentials.credentials
    payload = decode_jwt(token)
    user_id_str = payload.get("sub")

    if not user_id_str:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        # If the string is not a valid UUID
        raise HTTPException(status_code=401, detail="Invalid token subject")

    user = await get_user_by_id(session=session, user_id=user_id)

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user
