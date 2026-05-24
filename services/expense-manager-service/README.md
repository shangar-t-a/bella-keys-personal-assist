# Expense Manager Service

Keys' personal expense manager service built with FastAPI, following Clean Architecture principles.

- [Expense Manager Service](#expense-manager-service)
  - [1. Folder Structure (Backend)](#1-folder-structure-backend)
  - [2. Layered Architecture \& File-Level Details](#2-layered-architecture--file-level-details)
    - [Domain Layer (`app/entities/`)](#domain-layer-appentities)
    - [Use Cases Layer (`app/use_cases/`)](#use-cases-layer-appuse_cases)
    - [Infrastructure Layer (`app/infrastructures/`)](#infrastructure-layer-appinfrastructures)
    - [Presentation/API Layer (`app/routers/`)](#presentationapi-layer-approuters)
    - [Configuration Layer (`app/settings/`)](#configuration-layer-appsettings)
    - [Entrypoint](#entrypoint)
    - [Tests](#tests)
  - [4. Technology Stack \& Rationale](#4-technology-stack--rationale)
  - [Notes \& Best Practices](#notes--best-practices)
  - [5. Hybrid Architecture \& Networking](#5-hybrid-architecture--networking)

## 1. Folder Structure (Backend)

```text
expense-manager-service/
├── .coveragerc                                              # Test coverage config
├── .dockerignore                                            # Docker ignore file
├── .env                                                     # Environment variables (for local development)
├── .env.sample                                              # Sample env file for reference
├── .gitignore                                               # Git ignore file
├── Dockerfile                                               # Dockerfile for containerizing the app
├── mypy.ini                                                 # Mypy config (static type checking)
├── pyproject.toml                                           # Project metadata and dependencies
├── pytest.ini                                               # Pytest configurations
├── README.md                                                # Project documentation
├── ruff.toml                                                # Ruff config (linting)
├── tox.ini                                                  # Tox config (testing in isolated environments)
├── uv.lock                                                  # UV lock file (dependency management)
├── app/                                                     # Main application code
│   ├── __init__.py
│   ├── main.py                                              # FastAPI app entrypoint
│   ├── entities/                                            # Domain layer
│   │   ├── errors/                                          # Domain errors, one file per resource
│   │   ├── models/                                          # Domain models, one file per resource
│   │   │   ├── base.py                                      # Shared frozen Pydantic base
│   │   │   ├── sort.py                                      # Generic SortOrder enum (asc/desc)
│   │   │   ├── *.py                                         # account, period, spending_entry, monthly_planner models
│   │   │                                                    #   spending_entry also holds sort, filter,
│   │   │                                                    #   and JOIN-enriched detail models
│   │   └── repositories/                                    # Abstract repository interfaces, one file per resource
│   ├── infrastructures/                                     # Infrastructure layer (external systems)
│   │   ├── inmemory_db/                                     # ⚠️ DEPRECATED - retained for reference, not supported
│   │   ├── sqlite_db/                                       # ⚠️ DEPRECATED - retained for reference, not supported
│   │   └── postgres_db/                                     # Sole supported backend
│   │       ├── alembic/                                     # Alembic migrations
│   │       ├── alembic.ini                                  # Alembic config
│   │       ├── models/                                      # SQLAlchemy ORM models (account, period, spending_entry, monthly_planner)
│   │       ├── database.py                                  # Engine, session factory, Base, init_db/drop_db (for tests)
│   │       └── *.py                                         # Postgres repository implementations
│   ├── routers/                                             # Presentation/API layer
│   │   ├── v1/                                              # API version 1
│   │   │   ├── endpoints/                                   # FastAPI routers, one file per resource
│   │   │   ├── mappers/                                     # Schema <-> domain/use-case model converters
│   │   │   ├── schemas/                                     # Pydantic request/response schemas
│   │   │   │   ├── base.py                                  # Shared BaseSchema (camelCase aliases)
│   │   │   │   ├── pagination.py                            # PaginationParams and PaginationResponse
│   │   │   │   └── *.py                                     # Per-resource schemas incl. sort/filter params
│   │   │   ├── services.py                                  # Dependency injection
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── settings/                                            # Configuration layer
│   │   ├── base.py                                          # Base settings
│   │   ├── config.py                                        # Config loader
│   │   ├── dev.py                                           # Development settings
│   │   └── __init__.py
│   └── use_cases/                                           # Use Cases layer (Business logic)
│       ├── *.py                                             # Service classes, one per resource (account, period, spending_entry, monthly_planner)
│       ├── errors/                                          # Use-case errors, one file per resource
│       └── models/                                          # Flattened use-case models
│           ├── base.py                                      # Shared frozen Pydantic base
│           ├── pagination.py                                # Page - pagination metadata
│           └── spending_entry.py                            # Spending entry input/output models
├── docs/                                                    # Documentation
├── tests/                                                   # Test cases
│   ├── conftest.py                                          # Pytest configurations at root
│   ├── integration/                                         # Integration tests
|   |   ├── conftest.py                                      # Pytest configurations at integration test level
│   │   └── routers/
│   │       └── v1/
│   └── unit/                                                # Unit tests
│       ├── conftest.py                                      # Pytest configurations at unit test level
│       ├── settings.py
│       └── use_cases/
```

## 2. Layered Architecture & File-Level Details

The backend follows Clean Architecture principles, with each layer mapped to specific folders and files:

### Domain Layer (`app/entities/`)

- **Purpose:** Core business logic, domain models, and error definitions.
- **Key Files:**
  - `models/`: One file per resource plus a shared `base.py` (frozen Pydantic base with camelCase aliases) and `sort.py` (generic `asc`/`desc` enum). The `spending_entry` model file also contains JOIN-enriched detail models and domain objects for sort and filter.
  - `errors/`: Custom domain exceptions, one file per resource.
  - `repositories/`: Abstract interfaces that all storage adapters must implement, one file per resource.

### Use Cases Layer (`app/use_cases/`)

- **Purpose:** Application-specific business logic and orchestration.
- **Key Files:**
  - Service files (`account.py`, `period.py`, `spending_entry.py`, `monthly_planner.py`) - one service class per resource. `SpendingEntryService` handles paginated listing with sort and filter. `MonthlyPlannerService` handles summaries, expenses, and categories.
  - `models/` - flattened output models that decouple the router from entity internals. Includes `pagination.py` with the shared `Page` model.
  - `errors/` - use-case errors, kept separate from domain errors, one file per resource.

### Infrastructure Layer (`app/infrastructures/`)

- **Purpose:** External system integration, persistence, and adapters.
- **Key Files:**
  - `postgres_db/` **(sole supported backend)** - async SQLAlchemy repository implementations for account, period, spending entry, and monthly planner. The spending entry repository executes a JOIN query to return enriched results; sort and filter are applied at the DB level. `alembic/` holds the migration chain. `models/` holds the ORM models.
  - `inmemory_db/` and `sqlite_db/` - ⚠️ **Deprecated since February 2026.** Code retained for reference. Selecting either storage type raises a `ValueError` at runtime.

### Presentation/API Layer (`app/routers/`)

- **Purpose:** API endpoints, request/response schemas, and routing.
- **Key Files:**
  - `v1/endpoints/` - CRUD endpoints for account, period, spending entry, and monthly planner. `GET /spending_account/list` accepts query parameters for sorting, filtering, and pagination. `monthly_planner` endpoints manage the expense manager dashboard features (e.g. `GET /v1/monthly-planner/summary/{year}/{month}`).
  - `v1/schemas/` - Pydantic schemas per resource. `base.py` provides the shared camelCase alias base. `pagination.py` provides reusable `PaginationParams` and `PaginationResponse`. Spending entry schemas include dedicated sort and filter param schemas.
  - `v1/mappers/` - Converts HTTP schema objects to domain/use-case models. Includes a query-params mapper that translates sort and filter params into domain objects.
  - `v1/services.py` - Dependency injection. Only `postgresql` is wired; `inmemory` and `sqlite` raise a `ValueError`.

### Configuration Layer (`app/settings/`)

- **Purpose:** Environment and application configuration.
- **Key Files:**
  - `base.py`, `dev.py`, `config.py`: Settings for different environments, loaded via Pydantic.

### Entrypoint

- **`main.py`**: FastAPI app initialization, middleware, and startup logic.

### Tests

- **`tests/`**: Unit and integration tests for all layers.

#### Running Tests

Before running tests, you must initialize the test database and user in your local PostgreSQL instance on the host PC (since it follows the hybrid "inside-out" architecture):

1. Connect to your local PostgreSQL server as the superuser (`postgres`).
2. Run the following SQL commands to create the test user and database:
   ```sql
   CREATE USER ems_test_user WITH ENCRYPTED PASSWORD 'test123';
   CREATE DATABASE expense_manager_test OWNER ems_test_user;
   ```
3. Run the tests using `uv`:
   ```bash
   uv run pytest
   ```


## 4. Technology Stack & Rationale

- **Python 3.14+**: Backend technology.
- **FastAPI**: High-performance, async web framework for building APIs.
- **Pydantic**: Data validation and settings management.
- **SQLAlchemy (async)**: Async ORM for database access (PostgreSQL).
- **Alembic (async)**: Database migrations.
- **Uvicorn**: ASGI server for running FastAPI apps.
- **UV**: Dependency management.
- **Mypy**: Static type checking.
- **Pytest**: Testing framework.
- **Tox**: Testing in isolated environments.
- **Ruff**: Linting and code quality.
- **Clean Architecture**: Promotes separation of concerns, testability, and maintainability.
- **PostgreSQL Repository (only)**: Sole supported persistence backend. SQLite and in-memory adapters are retained in the codebase but deprecated as of February 2026.

## Notes & Best Practices

- **Dependency Rule:** Outer layers (API, Infrastructure) depend on inner layers (Use Cases, Entities), never the reverse.
- **Storage type:** `STORAGE_TYPE` must be set to `postgresql` in `.env`. Setting it to `inmemory` or `sqlite` raises a `ValueError` at startup - those adapters are deprecated and no longer wired.
- **Sort & filter:** `GET /v1/spending_account/list` accepts `sort_by`, `sort_order`, `month`, `year`, and `account_name` as query parameters. Sorting and filtering are applied at the DB level.
- **Pagination:** Spending entry list endpoints use `page`/`size` query parameters and return a `PaginationResponse` in the body.
- **File splitting:** Each resource (account, period, spending_entry, monthly_planner) has its own file across every layer - models, errors, repositories, use cases, schemas, and endpoints.
- **Extensibility:** Add new features by extending the appropriate layer, maintaining separation of concerns.
- **Configuration:** Environment-specific settings are managed in `settings/` and `.env` files.
- **Testing:** All tests are in `tests/`.

## 5. Hybrid Architecture & Networking

This service follows the project-wide **Hybrid "Inside-Out" Architecture**. When running in Docker, it does **not** provide its own database. Instead, it is configured to reach out to the host PC (via `host.docker.internal`) to find its PostgreSQL instance. This allows you to manage your data locally while keeping the application logic containerized.

> This structure ensures maintainability, testability, and clear separation of concerns as the service evolves.
