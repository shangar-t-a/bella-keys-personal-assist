# Bella Keys Scripts

This directory contains scripts for building and running the Bella Keys Electron desktop application with optional service selection.

## Available Scripts

### Build Scripts

#### `build-electron.sh` (Linux/macOS)

Build the Electron app with interactive service selection.

```bash
# From repository root
bash scripts/build-electron.sh
```

#### `build-electron.bat` (Windows)

Windows batch script for building the Electron app.

```cmd
# From repository root
scripts\build-electron.bat
```

### Run Scripts

#### `run-desktop-app.sh` (Linux/macOS)

Run the desktop app with services from GitHub Container Registry.

```bash
# From repository root
bash scripts/run-desktop-app.sh
```

#### `run-desktop-app.bat` (Windows)

Windows batch script for running the desktop app.

```cmd
# From repository root
scripts\run-desktop-app.bat
```

## Service Profiles

### Minimal

- **Services**: Expense Manager only
- **Resources**: ~2GB RAM
- **Ports**: 5432, 8000

### Standard (Recommended)

- **Services**: Expense Manager + Bella Chat
- **Resources**: ~4GB RAM
- **Ports**: 5432, 6333, 8000, 8001, 5000

### Full

- **Services**: All services + Monitoring
- **Resources**: ~6GB RAM
- **Ports**: 5432, 6333, 6334, 8000, 8001, 5000, 6006, 4317, 9090

## Quick Start

1. **Build the app**:

   - Linux/macOS: `bash scripts/build-electron.sh`
   - Windows: `scripts\build-electron.bat`

2. **Run the app**:

   - Linux/macOS: `bash scripts/run-desktop-app.sh`
   - Windows: `scripts\run-desktop-app.bat`

## Prerequisites

- Node.js 18+
- Docker Desktop
- Git

## Configuration

Edit `docker/.env` to configure:

- Database settings
- AI model settings
- Port configurations
- API keys

## Troubleshooting

### Docker Issues

- Ensure Docker Desktop is running
- Check port availability
- Verify Docker daemon status

### Build Issues

- Clear node_modules: `rm -rf node_modules && npm install`
- Check Node.js version: `node --version`
- Verify dependencies: `npm ls`

### Service Issues

- Check service logs: `docker compose logs`
- Verify environment variables
- Test service health endpoints
