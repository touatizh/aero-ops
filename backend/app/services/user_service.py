from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password
from app.models import Role, User
from app.schemas import UserCreate


async def get_user_by_username(session: AsyncSession, username: str) -> User | None:
    """Query users table for a user by `username` and returns the User model."""

    result = await session.exec(select(User).where(User.username == username))

    return result.first()


async def get_user_by_id(session: AsyncSession, user_id: UUID) -> User | None:
    """Query users table for a user by the UUID and returns the User model."""

    result = await session.exec(select(User).where(User.id == user_id))

    return result.first()


async def create_user(
    session: AsyncSession, user: UserCreate, role: Role | None = None
) -> User:
    """Creates a new user in the database and returns the User model."""

    hashed_pwd = hash_password(user.password)

    new_user = User(
        username=user.username,
        hashed_pwd=hashed_pwd,
    )
    if role:
        new_user.role = role

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user
