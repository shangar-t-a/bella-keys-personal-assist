# Developer Development Workflow

This document details the development environment setup, build procedures, architecture rules, and release pipeline.

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
