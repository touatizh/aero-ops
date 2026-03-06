# ruff: noqa: F401

from app.api.v1.auth import router as auth_router
from app.api.v1.flight import router as flight_router

__all__ = [
    "auth_router",
    "flight_router",
]
