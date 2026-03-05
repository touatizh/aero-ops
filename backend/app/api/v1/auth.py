from fastapi import APIRouter

from app.db.dependency import DbSession
from app.schemas.common import TokenResponse
from app.schemas.user import UserLogin
from app.services.auth_service import login

router: APIRouter = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=TokenResponse)
async def handle_login(session: DbSession, data: UserLogin):
    return await login(session=session, data=data)
