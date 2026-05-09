# Local Development Guide

Run the full application stack locally using Docker Compose.

## Prerequisites

- Docker Desktop 4.0+
- Git
- 4GB+ available RAM

## Quick Start

### 1. Environment Setup

```bash
# Copy example environment file
cp docker/.env.example docker/.env

# Edit configuration
# - Set your API keys
# - Adjust ports if needed
# - Configure database passwords
```

### 2. Start Services

```bash
# From repository root
docker compose -f docker/docker-compose.yaml up -d

# Or use helper script
bash scripts/services/run-ems-web.sh
```

### 3. Verify Services

| Service | URL | Purpose |
|---------|-----|---------|
| Expense Manager API | <http://localhost:8000> | Backend API |
| Bella Chat API | <http://localhost:8001> | AI chat service |
| Keys UI | <http://localhost:5000> | Web interface |
| PostgreSQL | localhost:5432 | Database |

### 4. View Logs

```bash
# All services
docker compose -f docker/docker-compose.yaml logs -f

# Specific service
docker compose -f docker/docker-compose.yaml logs -f expense-manager-service
```

### 5. Stop Services

```bash
docker compose -f docker/docker-compose.yaml down

# Remove volumes (clears data)
docker compose -f docker/docker-compose.yaml down -v
```

## Service Profiles

Choose which services to run based on your needs:

### Minimal (Expense Manager only)

```bash
# Resources: ~2GB RAM
# Ports: 5432, 8000

docker compose -f docker/docker-compose.yaml up -d expense-manager-service db
```

### Standard (Recommended)

```bash
# Resources: ~4GB RAM
# Ports: 5432, 6333, 8000, 8001, 5000

docker compose -f docker/docker-compose.yaml up -d
```

### Full (All services + Monitoring)

```bash
# Resources: ~6GB RAM
# Additional: ChromaDB, Ollama, Monitoring

docker compose -f docker/docker-compose.yaml up -d
```

## Helper Scripts

Located in `scripts/services/`:

| Script | Purpose |
|--------|---------|
| `run-ems-web.sh` | Run Expense Manager + Web UI |
| `run-ems-desktop.sh` | Run EMS with desktop settings |
| `run-bella-web.sh` | Run Bella Chat + Web UI |
| `run-bella-desktop.sh` | Run Bella with desktop settings |

## Configuration

### Environment Variables

Key settings in `docker/.env`:

```bash
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=expense_manager

# API Keys
OPENAI_API_KEY=sk-...           # For AI features
ANTHROPIC_API_KEY=sk-ant-...    # Alternative AI

# Ports (change if conflicts)
EMS_PORT=8000
BELLA_CHAT_PORT=8001
KEYS_UI_PORT=5000
```

### Volume Mounts

Data persists in named volumes:

- `postgres_data` - Database files
- `chroma_data` - Vector store
- `ollama_data` - Local models

## Development Workflow

### 1. Start Infrastructure

```bash
docker compose -f docker/docker-compose.yaml up -d db chroma
```

### 2. Run Services Locally

For active development, run services outside Docker:

```bash
# Terminal 1: Expense Manager Service
cd services/expense-manager-service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Keys UI
cd keys-personal-assist-ui
npm install
npm run dev
```

### 3. Database Migrations

```bash
# Run migrations in container
docker compose -f docker/docker-compose.yaml exec expense-manager-service alembic upgrade head
```

## Troubleshooting

### Port Conflicts

```bash
# Check what's using port 8000
lsof -i :8000

# Change in docker/.env
EMS_PORT=8001
```

### Database Connection Issues

```bash
# Reset database
docker compose -f docker/docker-compose.yaml down -v
docker compose -f docker/docker-compose.yaml up -d db
```

### Out of Memory

```bash
# Reduce to minimal profile
docker compose -f docker/docker-compose.yaml up -d expense-manager-service db

# Or increase Docker Desktop memory limit
```

## Next Steps

- [CI/CD Pipeline](./ci-cd-pipeline.md) - Production deployment
- [Electron App](./electron-app.md) - Desktop distribution
- [Troubleshooting](./troubleshooting.md) - Common issues
