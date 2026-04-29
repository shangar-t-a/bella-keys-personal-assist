# Bella Keys Personal Assistant — Workspace Instructions

Personal management suite for Shangar (Keys) Arivazhagan. Monorepo with two apps:
- **Expense Manager** — tracks spending accounts and monthly expenses
- **Bella Chat** — RAG-based LLM chatbot fed by ETL pipelines from a personal GitHub repo

## Architecture

```
keys-personal-assist-ui  (port 3000, React + Vite)
    ├─ /api/ems/*       ──► expense-manager-service  (port 8000, FastAPI)
    │                              └─► postgres  (port 5432)
    └─ /api/bella-chat/* ──► bella-chat-service     (port 5000, FastAPI)
                                       ├─► qdrant   (port 6333)
                                       └─► phoenix  (port 6006, optional)
```

The UI uses relative API paths — Vite proxies in dev, nginx proxies in production. All services share a `bella-keys-network` Docker bridge.

`expense-manager-service` follows **Clean Architecture**:
- `app/entities/` — domain models, repository interfaces, domain errors
- `app/use_cases/` — business logic, use-case errors
- `app/infrastructures/` — storage adapters (inmemory, sqlite, postgres)
- `app/routers/v1/` — HTTP layer: endpoints, schemas, mappers, DI via `services.py`
- `app/settings/` — pydantic-settings config; `get_settings()` is a cached singleton

`bella-chat-service` structure: `app/agents/`, `app/core/`, `app/dependencies/`, `app/routers/`, `app/settings/`

## Tech Stack

| Layer | Tech |
|---|---|
| Backend | Python 3.13+, FastAPI, Pydantic v2, SQLAlchemy async, Alembic |
| AI/LLM | LangChain, LangGraph, Qdrant, HuggingFace embeddings, Ollama / Gemini |
| Frontend | React 19, TypeScript 5.9, Vite 7, Material UI v6, React Router v7, Zod |
| Python tooling | `uv` (package manager), Ruff (linting), mypy (types), pytest + tox |
| Frontend tooling | `npm`, ESLint |
| Infra | Docker Compose, nginx (prod) |

## Build & Test

### All services (Docker)
```bash
# Requires root .env — see docs/requirements/env-file.md
docker-compose up -d
```

### expense-manager-service
```bash
cd services/expense-manager-service
uv sync
uv run uvicorn app.main:app --reload   # dev server
uv run pytest                          # tests with coverage
uv run tox                             # lint + type check + test (isolated)
uv run tox -e lint|type|test           # individual checks
```

### bella-chat-service
```bash
cd services/bella-chat-service
uv sync
docker-compose up -d          # starts qdrant (required first)
uv run python app/main.py     # not yet containerized in root compose
uv run pytest
uv run tox
```

### keys-personal-assist-ui
```bash
cd keys-personal-assist-ui
npm install --legacy-peer-deps   # --legacy-peer-deps required (MUI v6 + React 19)
npm run dev                      # dev server → http://localhost:3000
npm run build
```

## Conventions

- **API versioning**: all routes under `/v1/`
- **Python packages**: version in `app/__init__.py`, built with hatchling
- **Local wheel**: `utilities` lib shipped as `.whl` in `py_dependencies/`; referenced in `pyproject.toml` by path
- **Test layout**: `tests/unit/` and `tests/integration/`, each with own `conftest.py`
- **Frontend alias**: `@/` → `src/`; pages in `src/pages/`, components in `src/components/`
- **Currency**: INR throughout the UI
- **Theme**: teal / emerald-cyan gradient; MUI primary color defined in `src/theme/theme.ts`
- **Chunk budget**: `vendor-markdown` (~780 KB) is lazy-loaded on chat page only; Vite chunk warning limit raised to 800 KB

## Environment

Copy and fill `.env` at repo root. Key groups:

| Prefix | Purpose |
|---|---|
| `EMS_PG_DB_*` | Postgres credentials for expense-manager-service |
| `EMS_*` | Expense manager runtime settings (host, port, storage type, DB URL) |
| `BCS_*` | Bella chat service settings |
| `SYNTHESIS_MODEL_PROVIDER/NAME` | LLM provider (`ollama` or `gemini`) |
| `EMBEDDING_MODEL_PROVIDER/NAME/DIMENSION` | Embedding model config |
| `GOOGLE_API_KEY` | Gemini API key |
| `OLLAMA_URL` | Ollama server URL |
| `QDRANT_URL` + `QDRANT_COLLECTION_NAME` | Qdrant connection |
| `ARIZE_ENABLED` + `ARIZE_*` | Arize Phoenix tracing (opt-in, needs its own Postgres) |

See [docs/requirements/env-file.md](../docs/requirements/env-file.md) for the full reference.

## Pitfalls

- `--legacy-peer-deps` is **required** for `npm install` — MUI v6 has peer conflicts with React 19
- `bella-chat-service` is **not in the root docker-compose** yet — launch manually
- `STORAGE_TYPE` for expense-manager-service: `inmemory` | `sqlite` | `postgres`
- Arize Phoenix tracing is **opt-in** — set `ARIZE_ENABLED=true` and provide its Postgres DB vars
- Both chat agents (`expense-manager-agent`, `keys-personal-wiki-agent`) are WIP
- CORS is settings-driven in both services — not hardcoded
