# AeroOps ✈️

<!--toc:start-->

- [AeroOps ✈️](#aeroops-️)
  - [🚀 Key Features](#🚀-key-features)
  - [🛠️ Tech Stack](#🛠️-tech-stack)
  - [🏃 Getting Started](#🏃-getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [📐 Architecture](#📐-architecture)
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
- **Immutability by Default:** Flight records are immutable; corrections are handled via voiding and replacement workflows.
- **Explicit Workflows:** State transitions (Pending → Approved → Voided) are enforced via domain logic, not generic updates.
- **Async Architecture:** Built with `FastAPI` and `SQLModel` on an async `PostgreSQL` stack.
- **Reproducible Environment:** Fully declarative development environment using Nix Flakes.

---

## 🛠️ Tech Stack

**Backend:**

- **Framework:** FastAPI (Python 3.14)
- **ORM:** SQLModel (Pydantic + SQLAlchemy 2.0)
- **Database:** PostgreSQL (Async via `asyncpg`)
- **Migrations:** Alembic
- **Auth:** JWT (Python-JOSE) & Argon2 hashing.

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

Access the API documentation at: `http://127.0.0.1:8000/docs`

---

## 📐 Architecture

The project follows a layered architecture to ensure maintainability and testability.

- **`app/api`**: HTTP routes and request validation (Pydantic Schemas).
- **`app/services`**: Business logic and workflow enforcement.
- **`app/models`**: Database table definitions (SQLModel).
- **`app/core`**: Configuration, security, and global utilities.

---

## 🗺️ Roadmap

- [x] Project Setup & Async DB Configuration
- [x] Domain Models (User, Flight, AuditLog)
- [ ] Authentication & Authorization (RBAC)
- [ ] Flight Lifecycle Services (Approval/Voiding logic)
- [ ] Audit Logging Implementation
- [ ] React Frontend (Thin Client)

---

## 👨‍💻 Author

**Helmi Touati**

- _Helicopter Pilot & Software Engineering._
- [LinkedIn](https://www.linkedin.com/in/helmi-touati-451518273) | [GitHub](https://github.com/touatizh)

---

## 📜 License

This project is licensed under the MIT License.
