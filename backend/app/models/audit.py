from uuid import UUID

from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from app.models.base import BaseModel


class AuditLog(BaseModel, table=True):
    actor_id: UUID
    target_id: UUID
    action: str
    details: dict | None = Field(sa_type=JSONB, nullable=True)
