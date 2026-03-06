from datetime import UTC, datetime
from uuid import UUID

from fastapi.exceptions import HTTPException
from sqlalchemy import func
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.audit import AuditLog
from app.models.flight import Flight, FlightStatus
from app.models.user import Role, User
from app.schemas.flight import FlightCreate, FlightVoid


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

    if current_user.role != Role.OPS:
        raise HTTPException(403, "Only OPS can approve flights.")

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
        action="Flight_APPROVED",
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

    if current_user.role != Role.OPS:
        raise HTTPException(403, "Only OPS can void flights.")

    flight = await get_flight_by_id(session=session, flight_id=flight_id)

    if not flight:
        raise HTTPException(status_code=404, detail="Flight not found")

    if flight.status == FlightStatus.VOIDED:
        raise HTTPException(status_code=400, detail="Flight is already voided")

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
    flights = result.all()

    return len(flights)
