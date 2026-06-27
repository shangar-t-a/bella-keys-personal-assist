# Developer Development Workflow

This document details the development environment setup, build procedures, architecture rules, coding standards, testing principles, and release pipeline for Bella Keys.

---

## 1. Local Development Quick Start

Automate project setup and dependency synchronization (works on Linux, macOS, and Windows Git Bash):

```bash
bash scripts/setup.sh
```

This script copies env file templates, syncs all Python dependencies via `uv`, installs UI packages via `npm`, and can optionally initialize local databases.

### Running Development Services

Use the unified developer launcher to start different development configurations (interactive or via command line arguments: `ems-web`, `bella-web`, `ems-desktop`, `bella-desktop`):

```bash
bash scripts/run-dev.sh [profile]
```

For example, to run the Expense Manager Service with Electron UI:

```bash
bash scripts/run-dev.sh ems-desktop
```

### Common Developer Tasks

* **Running Migrations:** Run `bash scripts/db-migrate.sh` to apply database schema updates via Alembic.
* **Running Tests:** Run `bash scripts/run-tests.sh` to execute the pytest suite.

---

## 2. Packaging and Electron Builds

To build production installer binaries:

* **Windows:**

  ```powershell
  .\scripts\electron\build.bat
  ```

* **Linux/macOS:**

  ```bash
  bash scripts/electron/build.sh
  ```

Output binaries are stored in the `dist/` directory.

---

## 3. Architecture Standards

### Tech Stack

| Layer | Technology |
| --- | --- |
| Frontend SPA | Vite + React 18 + TypeScript + MUI v6 |
| Backend Services | FastAPI + SQLAlchemy async + Pydantic v2 + Python ≥ 3.13 |
| Dependency Management | `uv` for Python services; `npm` for the UI |
| Database | PostgreSQL (via `asyncpg`) |

### Stateless Containers

All containerized services must remain stateless.

1. Do not use Docker-managed named volumes for application data.
2. Direct all database and system connections to the host PC via `host.docker.internal`.
3. Bind mounts are permitted only for local engine caches (e.g., Qdrant).

### Health Checks

All services must expose a `/health` endpoint. Configure the container health check in `docker-compose.yaml` using `curl`:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Clean Architecture — Backend Layer Rules

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

**Rules:**

* `entities/models/` — pure Pydantic `BaseModel`. No SQLAlchemy, no FastAPI.
* `entities/repositories/` — abstract `ABC` interfaces only. One interface per domain entity.
* `use_cases/` — `*Service` classes importing only from `entities/` and `use_cases/models/`.
* `routers/v1/mappers/` — static mapper classes with `to_use_case_model()` and `to_response_model()` methods. Zero business logic.
* `routers/v1/endpoints/` — FastAPI route functions only. Inject services via `Depends()`, call the service, map response, return. No logic.

---

## 4. Backend Coding Standards

### Linting — `ruff check` is mandatory before every commit

Run from the service root before staging any Python file:

```bash
uv run ruff check
```

The enforced rule sets (configured in `ruff.toml`):

| Rule Set | Description |
| --- | --- |
| `E` / `W` | pycodestyle errors and warnings |
| `F` | Pyflakes (unused imports, undefined names) |
| `I` | isort (import ordering) |
| `B` | flake8-bugbear (likely bugs) |
| `C4` | flake8-comprehensions |
| `D` | pydocstyle — **Google convention** |
| `N` | pep8-naming |
| `UP` | pyupgrade (modern Python syntax) |
| `PL` | Pylint |
| `SIM` | flake8-simplify |
| `TC` | flake8-type-checking |

* **Line length:** 120 characters.
* **Scope:** `app/**/*.py` (Alembic versions and deprecated infra excluded).

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

# ❌ Wrong — scattered imports or imports inside functions
def some_function():
    from app.entities.models.asset import Asset
```

### Docstrings — Google Style, Every Public Symbol

Every module, class, and public method must have a Google-style docstring. Enforced by ruff `D` rules.

```python
"""Module-level docstring describing the module."""


class AssetService:
    """Service handling asset orchestration and financial calculations."""

    async def create_asset(self, asset_create: AssetCreate) -> AssetWithCalc:
        """Create a new asset and log its initial transaction."""
```

* One-liner for simple getters/delete operations.
* Multi-line for methods with non-obvious logic.

### Error Handling in Endpoints

```python
# ValueError from use case layer → 404
except ValueError as e:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e

# Broad Exception from create/update → 400
except Exception as e:
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
```

* Always `raise HTTPException(...) from e` — never bare raise — to preserve the stack trace.

### Other Conventions

* **IDs:** Generate with `uuid.uuid4().hex` (compact hex string, no dashes).
* **Financial values:** Always `round(value, 2)` before persisting or returning.
* **Dependency injection:** Use FastAPI `Depends()` in endpoint signatures. Never instantiate services directly inside endpoint logic.

---

## 5. Backend Testing Standards

### Framework

`pytest` + `pytest-asyncio` + `pytest-cov`. All tests run via:

```bash
bash scripts/run-tests.sh
```

Async tests automatically receive `asyncio(loop_scope="session")` via the `conftest.py` hook — no manual marking required.

### Test Database

Unit tests in this project connect to a **dedicated test PostgreSQL database** (`expense_manager_test`), not mocks. The `conftest.py` `init_and_drop_db` session fixture initialises and tears down the schema. Tests exercise the full use case → repository → database path.

### Test Organization

* Group tests by domain and scenario: `class TestAssetServiceCRUD`, `class TestAssetServiceSummary`, etc.
* Every test class and method must have a Google-style docstring.
* Add `# ruff: noqa: PLR2004, E501` at the top of test files to suppress magic-number and line-length warnings (acceptable in test context only).

```python
# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager assets service use case."""
```

### Thoroughness Requirements

Every new feature use case must be covered with tests for:

| Scenario | What to verify |
| --- | --- |
| **Happy path** | Create, read, update, delete return correct values |
| **Recalculation** | Computed/cached fields update correctly after every transaction change |
| **Edge cases** | Zero invested value (division guard), no transactions (reset to zero), unit-based vs flat-based branching |
| **Rollback** | Deleting a transaction correctly reverts calculated state on the parent |
| **Self-cleanup** | Every test deletes its own created data; confirm via `pytest.raises(ValueError)` |

### Fixture Pattern

* Shared repository fixtures: `scope="session"` in `conftest.py`.
* Per-test service fixtures: default (function) scope, wrapping the session-scoped repo.
* Seed data helpers: module-level async functions (not fixtures), called inside tests that need them.

```python
@pytest.fixture
def asset_service(asset_repo):
    """Provide an instance of AssetService."""
    return AssetService(asset_repository=asset_repo)
```

---

## 6. General Coding and Commenting Standards

### Comment Style Standard

All code comments in any language (Python, TypeScript, CSS, HTML, JSX/TSX, etc.) must remain simple, clean, and undecorated. Never use visual delimiters, horizontal lines, trailing dashes, or custom block dividers (such as `# ---* comment --------` or `// ── comment ──`). Comments should simply be `# comment`, `// comment`, or `/* comment */`.

---

## 7. Frontend Coding Standards

### API Calls — Always Use `fetchWithAuth`

Never use raw `fetch` or `axios` for authenticated endpoints. Use `fetchWithAuth` from `src/api/clients/fetchClient.ts`:

```typescript
// ✅ Correct
const response = await fetchWithAuth(`${emsBase}/assets`);

// ❌ Wrong
const response = await fetch(`${emsBase}/assets`, {
  headers: { Authorization: `Bearer ${token}` },
});
```

`fetchWithAuth` automatically attaches the Bearer token, performs **silent token refresh on 401**, and retries the original request.

### Authentication Pattern

`AuthContext` (`src/context/AuthContext.tsx`) is the single source of truth for React auth state. `localStorage` is the persistence layer only.

**On app mount:**

1. If a `refresh_token` exists in `localStorage` → call `/refresh`.
2. On success: store new tokens, update React state.
3. On network failure: fall back to expiry check of the existing `access_token`.
4. On no refresh token: log out immediately.

**Cross-layer auth sync** uses a custom window event bus — avoiding any direct import between the fetch layer and React context:

* `window.dispatchEvent(new Event('auth-logout'))` → triggers `logout()` in `AuthContext`.
* `window.dispatchEvent(new CustomEvent('auth-refresh', { detail: { access_token } }))` → syncs new token into `AuthContext` state.

### UI Component Standards

**Never use `window.confirm` or `window.alert`** for destructive actions. Always use a custom in-app MUI `<Dialog>`.

**Custom confirm dialog pattern** (reusable recipe):

```tsx
const [confirmDialog, setConfirmDialog] = useState<{
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
}>({ open: false, title: '', message: '', onConfirm: () => {} });

const openConfirm = (title: string, message: string, onConfirm: () => void) => {
  setConfirmDialog({ open: true, title, message, onConfirm });
};

const closeConfirm = () => {
  setConfirmDialog((prev) => ({ ...prev, open: false }));
};
```

Render the dialog at the end of the component JSX (outside any primary dialog if nesting is needed).

**`<DialogContent>` layout fix** — wrap fields in a `<Box>` to prevent MUI floating label clipping:

```tsx
// ✅ Correct
<DialogContent>
  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
    <TextField ... />
  </Box>
</DialogContent>

// ❌ Wrong — applies flex directly on DialogContent, which clips labels
<DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
  <TextField ... />
</DialogContent>
```

**Required field labels** — MUI `<TextField required>` auto-appends the asterisk. Do not manually add `*` to the `label` prop.

```tsx
// ✅ Correct
<TextField required label="Asset Name" />

// ❌ Wrong
<TextField required label="Asset Name *" />
```

### Build Verification — Mandatory Before Committing UI Changes

```bash
npm run build:web
```

TypeScript must compile with **zero errors** before staging any UI file. No `any` suppressions without an inline comment justification.

---

## 8. Continuous Integration and Release Pipeline

The project utilizes GitHub Actions for building and publishing Docker images to the GitHub Container Registry (GHCR).

### Build Triggers

To prevent registry clutter and control costs:

* Builds do not trigger on standard source code commits.
* Builds only trigger on `push` to `main` when a service `VERSION` file is modified (e.g., `services/expense-manager-service/VERSION`).

### Security Scanning

The build pipeline scans all generated images for high and critical vulnerabilities using Trivy before publishing.

### Release Notes Standard (Monorepo Unified Changelog)

To manage independent release schedules across different services and applications, the project maintains a single root `CHANGELOG.md` document tracking changes chronologically.

Developers must adhere to the following release notes standards:

1. **Header Format**: Every entry must use the component-prefixed version header format:
   `## [<component-name>@<version>] - YYYY-MM-DD`
   Example: `## [expense-manager-service@1.4.0] - 2026-06-26`
2. **Professional Language**: Do not include emojis in the release notes or titles. Maintain a clean, professional, and industry-standard tone.
3. **Change Classification**: Categorize changes under the standard Keep a Changelog taxonomy:
   * `Added` for new features.
   * `Changed` for modifications of existing behavior.
   * `Deprecated` for features slated for removal.
   * `Removed` for deleted features.
   * `Fixed` for bug resolutions.
   * `Security` for security patches.
