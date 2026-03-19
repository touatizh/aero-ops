from uuid import UUID

from fastapi import HTTPException
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_password
from app.models import Role, User
from app.models.flight import Flight, FlightStatus
from app.schemas import UserCreate, UserRead
from app.schemas.user import UserReadWithStats, UserUpdate


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


async def get_all_users(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    active_filter: bool | None = None,
    role_filter: Role | None = None,
) -> list[UserRead]:
    query = select(User)
    if isinstance(active_filter, bool):
        query = query.where(User.is_active == active_filter)
    if role_filter:
        query = query.where(User.role == role_filter)
    query = query.offset(skip).limit(limit)
    result = await session.exec(query)
    user_list = result.all()
    return [UserRead(**user.model_dump()) for user in user_list]


async def get_users_count(
    session: AsyncSession,
    active_filter: bool | None = None,
    role_filter: Role | None = None,
) -> int:
    query = select(func.count()).select_from(User)
    if isinstance(active_filter, bool):
        query = query.where(User.is_active == active_filter)
    if role_filter:
        query = query.where(User.role == role_filter)

    result = await session.exec(query)

    return result.one()


async def get_user_with_stats(
    session: AsyncSession,
    user_id: UUID,
) -> UserReadWithStats | None:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(404, detail="User not found.")

    user_read = UserRead(**user.model_dump())

    total_flights = await session.exec(
        select(func.count()).select_from(Flight).where(Flight.pilot_id == user.id)
    )
    total_flight_hours = await session.exec(
        select(func.sum(Flight.duration_min))
        .select_from(Flight)
        .where(Flight.pilot_id == user.id)
    )
    total_flight_hours_scalar = total_flight_hours.one()
    total_flight_hours = total_flight_hours_scalar if total_flight_hours_scalar else 0.0
    pending_flights = await session.exec(
        select(func.count())
        .select_from(Flight)
        .where(Flight.pilot_id == user.id)
        .where(Flight.status == FlightStatus.PENDING)
    )
    return UserReadWithStats(
        **user_read.model_dump(),
        total_flights=total_flights.one(),
        total_flight_hours=round(total_flight_hours / 60, 2),
        pending_flights=pending_flights.one(),
    )


async def update_user(session: AsyncSession, user_id: UUID, update: UserUpdate) -> User:
    user = await get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(404, "User not found.")

    update_data = update.model_dump(exclude_unset=True)
    user.username = update_data.get("username", user.username)
    new_password = update_data.get("password", None)
    if new_password:
        user.hashed_pwd = hash_password(new_password)
    user.role = update_data.get("role", user.role)
    user.is_active = update_data.get("is_active", user.is_active)

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
