# 🛠️ Developer Development Workflow

This guide details how to build, modify, and extend the Bella Keys ecosystem.

## 1. Repository Overview

* `keys-personal-assist-ui/`: Electron + React (Vite).
* `services/`: Python backends (FastAPI, LangGraph).
* `mcps/`: Model Context Protocol servers.
* `docker/`: Multi-environment orchestration.
* `scripts/`: Build and run automation.

## 2. Building from Source

### Building the Desktop UI

```bash
cd keys-personal-assist-ui
npm install --legacy-peer-deps
npm run build:electron
```

### Building Production Artifacts

Use the consolidated build script to generate the installer and portable binaries:

```powershell
.\scripts\build-electron.bat
```

## 3. Architecture Standards

### The "Inside-Out" Rule

All Dockerized services must remain stateless.

1. **Never** use Docker-managed named volumes for persistent data.
2. **Always** use `host.docker.internal` for external service discovery.
3. **Bind Mounts** are only permitted for containerized engines requiring local persistence (e.g., Qdrant storage).

### Health Check Standard

All containers must support `curl` for health monitoring. Use the following pattern in compose files:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:PORT/health"]
```
