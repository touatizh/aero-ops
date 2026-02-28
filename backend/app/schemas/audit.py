from datetime import datetime
from uuid import UUID

from sqlmodel import SQLModel

#! Note: Audit logs are read-only no input schemas are needed.


class AuditLogRead(SQLModel):
    """Schema for audit log output."""

    id: UUID
    actor_id: UUID
    target_id: UUID
    action: str
    details: dict | None = None
    created_at: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "c8a3b2b4-4b3a-4e9e-8d8c-3f3e2d2c1b1a",
                "actor_id": "4e38fb1d-5a98-49b4-949c-e3d4ac4a416c",
                "target_id": "02923168-da6c-4680-ba57-84b3f0d93258",
                "action": "flight.approved",
                "details": {
                    "flight_id": "02923168-da6c-4680-ba57-84b3f0d93258",
                    "previous_status": "Pending",
                    "new_status": "Approved",
                },
                "created_at": "2023-01-01T00:00:00",
            }
        }


class AuditLogReadWithDetails(AuditLogRead):
    """Extended audit log output with details."""

    actor_username: str
    target_type: str  # "flight", "user"


class AuditLogListResponse(SQLModel):
    """Paginated response for audit log list."""

    total: int
    page: int
    page_size: int
    logs: list[AuditLogRead]
