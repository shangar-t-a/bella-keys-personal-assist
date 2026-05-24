# Setup Guide

This guide covers the prerequisites, database initialization, and startup procedures for running Bella Keys.

## Prerequisites

Ensure the following dependencies are installed and running on your host machine:

* **Docker Desktop:** Required for running containerized application services.
* **PostgreSQL:** Required on the host machine to store financial and AI checkpoint data.
* **Ollama (Optional):** Required on the host machine if using local-first AI models.

## 1. Database Initialization

The application follows an "inside-out" architecture, meaning databases run on your host PC rather than inside Docker containers.

1. Locate the initialization script at `scripts/database/init-db.sql`.
2. Execute this script against your host PostgreSQL instance (e.g., using `psql` or an administration GUI like pgAdmin or DBeaver).
3. The script creates the following databases:
   * `expense_manager`
   * `expense_manager_test` (for unit/integration testing)
   * `bella_chat_arize_data`
   * `bella_chat_checkpoints`

## 2. Environment Configuration

1. Copy the sample environment file:
   ```bash
   cp docker/.env.example docker/.env
   ```
2. Open `docker/.env` and configure your database passwords and API keys (e.g., Google or OpenAI keys, if applicable).

## 3. Running the Application

Launch both the backend services and the desktop application using the unified runner script:

```powershell
.\scripts\run-desktop-app.bat
```

During startup, select a service profile:

| Profile | Services Running | RAM Required | Description |
| :--- | :--- | :--- | :--- |
| **Minimal** | Expense Manager | ~2GB | Basic financial tracking only |
| **Standard** | EMS + Bella Chat | ~4GB | Full AI assistant and finance tracking |

## Troubleshooting

### Database Connection Failures
* Ensure PostgreSQL is running on the host machine.
* Verify that your firewall allows traffic on port `5432`.
* Check that `EMS_PG_DB_HOST` in `docker/.env` is set to `host.docker.internal`.

### Port Conflicts
If a port is already allocated, modify the target port in `docker/.env` (e.g., change `EMS_PORT` or `PERSONAL_ASSIST_UI_PORT`).
