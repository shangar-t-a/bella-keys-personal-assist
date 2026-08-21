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

## Production Deployment & Service Management (`bella-deploy`)

Production deployment and container lifecycles on Windows, macOS, and Linux are managed using the cross-platform CLI tool **`bella-deploy`** ([tools/deploy-manager](tools/deploy-manager/README.md)).

### 1. Install Globally via `uv tool`

```bash
uv tool install "git+https://github.com/shangar-t-a/bella-keys-personal-assist#subdirectory=tools/deploy-manager"
```

### 2. Run in Any Deployment Directory

```bash
# Launch interactive Production Manager TUI
bella-deploy

# Or run direct subcommands
bella-deploy start --profile ems
bella-deploy status
bella-deploy logs -f
bella-deploy update
```

> [!NOTE]
> **Legacy Windows Batch Runner:** The legacy Windows batch runner `scripts/deploy/bella-keys-manager.bat` remains available as a deprecated fallback.
