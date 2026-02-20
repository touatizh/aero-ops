from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.core.config import settings
from app.db.base import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
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
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
# TODO : Include API routers here later


@app.get("/healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"message": "Welcome to AeroOps", "status": "Operational"}
