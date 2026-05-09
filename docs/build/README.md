# Build & Run Guide

Complete guide for building, running, and deploying the Bella Keys Personal Assist application.

## Quick Start

### Run Locally with Docker

```bash
# 1. Clone and navigate
git clone <repo-url>
cd bella-keys-personal-assist

# 2. Configure environment
cp docker/.env.example docker/.env
# Edit docker/.env with your settings

# 3. Start services
docker compose -f docker/docker-compose.yaml up -d

# 4. Access application
# Web UI: http://localhost:5000
# API: http://localhost:8000
```

### Build for Production

See [CI/CD Pipeline](./ci-cd-pipeline.md) for automated builds via GitHub Actions.

### Build Electron Desktop App

```bash
# Linux/macOS
bash scripts/electron/build.sh

# Windows
scripts\electron\build.bat
```

## Documentation Sections

| Document | Purpose |
|----------|---------|
| [Local Development](./local-development.md) | Docker Compose setup for local development |
| [CI/CD Pipeline](./ci-cd-pipeline.md) | GitHub Actions workflows, GHCR image publishing |
| [Electron App](./electron-app.md) | Desktop app build and distribution |
| [Scripts Reference](./scripts-reference.md) | All build/run scripts catalog |
| [Troubleshooting](./troubleshooting.md) | Common issues and solutions |

## Build Artifacts

| Type | Location | Documentation |
|------|----------|---------------|
| Docker Images | `ghcr.io/<owner>/*` | [CI/CD Pipeline](./ci-cd-pipeline.md) |
| Electron App | `dist/` | [Electron App](./electron-app.md) |
| Local Services | Docker Compose | [Local Development](./local-development.md) |

## Scripts Overview

All scripts are organized by purpose:

```
scripts/
├── electron/          # Desktop app build/run
├── docker/            # Service run scripts
└── README.md          # Script index
```

See [Scripts Reference](./scripts-reference.md) for detailed usage.

## Architecture Overview

### Services

- **Expense Manager Service** - Backend API for expense tracking
- **Bella Chat Service** - AI conversational interface
- **EMS MCP Server** - Model Context Protocol server
- **Keys Personal Assist UI** - Frontend web application

### Build Targets

| Target | Method | Use Case |
|--------|--------|----------|
| Local Dev | Docker Compose | Development, testing |
| CI/CD | GitHub Actions | Production images |
| Desktop | Electron | End-user application |

## Next Steps

- **Developing?** → [Local Development](./local-development.md)
- **Deploying?** → [CI/CD Pipeline](./ci-cd-pipeline.md)
- **Building desktop app?** → [Electron App](./electron-app.md)
- **Issue with build?** → [Troubleshooting](./troubleshooting.md)
