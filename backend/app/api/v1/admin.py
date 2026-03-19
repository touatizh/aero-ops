from math import ceil
from uuid import UUID

from fastapi import APIRouter, Depends

from app.core.dependency import require_role
from app.core.roles import ADMIN, OPS_OR_ADMIN
from app.db.dependency import DbSession
from app.models import User
from app.models.user import Role
from app.schemas import (
    AdminUserCreate,
    FlightStatistics,
    PaginatedResponse,
    UserRead,
    UserReadWithStats,
    UserUpdate,
)
from app.services.flight_service import get_all_flights_statistics
from app.services.user_service import (
    create_user,
    get_all_users,
    get_user_with_stats,
    get_users_count,
    update_user,
)

router: APIRouter = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/statistics", response_model=FlightStatistics)
async def get_flight_statistics(
    session: DbSession, current_user: User = Depends(require_role(*OPS_OR_ADMIN))
):
    return await get_all_flights_statistics(session=session)


@router.get("/users", response_model=PaginatedResponse[UserRead])
async def handle_get_all_users(
    session: DbSession,
    current_user: User = Depends(require_role(*OPS_OR_ADMIN)),
    active_filter: bool | None = None,
    role_filter: Role | None = None,
    page: int = 1,
    page_size: int = 10,
):
    skip = (page - 1) * page_size
    users_list = await get_all_users(
        session=session,
        skip=skip,
        limit=page_size,
        active_filter=active_filter,
        role_filter=role_filter,
    )
    total_users = await get_users_count(
        session=session, active_filter=active_filter, role_filter=role_filter
    )
    return PaginatedResponse(
        total=total_users,
        page=page,
        page_size=page_size,
        total_pages=ceil(total_users / page_size),
        items=users_list,
    )


@router.get("/users/{id}", response_model=UserReadWithStats)
async def handle_get_user_with_details(
    session: DbSession,
    id: UUID,
    current_user: User = Depends(require_role(*OPS_OR_ADMIN)),
):
    return await get_user_with_stats(session=session, user_id=id)


@router.post("/users", response_model=UserRead)
async def handle_create_user(
    session: DbSession,
    user_data: AdminUserCreate,
    current_user: User = Depends(require_role(*ADMIN)),
):
    new_user = await create_user(
        session=session,
        user=user_data,
    )
    return UserRead(**new_user.model_dump())


@router.patch("/users/{id}", response_model=UserRead)
async def handle_update_user(
    session: DbSession,
    id: UUID,
    user_data: UserUpdate,
    current_user: User = Depends(require_role(*ADMIN)),
):
    updated_user = await update_user(session=session, user_id=id, update=user_data)
    return UserRead(**updated_user.model_dump())
