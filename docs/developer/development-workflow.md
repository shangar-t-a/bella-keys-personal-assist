# Developer Development Workflow

This document details the development environment setup, build procedures, architecture rules, and release pipeline.

## 1. Running Services Locally

For active development, services can be run directly on the host machine.

### Expense Manager Service (FastAPI)
```bash
cd services/expense-manager-service
uv sync
uv run app/main.py
```

### Desktop UI (React/Vite Dev Mode)
```bash
cd keys-personal-assist-ui
npm install --legacy-peer-deps
npm run dev
```
The interface is available at `http://localhost:3000`. API requests to `/api/ems` and `/api/bella-chat` are proxied to the local backends.

---

## 2. Packaging and Electron Builds

To build production installer binaries:

* **Windows:**
  ```powershell
  .\scripts\build-electron.bat
  ```
* **Linux/macOS:**
  ```bash
  bash scripts/electron/build.sh
  ```

Output binaries are stored in the `dist/` directory.

---

## 3. Architecture Standards

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

---

## 4. Continuous Integration and Release Pipeline

The project utilizes GitHub Actions for building and publishing Docker images to the GitHub Container Registry (GHCR).

### Build Triggers
To prevent registry clutter and control costs:
* Builds do not trigger on standard source code commits.
* Builds only trigger on `push` to `main` when a service `VERSION` file is modified (e.g., `services/expense-manager-service/VERSION`).

### Security Scanning
The build pipeline scans all generated images for high and critical vulnerabilities using Trivy before publishing.
