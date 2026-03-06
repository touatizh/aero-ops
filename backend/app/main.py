from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.v1 import *
from app.core.config import settings
from app.db.base import init_db
from app.db.session import SessionLocal
from app.models import Role
from app.schemas import UserCreate
from app.services.user_service import create_user, get_user_by_username


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with SessionLocal() as session:
        user = await get_user_by_username(
            session=session, username=settings.FIRST_SUPERUSER_USERNAME
        )
        if not user:
            admin_user: UserCreate = UserCreate(
                username=settings.FIRST_SUPERUSER_USERNAME,
                password=settings.FIRST_SUPERUSER_PASSWORD.get_secret_value(),
            )
            try:
                await create_user(session=session, user=admin_user, role=Role.ADMIN)
            except Exception as e:
                print("Unable to seed admin user.", e)
            else:
                print("Admin user seeded.")

    yield


app = FastAPI(title="AeroOps API", version=settings.VERSION, lifespan=lifespan)
limiter = Limiter(key_func=get_remote_address)

# Apply middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    # TODO : Add any additional middleware configuration
)


# Add rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Register routers
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(flight_router, prefix=settings.API_PREFIX)
