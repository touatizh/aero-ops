from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import generate_user_tokens, verify_password
from app.models.user import User
from app.schemas.user import UserLogin
from app.services.user_service import get_user_by_username


async def authenticate_user(
    session: AsyncSession, username: str, password: str
) -> User | bool:
    user = await get_user_by_username(session=session, username=username)
    if not user:
        return False

    password_match = verify_password(
        plain_password=password, hashed_password=user.hashed_pwd
    )
    return user if password_match else False


async def login(session: AsyncSession, data: UserLogin):
    authenticated_user = await authenticate_user(
        session=session, username=data.username, password=data.password
    )
    if isinstance(authenticated_user, User):
        tokens = generate_user_tokens(
            str(authenticated_user.id), authenticated_user.role
        )
        return tokens
    else:
        raise HTTPException(status_code=401, detail="Invalid credentials")
