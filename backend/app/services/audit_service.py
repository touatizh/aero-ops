from uuid import UUID

from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import func, select

from app.models import AuditLog


async def get_audit_log_by_id(session: AsyncSession, id: UUID) -> AuditLog:
    result = await session.exec(select(AuditLog).where(AuditLog.id == id))

    return result.first()


async def get_audit_log_count(
    session: AsyncSession,
    actor_filter: UUID | None = None,
    target_filter: UUID | None = None,
    action_filter: str | None = None,
) -> int:
    query = select(func.count()).select_from(AuditLog)
    if actor_filter:
        query = query.where(AuditLog.actor_id == actor_filter)
    if target_filter:
        query = query.where(AuditLog.target_id == target_filter)
    if action_filter:
        query = query.where(AuditLog.action == action_filter)

    result = await session.exec(query)

    return result.one()


async def get_audit_logs(
    session: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    actor_filter: UUID | None = None,
    target_filter: UUID | None = None,
    action_filter: str | None = None,
) -> list[AuditLog]:
    query = select(AuditLog)
    if actor_filter:
        query = query.where(AuditLog.actor_id == actor_filter)
    if target_filter:
        query = query.where(AuditLog.target_id == target_filter)
    if action_filter:
        query = query.where(AuditLog.action == action_filter)

    query = query.offset(skip).limit(limit)

    result = await session.exec(query)

    return list(result.all())


def get_target_type_from_action(action: str) -> str:
    match action.split("_")[0]:
        case "FLIGHT":
            return "Flight"
        case "USER":
            return "User"
        case _:
            return "Unknown"
