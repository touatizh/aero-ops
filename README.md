# AeroOps ✈️

<!--toc:start-->

- [AeroOps ✈️](#aeroops-️)
  - [🚀 Key Features](#🚀-key-features)
  - [🛠️ Tech Stack](#🛠️-tech-stack)
  - [🏃 Getting Started](#🏃-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [📐 Architecture](#📐-architecture)
  - [🔌 API Endpoints](#🔌-api-endpoints)
    - [Authentication](#authentication)
    - [Flight Operations](#flight-operations)
  - [🗺️ Roadmap](#🗺️-roadmap)
  - [👨‍💻 Author](#👨‍💻-author)
  - [📜 License](#📜-license)
  <!--toc:end-->

**A Backend-First Aviation Operations & Readiness Management System**

AeroOps is a domain-driven application designed to manage pilot flight declarations and operational validation. It prioritizes data integrity, auditability, and strict workflow enforcement over generic CRUD operations.

> **Note:** This project serves as a portfolio piece demonstrating professional-grade backend architecture, async patterns in Python, and domain-driven design.

---

## 🚀 Key Features

- **Domain-Driven Design:** Strict separation between API, Service, and Data layers.
- **Role-Based Access Control (RBAC):** Fine-grained permissions for Pilot (PI), Operations (OPS), and Admin roles.
- **Immutability by Default:** Flight records are immutable; corrections are handled via voiding and replacement workflows.
- **Explicit Workflows:** State transitions (Pending → Approved → Voided) are enforced via domain logic, not generic updates.
- **Complete Audit Trail:** All flight operations (creation, approval, voiding) are logged with actor tracking.
- **Async Architecture:** Built with `FastAPI` and `SQLModel` on an async `PostgreSQL` stack.
- **Comprehensive Testing:** Full test coverage with 22 test cases covering workflows, permissions, and edge cases.
- **Reproducible Environment:** Fully declarative development environment using Nix Flakes.

---

## 🛠️ Tech Stack

**Backend:**

- **Framework:** FastAPI (Python 3.14)
- **ORM:** SQLModel (Pydantic + SQLAlchemy 2.0)
- **Database:** PostgreSQL (Async via `asyncpg`)
- **Migrations:** Alembic
- **Auth:** JWT (Python-JOSE) & Argon2 hashing
- **Testing:** Pytest with async support

**Infrastructure & Tooling:**

- **Environment:** Nix Flakes (Reproducible shells)
- **Dependency Management:** uv
- **Containerization:** Docker (Planned)

---

## 🏃 Getting Started

### Prerequisites

- **Nix** (with Flakes enabled)
- **Docker** (optional, for containerized DB)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/touatizh/aero-ops.git
   cd aero-ops
   ```

2. **Enter the Development Shell:**
   This command sets up Python, Node.js, Postgres, Redis, and all required tools automatically.

   ```bash
   nix develop
   ```

   _On first run, the shell will automatically install dependencies (`uv sync`) and setup the local Postgres database._

3. **Configure Environment:**
   Copy the example environment file and update secrets if necessary.

   ```bash
   cp .env.example .env
   ```

4. **Apply Migrations:**

   ```bash
   cd backend
   uv run alembic upgrade head
   ```

5. **Run the Server:**

   ```bash
   uv run uvicorn app.main:app --reload
   ```

6. **Run Tests:**

   ```bash
   uv run pytest
   ```

Access the API documentation at: `http://127.0.0.1:8000/docs`

---

## 📐 Architecture

The project follows a layered architecture to ensure maintainability and testability.

- **`app/api`**: HTTP routes and request validation (Pydantic Schemas).
- **`app/services`**: Business logic and workflow enforcement.
- **`app/models`**: Database table definitions (SQLModel).
- **`app/core`**: Configuration, security, and global utilities.
- **`tests/`**: Comprehensive test suite with fixtures for RBAC testing.

**Database Schema:**

```
Users (id, username, role, is_active)
  ↓
Flight Logs (id, dof, duration_min, aircraft_category, status, pilot_id, created_by_id)
  ↓
Audit Logs (id, action, actor_id, target_id, details, created_at)
```

---

## 🔌 API Endpoints

### Authentication

- **POST** `/api/auth/login` - User login (returns JWT access token)

### Flight Operations

- **POST** `/api/flights/` - Create flight log
  - PI users: Create for themselves
  - OPS users: Create for any pilot (requires `pilot_id`)

- **POST** `/api/flights/{id}/approve` - Approve pending flight (OPS only)

- **POST** `/api/flights/{id}/void` - Void flight with reason (OPS only)

- **GET** `/api/flights/` - List flights with pagination and filtering
  - PI users: See only their own flights
  - OPS users: See all flights
  - Query params: `status`, `page`, `page_size`

- **GET** `/api/flights/{id}` - Get detailed flight information with user details

**All endpoints require JWT authentication via Bearer token.**

---

## 🗺️ Roadmap

- [x] Project Setup & Async DB Configuration
- [x] Domain Models (User, Flight, AuditLog)
- [x] Authentication & Authorization (RBAC)
- [x] Flight Lifecycle Services (Approval/Voiding logic)
- [x] Audit Logging Implementation
- [ ] Administration (User Management, Audit Log Access, Role Assignment)
- [ ] React Frontend (Thin Client)
- [ ] Comprehensive Test Suite
- [ ] Deployment & CI/CD Pipeline
- [ ] Advanced Reporting & Analytics

---

## 👨‍💻 Author

**Helmi Touati**

- _Helicopter Pilot & Software Engineer_
- [LinkedIn](https://www.linkedin.com/in/helmi-touati-451518273) | [GitHub](https://github.com/touatizh)

---

## 📜 License

This project is licensed under the MIT License.
