from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.flight import AircraftCategory, FlightStatus

# Input Schemas


class FlightCreate(SQLModel):
    """Schema for creating a new flight."""

    dof: datetime
    duration_min: int = Field(gt=0.0)
    aircraft_category: AircraftCategory = Field(default=AircraftCategory.A)
    pilot_id: UUID | None = None
    notes: str | None

    class Config:
        json_schema_extra = {
            "example": {
                "dof": "2023-01-01T00:00:00",
                "duration_min": 60,
                "aircraft_category": "Helicopter",
                "pilot_id": "c8a3b2b4-4b3a-4e9e-8d8c-3f3e2d2c1b1a",
                "notes": "Some notes about the flight",
            }
        }


class FlightApprove(SQLModel):
    """Schema for approving a flight."""

    notes: str | None = None


class FlightVoid(SQLModel):
    """Schema for voiding a flight."""

    void_reason: str

    class Config:
        json_schema_extra = {
            "example": {
                "void_reason": "Duplicate entry - flight already recorded",
            }
        }


# Output Schemas


class UserSummary(SQLModel):
    """User information to extend flight output."""

    id: UUID
    username: str
    role: str


class FlightRead(SQLModel):
    """Schema for flight output."""

    id: UUID
    dof: datetime
    duration_min: int
    aircraft_category: AircraftCategory
    status: FlightStatus
    notes: str | None

    # To be included only if status is VOIDED
    voided_at: datetime | None
    void_reason: str | None
    voided_by_id: UUID | None

    # Related IDs
    pilot_id: UUID
    created_by_id: UUID


class FlightReadWithDetails(FlightRead):
    """Extended flight output with Details."""

    pilot: UserSummary
    created_by: UserSummary
    voided_by: UserSummary | None = None


class FlightListResponse(SQLModel):
    """Paginated response for listing flights."""

    total: int
    page: int
    page_size: int
    flights: list[FlightRead]


class FlightStatistics(SQLModel):
    """Flight statistics for reporting purposes."""

    total_flights: int
    total_hours: int
    pending_flights: int
    approved_flights: int
    voided_flights: int
    flights_by_aircraft_category: dict[str, int]
    flights_by_pilot: dict[str, int]
