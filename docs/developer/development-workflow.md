# Developer Development Workflow

This document details the development environment setup, build procedures, architecture rules, coding standards, testing principles, and release pipeline for Bella Keys.

---

## 1. Local Development Quick Start

Automate project setup and dependency synchronization (works on Linux, macOS, and Windows Git Bash):

```bash
bash scripts/setup.sh
```

This script copies env file templates, syncs all Python dependencies via `uv`, installs UI packages via `npm`, and optionally initializes local databases.

### Running Development Services

Start different development configurations (interactive or via command line arguments: `ems-web`, `bella-web`, `ems-desktop`, `bella-desktop`):

```bash
bash scripts/run-dev.sh [profile]
```

### Common Developer Tasks

* **Running Migrations:** `bash scripts/db-migrate.sh` (Alembic database schema updates).
* **Running Tests:** `bash scripts/run-tests.sh` (Pytest suite).

---

## 2. Packaging and Electron Builds

Build production installer binaries:

* **Windows:** `.\scripts\electron\build.bat`
* **Linux/macOS:** `bash scripts/electron/build.sh`

Output binaries are stored in the `dist/` directory.

---

## 3. Architecture Standards

### Tech Stack

* **Frontend SPA:** Vite + React 18 + TypeScript + MUI v6 (Refer to [ui-guidelines.md](ui-guidelines.md) for patterns).
* **Backend Services:** FastAPI + SQLAlchemy async + Pydantic v2 + Python ≥ 3.13.
* **Dependency Management:** `uv` (Python) and `npm` (UI).
* **Database:** PostgreSQL (via `asyncpg`).

### Container & Service Rules

1. **Stateless Containers:** Do not use Docker-managed named volumes for application data. Direct all DB/system connections to the host PC via `host.docker.internal`.
2. **Health Checks:** All services must expose a `/health` endpoint. Configure the container health check in `docker-compose.yaml` using `curl` check.

### Clean Architecture (Backend Layer Rules)

Backend services follow a strict layered clean architecture. Imports must flow downwards only:

```
routers/v1/          ← HTTP boundary (FastAPI schemas, mappers, endpoints)
use_cases/           ← Business logic and orchestration (Service classes & models)
entities/            ← Core domain (pure Pydantic models, ABC interfaces)
infrastructures/     ← Concrete database implementations (SQLAlchemy repositories)
```

* **Entities:** Pure Pydantic models with zero framework imports.
* **Mappers:** Static mapper classes with zero business logic.
* **Endpoints:** Thin FastAPI route handlers injecting services via `Depends()`.

---

## 4. Backend Coding Standards

### Linting & Formatting

Linter rules are configured in `ruff.toml`. Run from the service root before committing:

```bash
uv run ruff check
```

Key constraints:

* **Line Length:** 120 characters.
* **Scope:** `app/**/*.py` (Alembic versions and deprecated infra excluded).

### Import Ordering

All imports must be at the **top of the file**. Format: **stdlib → third-party → internal `app.*`**. Group multiple imports from the same parent package.

### Code Quality & Docstrings

* **Docstrings:** Use Google-style docstrings for every module, class, and public method.
* **Top-Level Imports:** All imports must reside at the top of the file. Function-level imports are prohibited unless required to prevent circular dependencies.
* **Single Responsibility:** Decompose complex functions. Methods exceeding 50 lines must be refactored.
* **Minimizing Suppressions:** Avoid file-wide or block-wide Ruff suppressions (e.g., `# ruff: noqa: PLR0912, PLR2004`) in source files. Keep suppressions restricted to unit tests.
* **Error Handling:** Always use `raise HTTPException(...) from e` to preserve the stack trace.
* **Financial values:** Always `round(value, 2)` before persisting or returning.

---

## 5. Backend Testing Standards

All tests are run via `pytest` through `bash scripts/run-tests.sh`.

### Test Setup

* **Test Database:** Tests run against a dedicated PostgreSQL database (`expense_manager_test`), not mocks, verifying the full database integration path.
* **Async Loop Scope:** Handled session-wide in `conftest.py` — do not mark individual tests.

### Test Coverage Checklist

Every new feature or use case must cover:

* **Happy Paths:** Verify standard CRUD operations return expected models and codes.
* **Recalculations:** Verify parent models' computed/cached fields (e.g. `current_value`) update correctly when children are added, edited, or deleted.
* **Edge Cases:** Zero balance, division guards, transaction boundary scenarios, unit vs value-based branching.
* **Rollbacks:** Ensure transactions that fail or are deleted cleanly rollback parent state.
* **Cleanup:** Every test must clean up its own created data.

### Fixtures Pattern

Use session-scoped repository fixtures and function-scoped service wrappers in `conftest.py`.

---

## 6. Continuous Integration & Release Pipeline

Conducted via GitHub Actions to build and publish Docker images to GHCR.

* **Build Triggers:** Only trigger on `push` to `main` when a service `VERSION` file is modified (e.g., `services/expense-manager-service/VERSION`). Standard commits do not trigger builds.
* **Security Scanning:** Trivy scans are executed on all generated images before publishing.

---

## 7. Documentation Guidelines & Reference Mapping

To keep documentation clean and maintainable:

* **Development Workflow & Standards:** [development-workflow.md](development-workflow.md)
* **UI & Frontend Coding Guidelines:** [ui-guidelines.md](ui-guidelines.md)
* **Feature Requirements & Specs:** `docs/developer/feature/<module>/<feature>.md` (e.g., [liabilities.md](feature/wealth_manager/liabilities.md))
* **Mathematical & Calculation Logic:** `docs/developer/feature/<module>/calculations.md` (e.g., [calculations.md](feature/wealth_manager/calculations.md))
* **Implementation Plans:** Temporary plans live under `.agents/plans/` or `.agents/rules/` to facilitate context discovery.
