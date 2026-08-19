# Bella Keys: Personal Intelligence and Expense Management

Bella Keys is a desktop application that combines professional-grade expense management with a private AI personal assistant.

The project uses a hybrid "inside-out" architecture: application logic is containerized via Docker while user data (PostgreSQL database and Ollama models) remains on the host machine to ensure privacy and data sovereignty.

## User Journey & Portfolio Showcase

Explore every screen of the application in light and dark themes, including SSO authentication, budget tracking, wealth management, and AI chat:

* **[Live User Journey Showcase](https://shangar-t-a.github.io/bella-keys-personal-assist/)** (Hosted on GitHub Pages)
* **[Local Showcase File](docs/screens/user-journey.html)**

## Documentation

* [User Setup Guide](docs/user/setup-guide.md): Installing dependencies, initializing databases, and running the application.
* [Developer Workflow](docs/developer/development-workflow.md): Project structure, local development environment, and build commands.
* [Git Guidelines](.agents/rules/git-guidelines.md): Rules for branch naming, commits, and pull requests.

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

> [!NOTE]
> Production service execution and management is currently supported for **Windows only**.

To run or update Bella Keys on a target Windows PC:

1. Place your configuration files (`docker-compose.prod.yaml`, `.env`, and `init-db-prod.sql`) in `%USERPROFILE%\.keys_sandbox\bella-keys\`.
2. Download or copy `scripts/deploy/bella-keys-manager.bat` into that directory.
3. Double-click or run `bella-keys-manager.bat` from Command Prompt / PowerShell.

### Service Operations & Updates

The single `bella-keys-manager.bat` batch script handles the entire lifecycle:

* **Service Management:** Start, stop, restart, view logs, and inspect service status.
* **Updates:** Automatically self-updates the manager script, downloads latest compose configurations, auto-syncs missing environment variables in `.env`, pulls updated Docker images, and recreates containers seamlessly.
