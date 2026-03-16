from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependency import get_current_user
from app.db.dependency import DbSession
from app.models.flight import FlightStatus
from app.models.user import Role, User
from app.schemas import (
    FlightApprove,
    FlightCreate,
    FlightListResponse,
    FlightRead,
    FlightReadWithDetails,
    FlightVoid,
    UserSummary,
)
from app.services.flight_service import (
    approve_flight,
    create_flight,
    get_flight_by_id,
    get_flight_count,
    get_flights,
    void_flight,
)
from app.services.user_service import get_user_by_id

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.post("/", response_model=FlightRead)
async def handle_create_flight(
    session: DbSession,
    data: FlightCreate,
    current_user: User = Depends(get_current_user),
):

    # Validate pilot_id if provided (OPS creating flight for someone else)
    if data.pilot_id is not None:
        pilot = await get_user_by_id(session=session, user_id=data.pilot_id)
        if not pilot:
            raise HTTPException(
                status_code=400, detail="pilot_id must be a valid Pilot ID."
            )
    new_flight = await create_flight(
        session=session, flight_data=data, current_user=current_user
    )
    return new_flight


@router.post("/{id}/void", response_model=FlightRead)
async def handle_void_flight(
    session: DbSession,
    id: UUID,
    data: FlightVoid,
    current_user: User = Depends(get_current_user),
):

    return await void_flight(
        session=session, flight_id=id, void_data=data, current_user=current_user
    )


@router.post("/{id}/approve", response_model=FlightRead)
async def handle_approve_flight(
    session: DbSession,
    id: UUID,
    data: FlightApprove,
    current_user: User = Depends(get_current_user),
):

    return await approve_flight(
        session=session, flight_id=id, current_user=current_user, notes=data.notes
    )


@router.get("/", response_model=FlightListResponse)
async def handle_list_flights(
    session: DbSession,
    status_filter: FlightStatus | None = None,
    page: int = 1,
    page_size: int = 10,
    current_user: User = Depends(get_current_user),
):
    skip = (page - 1) * page_size
    pilot_filter = current_user.id if current_user.role == Role.PI else None

    flights = await get_flights(
        session=session,
        pilot_id=pilot_filter,
        status=status_filter,
        skip=skip,
        limit=page_size,
    )

    total = await get_flight_count(
        session=session, pilot_id=pilot_filter, status=status_filter
    )

    flights = [FlightRead(**f.model_dump()) for f in flights]
    return FlightListResponse(
        total=total, page=page, page_size=page_size, flights=flights
    )


@router.get("/{id}", response_model=FlightReadWithDetails)
async def handle_get_flight_by_id(session: DbSession, id: UUID):
    flight = await get_flight_by_id(session=session, flight_id=id)
    if flight is None:
        raise HTTPException(status_code=404, detail="Flight not found.")

    pilot = await get_user_by_id(session=session, user_id=flight.pilot_id)
    if pilot is None:
        raise HTTPException(status_code=404, detail="Pilot: user not found.")

    pilot_sum = UserSummary(id=pilot.id, username=pilot.username, role=pilot.role)

    if flight.pilot_id != flight.created_by_id:
        created_by = await get_user_by_id(session=session, user_id=flight.created_by_id)
        if created_by is None:
            raise HTTPException(status_code=404, detail="Created by: user not found.")

        created_by_sum = UserSummary(
            id=created_by.id, username=created_by.username, role=created_by.role
        )
    else:
        created_by_sum = pilot_sum

    if flight.status == FlightStatus.VOIDED and flight.voided_by_id is not None:
        voided_by = await get_user_by_id(session=session, user_id=flight.voided_by_id)
        if voided_by is None:
            raise HTTPException(status_code=404, detail="Voided by: user not found.")

        voided_by_sum = UserSummary(
            id=voided_by.id, username=voided_by.username, role=voided_by.role
        )
    else:
        voided_by_sum = None

    flight_with_details = FlightReadWithDetails(
        **flight.model_dump(),
        pilot=pilot_sum,
        created_by=created_by_sum,
        voided_by=voided_by_sum,
    )
    return flight_with_details
