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

## Quick Start

1. **Setup Environment and Dependencies:**
   Run `bash scripts/setup.sh` (works on Linux, macOS, and Windows Git Bash)
2. **Run Development Services:**
   Run `bash scripts/run-dev.sh [profile]` (works on Linux, macOS, and Windows Git Bash)

