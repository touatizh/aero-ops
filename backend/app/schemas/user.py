from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel

from app.models.user import Role

# Input Schemas


class UserCreate(SQLModel):
    """Schema for creating a new user."""

    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=8)


class UserLogin(SQLModel):
    """Schema for user login."""

    username: str
    password: str


class UserUpdate(SQLModel):
    """Schema for user update."""

    username: str | None = None
    password: str | None = None
    role: Role | None = None
    is_active: bool | None = None


# Output Schemas


class UserRead(SQLModel):
    """Schema for user output with no sensitive data."""

    id: UUID
    username: str
    role: Role
    is_active: bool
    created_at: datetime


class UserReadWithStats(UserRead):
    """Schema for user output with flight statistics."""

    total_flights: int
    total_flight_hours: float = 0.0
    pending_flights: int
