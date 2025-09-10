
# Expense Manager Service Architecture

## 1. Folder Structure (Backend)

```text
expense_manager_service/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── entities/
│   │   ├── errors/
│   │   │   ├── accounts.py
│   │   │   ├── base.py
│   │   │   └── spending_account.py
│   │   ├── models/
│   │   │   ├── accounts.py
│   │   │   ├── base.py
│   │   │   └── spending_account.py
│   │   ├── repositories/
│   │   │   ├── accounts.py
│   │   │   └── spending_account.py
│   ├── infrastructures/
│   │   ├── inmemory_db/
│   │   │   ├── accounts.py
│   │   │   └── spending_account.py
│   │   └── sqlite_db/
│   │       ├── accounts.py
│   │       ├── database.py
│   │       └── spending_account.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── endpoints/
│   │   │   │   ├── accounts.py
│   │   │   │   └── spending_account.py
│   │   │   ├── schemas/
│   │   │   │   ├── accounts.py
│   │   │   │   ├── base.py
│   │   │   │   ├── errors.py
│   │   │   │   └── spending_account.py
│   │   │   └── services.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── config.py
│   │   └── dev.py
│   ├── use_cases/
│   │   ├── accounts.py
│   │   ├── spending_account.py
│   │   ├── dto/
│   │   │   ├── accounts.py
│   │   │   ├── base.py
│   │   │   └── spending_account.py
│   │   ├── errors/
│   │   │   └── accounts.py
│   │   ├── mappers/
│   │   │   ├── accounts.py
│   │   │   └── spending_account.py
│   │   └── errors/
│   │       └── base.py
├── tests/
├── pyproject.toml
├── README.md
├── ruff.toml
├── uv.lock
├── expense_manager.db
```

## 2. Layered Architecture & File-Level Details

The backend follows Clean Architecture principles, with each layer mapped to specific folders and files:

### Domain Layer (`app/entities/`)

- **Purpose:** Core business logic, domain models, and error definitions.
- **Key Files:**
  - `models/accounts.py`, `models/spending_account.py`: Define immutable business entities (e.g., `AccountName`, `SpendingAccountEntry`).
  - `models/base.py`: Base entity with common fields (e.g., `id`).
  - `errors/`: Custom exceptions for domain errors (e.g., `AccountNotFoundError`).
  - `repositories/`: Abstract repository interfaces (e.g., `AccountRepositoryInterface`).

### Use Cases Layer (`app/use_cases/`)

- **Purpose:** Application-specific business logic, orchestration, and DTOs.
- **Key Files:**
  - `accounts.py`, `spending_account.py`: Service classes encapsulating business use cases (e.g., `AccountService`).
  - `dto/`: Data Transfer Objects for use case input/output (e.g., `AccountNameDTO`).
  - `mappers/`: Convert between entities and DTOs.
  - `errors/`: Use-case-specific errors, distinct from domain errors.

### Infrastructure Layer (`app/infrastructures/`)

- **Purpose:** External system integration, persistence, and adapters.
- **Key Files:**
  - `inmemory_db/`: In-memory repository implementations for testing/dev.
  - `sqlite_db/`: SQLite repository implementations and DB config (e.g., `accounts.py`, `database.py`).

### Presentation/API Layer (`app/routers/`)

- **Purpose:** API endpoints, request/response schemas, and routing.
- **Key Files:**
  - `v1/endpoints/`: FastAPI routers for each resource (e.g., `accounts.py`).
  - `v1/schemas/`: Pydantic schemas for API requests/responses.
  - `v1/services.py`: Dependency injection for repositories/services.

### Configuration Layer (`app/settings/`)

- **Purpose:** Environment and application configuration.
- **Key Files:**
  - `base.py`, `dev.py`, `config.py`: Settings for different environments, loaded via Pydantic.

### Entrypoint

- **`main.py`**: FastAPI app initialization, middleware, and startup logic.

### Tests

- **`tests/`**: Unit and integration tests for all layers.

## 4. Technology Stack & Rationale

- **Python 3.12+**: Modern language features and type safety.
- **FastAPI**: High-performance, async web framework for building APIs.
- **Pydantic v2**: Data validation and settings management.
- **SQLAlchemy (async)**: Async ORM for database access (SQLite).
- **Uvicorn**: ASGI server for running FastAPI apps.
- **Ruff**: Linting and code quality.
- **Clean Architecture**: Promotes separation of concerns, testability, and maintainability.
- **In-memory & SQLite Repositories**: Support for both development/testing and production persistence.

## Notes & Best Practices

- **Dependency Rule:** Outer layers (API, Infrastructure) depend on inner layers (Use Cases, Entities), never the reverse.
- **Extensibility:** Add new features by extending the appropriate layer, maintaining separation of concerns.
- **Configuration:** Environment-specific settings are managed in `settings/` and `.env` files.
- **Testing:** All tests are in `tests/`.

> This structure ensures maintainability, testability, and clear separation of concerns as the service evolves.

## Shangar Notes

- DTO is not required here as the job is done by Pydantic models in the schema layer.
