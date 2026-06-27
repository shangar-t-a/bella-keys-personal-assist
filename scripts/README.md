# Scripts Index

Quick reference for all build, run, and utility scripts in the repository.

## Documentation

For detailed guides, see:

- [User Setup Guide](../docs/user/setup-guide.md) - Host prerequisites, setup, and runner instructions.
- [Developer Workflow](../docs/developer/development-workflow.md) - Local development environment details.

## Directory Structure

```text
scripts/
├── database/              # Database configuration SQL & utilities
│   ├── init-db.sql        # PostgreSQL init schema script (dev)
│   ├── init-db-prod.sql   # PostgreSQL init schema script (prod)
│   └── backup-db.ps1      # Database backup utility script
├── electron/              # Build desktop app installer (developers only)
│   ├── build.sh           # Build Electron app (Linux/macOS)
│   ├── build.bat          # Build Electron app (Windows)
│   ├── setup-electron.js
│   └── setup-wincodesign.js
├── screenshots/           # uv project — Playwright portfolio screenshot capture
│   ├── capture_screens.py # Main script (uv run capture_screens.py)
│   ├── pyproject.toml
│   ├── .python-version
│   └── README.md
├── utils/                 # Miscellaneous Python utility scripts
│   ├── generate-jwt-secret.py
│   └── update-env-passwords.py
├── db-migrate.sh          # Run database migrations (Linux/macOS/Windows Git Bash)
├── run-desktop-app.sh     # Run packaged app + pull services from GHCR (Linux/macOS/Windows Git Bash)
├── run-dev.sh             # Unified developer runner (Linux/macOS/Windows Git Bash)
├── run-tests.sh           # Run test suites (Linux/macOS/Windows Git Bash)
├── setup.sh               # Unified environment & dependency setup (Linux/macOS/Windows Git Bash)
└── README.md              # This file (Scripts Index)
```

## Quick Reference

### 1. Environment & Dependency Setup
Sets up environment configurations, syncs Python packages using `uv`, installs UI packages using `npm`, and initializes databases.
```bash
bash scripts/setup.sh
```

### 2. Run Local Development Services
Launches development databases/services in Docker and starts React/Electron components locally. Supports profiles: `ems-web`, `bella-web`, `ems-desktop`, `bella-desktop`.
```bash
bash scripts/run-dev.sh [profile]
```

### 3. Run Packaged Desktop App (Production)
Pulls pre-built containers from the GitHub Container Registry (GHCR) and starts the compiled desktop app.
```bash
bash scripts/run-desktop-app.sh
```

### 4. Running Migrations & Tests
Convenient wrappers for database schema migrations and testing.
```bash
# Apply database migrations
bash scripts/db-migrate.sh

# Run backend pytest suite
bash scripts/run-tests.sh
```

### 5. Capture Portfolio Screenshots
Captures all UI screens in light and dark themes into `docs/screens/v6.0/`.
Requires the UI dev server to be running on `http://localhost:3000`.
```bash
# One-time setup
cd scripts/screenshots
uv sync
uv run playwright install chromium

# Run
uv run capture_screens.py
```
