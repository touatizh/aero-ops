from datetime import UTC, datetime
from uuid import UUID

from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import col, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit import AuditLog
from app.models.flight import AircraftCategory, Flight, FlightStatus
from app.models.user import Role, User
from app.schemas.flight import FlightCreate, FlightStatistics, FlightVoid


async def get_flight_by_id(session: AsyncSession, flight_id: UUID) -> Flight | None:
    """Query flights table for a flight by UUID and returns the Flight model."""

    result = await session.exec(select(Flight).where(Flight.id == flight_id))

    return result.first()


async def create_flight(
    session: AsyncSession, flight_data: FlightCreate, current_user: User
) -> Flight:
    """Creates a new flight in the database and returns the Flight model."""

    if current_user.role == Role.PI:
        pilot_id = current_user.id
        created_by_id = current_user.id
    else:
        if not flight_data.pilot_id:
            raise HTTPException(status_code=400, detail="Pilot ID required")
        pilot_id = flight_data.pilot_id
        created_by_id = current_user.id

    new_flight = Flight(
        dof=flight_data.dof,
        duration_min=flight_data.duration_min,
        aircraft_category=flight_data.aircraft_category,
        notes=flight_data.notes,
        pilot_id=pilot_id,
        created_by_id=created_by_id,
        status=FlightStatus.PENDING,
    )

    session.add(new_flight)
    await session.flush()

    audit_log = AuditLog(
        action="FLIGHT_CREATED", actor_id=current_user.id, target_id=new_flight.id
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(new_flight)

    return new_flight


async def approve_flight(
    session: AsyncSession, flight_id: UUID, current_user: User, notes: str | None = None
) -> Flight:
    """Approves a pending flight."""

    flight = await get_flight_by_id(session=session, flight_id=flight_id)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.status != FlightStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot approve flight with status: {flight.status}",
        )

    flight.status = FlightStatus.APPROVED
    if notes:
        flight.notes = notes

    session.add(flight)
    await session.flush()

    audit_details = {
        "previous_status": "Pending",
        "new_status": "Approved",
    }

    audit_log = AuditLog(
        action="FLIGHT_APPROVED",
        actor_id=current_user.id,
        target_id=flight.id,
        details=audit_details,
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(flight)

    return flight


async def void_flight(
    session: AsyncSession, flight_id: UUID, void_data: FlightVoid, current_user: User
) -> Flight:
    """Voids a flight with a reason."""

    flight = await get_flight_by_id(session=session, flight_id=flight_id)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.status != FlightStatus.PENDING:
        raise HTTPException(
            status_code=400, detail=f"Cannot void flight with status: {flight.status}"
        )

    flight.status = FlightStatus.VOIDED
    flight.voided_at = datetime.now(UTC).replace(tzinfo=None)
    flight.void_reason = void_data.void_reason
    flight.voided_by_id = current_user.id

    session.add(flight)
    await session.flush()

    audit_details = {
        "previous_status": "Pending",
        "new_status": "Voided",
    }

    audit_log = AuditLog(
        action="FLIGHT_VOIDED",
        actor_id=current_user.id,
        target_id=flight.id,
        details=audit_details,
    )
    session.add(audit_log)

    await session.commit()
    await session.refresh(flight)

    return flight


async def get_flights(
    session: AsyncSession,
    pilot_id: UUID | None = None,
    status: FlightStatus | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Flight]:
    """Query flights with optional filters for pilot and status."""

    query = select(Flight)

    if pilot_id:
        query = query.where(Flight.pilot_id == pilot_id)

    if status:
        query = query.where(Flight.status == status)

    query = query.offset(skip).limit(limit)

    result = await session.exec(query)

    return list(result.all())


async def get_flight_count(
    session: AsyncSession,
    pilot_id: UUID | None = None,
    status: FlightStatus | None = None,
) -> int:
    """Get count of flights with optional filters."""

    query = select(func.count()).select_from(Flight)

    if pilot_id:
        query = query.where(Flight.pilot_id == pilot_id)

    if status:
        query = query.where(Flight.status == status)

    result = await session.exec(query)

    return result.one()


async def get_all_flights_statistics(
    session: AsyncSession,
) -> FlightStatistics:

    count_by_status_rows = await session.exec(
        select(Flight.status, func.count()).select_from(Flight).group_by(Flight.status)
    )
    count_by_category_rows = await session.exec(
        select(Flight.aircraft_category, func.count())
        .select_from(Flight)
        .group_by(Flight.aircraft_category)
    )
    count_by_pilot_rows = await session.exec(
        select(User.username, func.count())
        .select_from(Flight)
        .join(User, col(Flight.pilot_id) == col(User.id))
        .group_by(User.username)
    )
    total_durations = await session.exec(
        select(func.sum(Flight.duration_min)).select_from(Flight)
    )

    count_by_status = {s[0]: s[1] for s in count_by_status_rows.all()}
    flights_by_category = {cat.value: 0 for cat in AircraftCategory}
    for cat, count in count_by_category_rows.all():
        flights_by_category[cat] = count
    total_durations_scalar = total_durations.one()

    total_flights = sum(count_by_status.values())
    total_hours = total_durations_scalar // 60 if total_durations_scalar else 0
    pending_flights = count_by_status.get(FlightStatus.PENDING, 0)
    approved_flights = count_by_status.get(FlightStatus.APPROVED, 0)
    voided_flights = count_by_status.get(FlightStatus.VOIDED, 0)
    count_by_pilot = {p[0]: p[1] for p in count_by_pilot_rows.all()}

    payload = {
        "total_flights": total_flights,
        "total_hours": total_hours,
        "pending_flights": pending_flights,
        "approved_flights": approved_flights,
        "voided_flights": voided_flights,
        "flights_by_aircraft_category": flights_by_category,
        "flights_by_pilot": count_by_pilot,
    }

    return FlightStatistics(**payload)
