from fastapi import APIRouter, Depends

from app.core.dependency import require_role
from app.core.roles import OPS_OR_ADMIN
from app.db.dependency import DbSession
from app.models import User
from app.schemas import FlightStatistics
from app.services.flight_service import get_all_flights_statistics

router: APIRouter = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/statistics", response_model=FlightStatistics)
async def get_flight_statistics(
    session: DbSession, current_user: User = Depends(require_role(*OPS_OR_ADMIN))
):
    return await get_all_flights_statistics(session=session)
