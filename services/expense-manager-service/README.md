# Expense Manager Service

Backend microservice built with FastAPI, following Clean Architecture principles.

## 1. Folder Structure

```text
expense-manager-service/
├── Dockerfile                                               # Dockerfile for containerizing the app
├── pyproject.toml                                           # Project metadata and dependencies
├── uv.lock                                                  # UV lock file
├── app/                                                     # Main application code
│   ├── main.py                                              # FastAPI app entrypoint
│   ├── entities/                                            # Domain layer
│   │   ├── errors/                                          # Domain errors
│   │   ├── models/                                          # Domain models (account, period, spending_entry, monthly_planner, savings_bucket)
│   │   └── repositories/                                    # Abstract repository interfaces
│   ├── infrastructures/                                     # Infrastructure layer
│   │   ├── postgres_db/                                     # PostgreSQL database access layer
│   │   │   ├── alembic/                                     # Alembic migrations
│   │   │   ├── models/                                      # SQLAlchemy ORM models
│   │   │   └── database.py                                  # Engine and session initialization
│   ├── routers/                                             # Presentation/API layer
│   │   ├── v1/
│   │   │   ├── endpoints/                                   # FastAPI routers
│   │   │   ├── mappers/                                     # Request/response mappers
│   │   │   ├── schemas/                                     # Pydantic schemas
│   │   │   └── services.py                                  # Dependency injection setup
│   ├── settings/                                            # Configuration settings
│   └── use_cases/                                           # Use case layer (business logic)
│       ├── errors/                                          # Use case errors
│       ├── models/                                          # Use case schemas/models
│       └── *.py                                             # Core service modules (account, period, spending_entry, monthly_planner, savings_bucket)
└── tests/                                                   # Test suites
```

---

## 2. Layered Architecture

The service adheres to Clean Architecture principles:

* **Domain Layer (`app/entities/`):** Defines core business models, custom domain exceptions, and repository interfaces. Contains no dependencies on external libraries or frameworks.
* **Use Cases Layer (`app/use_cases/`):** Contains application-specific business logic. Orchestrates flow between domain entities and repository interfaces.
* **Infrastructure Layer (`app/infrastructures/`):** Handles persistence and external communication. Implements repository interfaces via asynchronous SQLAlchemy and PostgreSQL. Database migrations are managed via Alembic.
* **Presentation/API Layer (`app/routers/`):** Handles HTTP request validation, routing, error handling, and response mapping.

---

## 3. Local Test Environment

To run the test suite, initialize the test database in your local host PostgreSQL instance:

1. Connect to PostgreSQL:
   ```sql
   CREATE USER ems_test_user WITH ENCRYPTED PASSWORD 'test123';
   CREATE DATABASE expense_manager_test OWNER ems_test_user;
   ```
2. Execute tests:
   ```bash
   uv run pytest
   ```

---

## 4. Key Configurations

* **Storage Type:** Set `STORAGE_TYPE=postgresql` in `.env`.
* **Hybrid Networking:** When containerized, the service resolves the host database using `host.docker.internal:5432`.
