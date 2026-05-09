# Scripts Index

Quick reference for all build and run scripts.

## Documentation

For detailed documentation, see:

- [Build & Run Guide](../docs/build/README.md) - Overview and quick start
- [Scripts Reference](../docs/build/scripts-reference.md) - Complete script catalog
- [Electron App](../docs/build/electron-app.md) - Desktop app build/run
- [Local Development](../docs/build/local-development.md) - Docker development
- [Troubleshooting](../docs/build/troubleshooting.md) - Common issues

## Directory Structure

```
scripts/
├── database/          # Database initialization
│   └── init-db.sql    # PostgreSQL init script
├── electron/          # Build desktop app (developers only)
│   ├── build.sh       # Build Electron app (Linux/macOS)
│   └── build.bat      # Build Electron app (Windows)
├── services/          # Run backend services
│   ├── run-services-installed-app.sh     # Run services for installed app
│   ├── run-services-installed-app.bat    # Windows version
│   ├── run-ems-web.sh     # EMS + Web UI (development)
│   ├── run-bella-web.sh   # Bella Chat + Web UI (development)
│   └── run-*.sh           # Other service combinations
└── README.md          # This file
```

## Quick Start

### Build Desktop App

```bash
# Linux/macOS
bash scripts/electron/build.sh

# Windows
scripts\electron\build.bat
```

### Run Services (For Installed App)

If you installed the desktop app, start backend services:

```bash
# Linux/macOS
bash scripts/services/run-services-installed-app.sh

# Windows
scripts\services\run-services-installed-app.bat
```

### Run Services (Development)

For development with specific service combinations:

```bash
# EMS + Web UI
bash scripts/services/run-ems-web.sh

# Bella Chat + Web UI
bash scripts/services/run-bella-web.sh

# See scripts/services/ for all options
```

## Prerequisites

- Node.js 18+ (for Electron builds)
- Docker Desktop (for running services)
- Git
