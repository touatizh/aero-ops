from __future__ import annotations

from enum import StrEnum
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.flight import Flight


class Role(StrEnum):
    PI = "Pilot"
    OPS = "Operations Officer"
    ADMIN = "Administrator"


class User(BaseModel, table=True):
    username: str = Field(unique=True)
    hashed_pwd: str
    is_active: bool = True
    role: Role = Field(default=Role.PI)

    flights: list[Flight] = Relationship(back_populates="pilot")
