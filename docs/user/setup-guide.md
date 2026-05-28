# Setup Guide

This guide covers the prerequisites, database initialization, and startup procedures for running Bella Keys.

## Prerequisites

Ensure the following dependencies are installed and running on your host machine:

* **Docker Desktop:** Required for running containerized application services.
* **PostgreSQL:** Required on the host machine to store financial and AI checkpoint data.
* **Ollama (Optional):** Required on the host machine if using local-first AI models.

## 1. Local Development Setup

The application uses an "inside-out" architecture, meaning the application logic runs in Docker containers while data (PostgreSQL database and Ollama models) resides on your host machine.

Run the setup automation script to copy environment files, sync dependencies, and initialize the databases automatically (works on Linux, macOS, and Windows Git Bash):

```bash
bash scripts/setup.sh
```

During the setup process, choose `y` when prompted to initialize the PostgreSQL databases. This runs the SQL schema `scripts/database/init-db.sql` automatically.

If you prefer manual setup:
1. Copy `docker/.env.example` to `docker/.env` and edit it to configure passwords and keys.
2. Execute `scripts/database/init-db.sql` on your host PostgreSQL instance.

## 2. Production Deployment (Home PC)

For installing Bella Keys on a target end-user machine without cloning the repository, use the production installer script:

```bash
curl -sSL "https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/scripts/deploy/install-prod.sh" | bash
```

The script will guide you through setting up your environment variables and initializing your databases securely. Once complete, you can manage the services using the provided `run-prod.ps1` script (on Windows) located in your installation directory.

## 3. Running the Application (Development)

Launch both the backend services and the desktop application using the unified runner script (works on Linux, macOS, and Windows Git Bash):

```bash
bash scripts/run-desktop-app.sh
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
