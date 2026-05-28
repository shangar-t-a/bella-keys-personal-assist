# Bella Keys: Personal Intelligence and Expense Management

Bella Keys is a desktop application that combines professional-grade expense management with a private AI personal assistant.

The project uses a hybrid "inside-out" architecture: application logic is containerized via Docker while user data (PostgreSQL database and Ollama models) remains on the host machine to ensure privacy and data sovereignty.

## Documentation

* [User Setup Guide](docs/user/setup-guide.md): Installing dependencies, initializing databases, and running the application.
* [Developer Workflow](docs/developer/development-workflow.md): Project structure, local development environment, and build commands.
* [Git Workflow](docs/developer/git-workflow.md): Rules for branch naming, commits, and pull requests.

## Project Structure

* [keys-personal-assist-ui](keys-personal-assist-ui/README.md): React/Electron desktop interface.
* [services/expense-manager-service](services/expense-manager-service/README.md): Clean architecture FastAPI backend for financial tracking.
* [services/bella-chat-service](services/bella-chat-service/README.md): LangGraph AI assistant orchestration service.
* [services/etl-pipelines](services/etl-pipelines/README.md): Knowledge ingestion pipelines.
* [mcps/ems-mcp-server](mcps/ems-mcp-server/README.md): Model Context Protocol server exposing financial data.

## Quick Start (Development)

1. **Setup Environment and Dependencies:**
   Run `bash scripts/setup.sh` (works on Linux, macOS, and Windows Git Bash)
2. **Run Development Services:**
   Run `bash scripts/run-dev.sh [profile]` (works on Linux, macOS, and Windows Git Bash)

## Production Deployment (End-User / Home PC)

To install Bella Keys on a new PC without downloading the full repository, open a terminal (Git Bash, WSL, or macOS Terminal) and run:

```bash
curl -sSL "https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/scripts/deploy/install-prod.sh" | bash
```

**What this does:**
- Downloads the necessary configuration files.
- Prompts you to configure your `.env` secrets interactively or offline.
- Pulls and starts the latest Docker containers.

**Note:** You must have Docker, PostgreSQL, and Ollama installed natively on your host PC before running this script.

**Managing Services:**
Once installed, use the downloaded `run-prod.ps1` script (on Windows) to easily start, stop, or restart the background services.
