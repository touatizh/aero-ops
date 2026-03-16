from datetime import datetime
from enum import StrEnum
from uuid import UUID

from sqlmodel import Field, Relationship

from app.models.base import BaseModel
from app.models.user import User


class FlightStatus(StrEnum):
    PENDING = "Pending"
    APPROVED = "Approved"
    VOIDED = "Voided"


class AircraftCategory(StrEnum):
    H = "Helicopter"
    A = "Fixed-wing"
    G = "Glider"


class Flight(BaseModel, table=True):
    __tablename__ = "flight_logs"  # type: ignore
    #! Business fields
    dof: datetime
    duration_min: int = Field(gt=0.0)
    aircraft_category: AircraftCategory = Field(default=AircraftCategory.A)
    status: FlightStatus = Field(default=FlightStatus.PENDING)
    notes: str | None

    # if voided
    voided_at: datetime | None = None
    void_reason: str | None = None
    voided_by_id: UUID | None = Field(foreign_key="users.id", default=None)


    # IDs
    pilot_id: UUID = Field(foreign_key="users.id")
    created_by_id: UUID = Field(foreign_key="users.id")

    # Relationships
    pilot: User = Relationship(
        back_populates="flights",
        sa_relationship_kwargs={"foreign_keys": "[Flight.pilot_id]"},
    )
    created_by: User = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Flight.created_by_id]"}
    )
    voided_by: User | None = Relationship(
        sa_relationship_kwargs={"foreign_keys": "[Flight.voided_by_id]"}
    )
