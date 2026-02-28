from typing import Generic, TypeVar

from sqlmodel import SQLModel


class Message(SQLModel):
    """Generic message response"""

    message: str


class ErrorResponse(SQLModel):
    """Error response schema"""

    detail: str


class SuccessResponse(SQLModel):
    """Success response with message"""

    success: bool = True
    message: str


# Generic type for paginated responses
T = TypeVar("T")


class PaginatedResponse(SQLModel, Generic[T]):
    """Generic paginated response"""

    total: int
    page: int
    page_size: int
    total_pages: int
    items: list[T]


class TokenResponse(SQLModel):
    """JWT Token response"""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class TokenData(SQLModel):
    """Token payload data"""

    user_id: str
    username: str
    role: str
