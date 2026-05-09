# Scripts Reference

Complete catalog of build and run scripts.

## Quick Reference

| Task | Script | Platform |
|------|--------|----------|
| Build desktop app | `scripts/electron/build.sh` | Linux/macOS |
| Build desktop app | `scripts/electron/build.bat` | Windows |
| Run services (installed app) | `scripts/services/run-services-installed-app.sh` | Linux/macOS |
| Run services (installed app) | `scripts/services/run-services-installed-app.bat` | Windows |
| Run EMS + Web | `scripts/services/run-ems-web.sh` | Linux/macOS |
| Run Bella + Web | `scripts/services/run-bella-web.sh` | Linux/macOS |

## Electron Scripts

Location: `scripts/electron/`

### Build

Build the Electron desktop application.

**Linux/macOS:**

```bash
bash scripts/electron/build.sh
```

**Windows:**

```cmd
scripts\electron\build.bat
```

**What it does:**

1. Installs Node dependencies
2. Builds React app
3. Packages Electron app
4. Creates installers for current platform

**Outputs:**

- `dist/linux/*.AppImage`
- `dist/mac/*.dmg`
- `dist/win/*.exe`

### Run

Run the Electron app with services from GHCR.

**Linux/macOS:**

```bash
bash scripts/services/run-services-installed-app.sh [profile]
```

**Windows:**

```cmd
scripts\services\run-services-installed-app.bat [profile]
```

**Profiles:**

- `minimal` - Expense Manager only
- `standard` (default) - EMS + Bella Chat
- `full` - All services + monitoring

**Examples:**

```bash
bash scripts/services/run-services-installed-app.sh          # Standard profile
bash scripts/services/run-services-installed-app.sh minimal  # Minimal profile
```

## Docker Scripts

Location: `scripts/services/`

These are convenience wrappers for common Docker Compose operations.

### Service-Specific Runners

| Script | Services Started |
|--------|------------------|
| `run-ems-web.sh` | Expense Manager + Web UI |
| `run-ems-desktop.sh` | EMS with desktop config |
| `run-bella-web.sh` | Bella Chat + Web UI |
| `run-bella-desktop.sh` | Bella with desktop config |

**Usage:**

```bash
bash scripts/services/run-ems-web.sh
```

### Direct Docker Compose

For full control, use Docker Compose directly:

```bash
# Start all services
docker compose -f docker/docker-compose.yaml up -d

# Start specific services
docker compose -f docker/docker-compose.yaml up -d expense-manager-service

# View logs
docker compose -f docker/docker-compose.yaml logs -f

# Stop everything
docker compose -f docker/docker-compose.yaml down
```

## Legacy Scripts

The following scripts exist for backward compatibility:

| Script | Status | Replacement |
|--------|--------|-------------|
| `build-electron.sh` | Deprecated | `scripts/electron/build.sh` |
| `run-desktop-app.sh` | Deprecated | `scripts/services/run-services-installed-app.sh` |
| `docker/scripts/*.sh` | Deprecated | `scripts/services/*.sh` |

## Script Details

### Common Parameters

All run scripts accept these environment variables:

```bash
# Override default compose file
COMPOSE_FILE=docker/docker-compose.prod.yaml

# Service profile selection
SERVICE_PROFILE=minimal

# Enable verbose output
DEBUG=1
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Docker not running |
| 3 | Missing environment file |
| 4 | Port conflict |

## Creating New Scripts

Template for new Docker helper scripts:

```bash
#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting [Service Name]...${NC}"

# Check prerequisites
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Docker is not running${NC}"
    exit 2
fi

# Run services
docker compose -f docker/docker-compose.yaml up -d [services]

echo -e "${GREEN}[Service Name] is running at http://localhost:[port]${NC}"
```

## See Also

- [Local Development](./local-development.md) - Docker setup details
- [Electron App](./electron-app.md) - Desktop app documentation
- [Troubleshooting](./troubleshooting.md) - Common script issues
