# AeroOps FastAPI Schemas - Quick Reference

<!--toc:start-->

- [AeroOps FastAPI Schemas - Quick Reference](#aeroops-fastapi-schemas-quick-reference)
  - [Created Schema Files](#created-schema-files)
  - [Schema Categories](#schema-categories)
    - [1. User Schemas (`user.py`)](#1-user-schemas-userpy)
    - [2. Flight Schemas (`flight.py`)](#2-flight-schemas-flightpy)
    - [3. Audit Schemas (`audit.py`)](#3-audit-schemas-auditpy)
    - [4. Common Schemas (`common.py`)](#4-common-schemas-commonpy)
  - [Quick Usage Examples](#quick-usage-examples)
    - [Creating Endpoints](#creating-endpoints)
    - [Partial Updates (PATCH)](#partial-updates-patch)
    - [Pagination](#pagination)
    - [Authentication](#authentication)
  - [Key Features](#key-features)
  - [Import Pattern](#import-pattern)
  <!--toc:end-->

## Created Schema Files

```
backend/app/schemas/
├── __init__.py          # Central exports
├── common.py            # Shared schemas (Message, ErrorResponse, TokenResponse, etc.)
├── user.py              # User-related schemas
├── flight.py            # Flight-related schemas
└── audit.py             # Audit log schemas
```

## Schema Categories

### 1. User Schemas (`user.py`)

**Input Schemas:**

- `UserCreate` - Create new user (username, password)
- `UserLogin` - User authentication (username, password)
- `UserUpdate` - Update user (all optional fields for PATCH)

**Output Schemas:**

- `UserRead` - Basic user info (excludes hashed_pwd for security)
- `UserReadWithStats` - User with flight statistics

### 2. Flight Schemas (`flight.py`)

**Input Schemas:**

- `FlightCreate` - Create flight record (dof, duration_min, aircraft_category, pilot_id, notes)
- `FlightApprove` - Approve flight (optional notes)
- `FlightVoid` - Void flight (void_reason required)

**Output Schemas:**

- `FlightRead` - Basic flight information
- `FlightReadWithDetails` - Flight with pilot details (includes UserSummary objects)
- `FlightListResponse` - Paginated flight list
- `FlightStatistics` - Flight statistics and aggregations
- `UserSummary` - Minimal user info for nested responses

### 3. Audit Schemas (`audit.py`)

**Output Schemas Only (read-only):**

- `AuditLogRead` - Basic audit log entry
- `AuditLogReadWithDetails` - Audit log with actor/target details
- `AuditLogListResponse` - Paginated audit log list

### 4. Common Schemas (`common.py`)

**Utility Schemas:**

- `Message` - Simple message response
- `ErrorResponse` - Error detail response
- `SuccessResponse` - Success with message
- `PaginatedResponse[T]` - Generic paginated response
- `TokenResponse` - JWT token response (access_token, token_type, expires_in)
- `TokenData` - Token payload data

## Quick Usage Examples

### Creating Endpoints

```python
from app.schemas import UserCreate, UserRead, FlightCreate, FlightRead

# POST /users/ - Create user
@app.post("/users/", response_model=UserRead)
async def create_user(user: UserCreate):
    # FastAPI validates input against UserCreate
    # Response serialized as UserRead (excludes password)
    pass

# POST /flights/ - Create flight
@app.post("/flights/", response_model=FlightRead)
async def create_flight(flight: FlightCreate):
    # Validates: dof, duration_min > 0, aircraft_category enum
    pass
```

### Partial Updates (PATCH)

```python
from app.schemas import UserUpdate

@app.patch("/users/{user_id}", response_model=UserRead)
async def update_user(user_id: UUID, update: UserUpdate):
    # Only provided fields are updated
    data = update.model_dump(exclude_unset=True)
    # data only contains fields user actually sent
    pass
```

### Pagination

```python
from app.schemas import FlightListResponse

@app.get("/flights/", response_model=FlightListResponse)
async def list_flights(page: int = 1, page_size: int = 20):
    return FlightListResponse(
        total=total_count,
        page=page,
        page_size=page_size,
        flights=flight_list
    )
```

### Authentication

```python
from app.schemas import UserLogin, TokenResponse

@app.post("/auth/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    # Validate username/password
    token = create_jwt_token(user)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=3600
    )
```

## Key Features

✅ **Type Safety**: Full type hints for IDE autocompletion
✅ **Validation**: Pydantic validation on all inputs
✅ **Security**: Sensitive fields excluded from output schemas
✅ **Flexibility**: Optional fields for partial updates
✅ **Reusability**: Shared common schemas across endpoints

## Import Pattern

```python
# Import from root schemas package
from app.schemas import (
    UserCreate,
    UserRead,
    FlightCreate,
    FlightRead,
    Message,
    TokenResponse
)
```

All schemas are exported from `app.schemas.__init__.py` for clean imports.
