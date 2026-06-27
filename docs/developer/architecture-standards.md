# Architecture & Backend Coding Standards

This document details the monorepo technology stack, system architecture guidelines, clean architecture layered structures, and Python backend coding/linting standards.

---

## 1. System Technology Stack

| Layer | Technology |
| --- | --- |
| Frontend SPA | Vite + React 18 + TypeScript + MUI v6 |
| Backend Services | FastAPI + SQLAlchemy async + Pydantic v2 + Python ≥ 3.13 |
| Dependency Management | `uv` for Python services; `npm` for the UI |
| Database | PostgreSQL (via `asyncpg`) |

---

## 2. Stateless Containers

All containerized services must remain stateless.

1. Do not use Docker-managed named volumes for application data.
2. Direct all database and system connections to the host PC via `host.docker.internal`.
3. Bind mounts are permitted only for local engine caches (e.g., Qdrant).

---

## 3. Health Checks

All services must expose a `/health` endpoint. Configure the container health check in `docker-compose.yaml` using `curl`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

---

## 4. Layered Clean Architecture (Backend)

The backend services strictly follow a layered clean architecture. Each layer may only import from layers below it — **never upward**.

```txt
routers/v1/          ← HTTP boundary (FastAPI)
  schemas/           ← Pydantic HTTP request/response schemas
  mappers/           ← Pure static mapper classes (no logic)
  endpoints/         ← Thin route handlers; delegate to use cases immediately
use_cases/           ← Business logic and orchestration
  models/            ← Request/response DTOs for the use case layer
entities/            ← Core domain (pure Pydantic models, ABC interfaces)
  models/            ← Domain models; no DB or framework imports
  repositories/      ← Abstract ABC repository interfaces only
infrastructures/     ← Concrete DB implementations (SQLAlchemy)
```

### Dependency Rules

* `entities/models/` — pure Pydantic `BaseModel`. No SQLAlchemy, no FastAPI.
* `entities/repositories/` — abstract `ABC` interfaces only. One interface per domain entity.
* `use_cases/` — `*Service` classes importing only from `entities/` and `use_cases/models/`.
* `routers/v1/mappers/` — static mapper classes with `to_use_case_model()` and `to_response_model()` methods. Zero business logic.
* `routers/v1/endpoints/` — FastAPI route functions only. Inject services via `Depends()`, call the service, map response, return. No logic.

---

## 5. Python Coding & Linting Standards

### Linting

Run `ruff check` from the service root directory before staging/committing any Python file:

```bash
uv run ruff check
```

The enforced rule sets (configured in `ruff.toml`):

* `E` / `W` — pycodestyle errors and warnings
* `F` — Pyflakes (unused imports, undefined names)
* `I` — isort (import ordering)
* `B` — flake8-bugbear (likely bugs)
* `C4` — flake8-comprehensions
* `D` — pydocstyle (Google convention)
* `N` — pep8-naming
* `UP` — pyupgrade (modern Python syntax)
* `PL` — Pylint
* `SIM` — flake8-simplify
* `TC` — flake8-type-checking

* **Line length:** 120 characters maximum.
* **Scope:** `app/**/*.py` (Alembic migration versions and deprecated code excluded).

### Import Ordering

All imports must be at the **top of the file** — never inside functions or class bodies (unless guarding a circular import).
Order: **stdlib → third-party → internal `app.*`**. Group multiple names from the same module into a single parenthesized block:

```python
# ✅ Correct
from app.entities.models.asset import (
    Asset,
    AssetCategory,
    AssetFilter,
    AssetSort,
    AssetTransaction,
)

# ❌ Wrong
def some_function():
    from app.entities.models.asset import Asset
```

### Docstrings (Google Style)

Every module, class, and public method must have a Google-style docstring. Enforced by ruff `D` rules.

```python
"""Module-level docstring describing the module."""

class AssetService:
    """Service handling asset orchestration and financial calculations."""

    async def create_asset(self, asset_create: AssetCreate) -> AssetWithCalc:
        """Create a new asset and log its initial transaction."""
```

### Error Handling in Endpoints

```python
# ValueError from use case layer → 404
except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

# Broad Exception from create/update → 400
except Exception as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
```

* Always `raise HTTPException(...) from e` to preserve stack traces.

### Conventions

* **IDs:** Generate with `uuid.uuid4().hex` (compact hex string, no dashes).
* **Financial values:** Always `round(value, 2)` before persisting or returning.
* **Dependency injection:** Use FastAPI `Depends()` in endpoint signatures. Never instantiate services directly inside endpoint logic.
