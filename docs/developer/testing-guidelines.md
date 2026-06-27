# Backend Testing Guidelines

This document details the testing framework, test database configuration, test organization, and coverage standards for backend services.

---

## 1. Testing Framework

The project uses `pytest` + `pytest-asyncio` + `pytest-cov`. Run tests using the unified test execution script:

```bash
bash scripts/run-tests.sh
```

- **Async scope:** Async tests automatically receive `asyncio(loop_scope="session")` via the `conftest.py` hook. No manual annotation or marking is needed.

---

## 2. Test Database Configuration

Unit/integration tests connect to a **dedicated test PostgreSQL database** (`expense_manager_test`) rather than using mocks.

- The `conftest.py` file exposes an `init_and_drop_db` session-scoped fixture to handle initial schema creation and teardown.
- Tests exercise the full execution path: `use case` → `repository` → `database`.

---

## 3. Test Organization

- Group tests by domain and scenario inside classes: e.g. `class TestAssetServiceCRUD`, `class TestAssetServiceSummary`.
- Every test class and test function/method must have a Google-style docstring.
- Add `# ruff: noqa: PLR2004, E501` at the top of test files to suppress magic-number and line-length warnings (permitted strictly in test scopes).

```python
# ruff: noqa: PLR2004, E501
"""Unit tests for the wealth manager assets service use case."""
```

---

## 4. Scenario Coverage Requirements

Every new use case/endpoint scenario must be covered by unit/integration tests verifying:

| Scenario | Validation Target |
| --- | --- |
| **Happy path** | Verify CRUD operations execute successfully and return correct models. |
| **Recalculation** | Check computed/cached fields are correctly re-evaluated after database mutations. |
| **Edge cases** | Division by zero guards (e.g. zero value metrics), empty records, compounding variations. |
| **Rollback** | Verify transaction deletion correctly reverts calculated status on the parent entity. |
| **Self-cleanup** | Test entities must be cleaned up after execution (verified via `pytest.raises`). |

---

## 5. Fixture Patterns

- **Shared repositories:** Configure with `scope="session"` in `conftest.py`.
- **Per-test service instances:** Default function scope, wrapping the session-scoped repositories.
- **Seed data helpers:** Write as module-level async functions (not pytest fixtures), called explicitly inside tests that need pre-populated state.

```python
@pytest.fixture
def asset_service(asset_repo):
    """Provide an instance of AssetService."""
    return AssetService(asset_repository=asset_repo)
```
