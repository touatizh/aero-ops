# ruff: noqa: F401

from app.schemas.audit import (
    AuditLogListResponse,
    AuditLogRead,
    AuditLogReadWithDetails,
)
from app.schemas.common import (
    ErrorResponse,
    Message,
    PaginatedResponse,
    SuccessResponse,
    TokenData,
    TokenResponse,
)
from app.schemas.flight import (
    FlightApprove,
    FlightCreate,
    FlightListResponse,
    FlightRead,
    FlightReadWithDetails,
    FlightStatistics,
    FlightVoid,
    UserSummary,
)
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserRead,
    UserReadWithStats,
    UserUpdate,
)

__all__ = [
    # Common schemas
    "Message",
    "ErrorResponse",
    "SuccessResponse",
    "PaginatedResponse",
    "TokenResponse",
    "TokenData",
    # Flight schemas
    "FlightCreate",
    "FlightApprove",
    "FlightVoid",
    "UserSummary",
    "FlightRead",
    "FlightReadWithDetails",
    "FlightListResponse",
    "FlightStatistics",
    # Audit schemas
    "AuditLogRead",
    "AuditLogReadWithDetails",
    "AuditLogListResponse",
    # User schemas
    "UserCreate",
    "UserLogin",
    "UserUpdate",
    "UserRead",
    "UserReadWithStats",
]
