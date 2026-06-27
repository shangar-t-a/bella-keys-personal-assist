# Developer Development Workflow

This document details the local development environment setup, running services, packaging procedures, and links to specialized standard guidelines.

---

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

## 3. Specialized Guideline References

To keep documentation clean, modular, and maintainable, developer standards are decoupled into separate reference guides:

* [Git Guidelines (Source of Truth)](../../.agents/rules/git-guidelines.md): Branch naming, commit formatting (with sign-off), and Pull Request standards.
* [Monorepo Release Guidelines (Source of Truth)](../../.agents/rules/release-guidelines.md): Checklist for syncing versions across monorepo package files and the CHANGELOG.
* [Architecture & Backend Coding Standards](architecture-standards.md): Monorepo technical stack, clean architecture structure, health checks, and Python code styling/docstrings.
* [Backend Testing Guidelines](testing-guidelines.md): Pytest setup, test database execution, test fixtures, and scenario coverage requirements.
* [Frontend Coding & UI Guidelines](frontend-guidelines.md): React/TypeScript API patterns, authentication event loops, and MUI Dialog layout rules.
