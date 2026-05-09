# Electron Desktop App

Build and run the Bella Keys Personal Assist desktop application.

## Overview

The Electron app provides a native desktop experience with:

- Integrated web UI
- Optional local service management
- System tray integration
- Auto-updater support

## Prerequisites

- Node.js 18+
- Docker Desktop (for local services)
- Git

## Build

### Linux/macOS

```bash
bash scripts/electron/build.sh
```

### Windows

```cmd
scripts\electron\build.bat
```

## Run Desktop App

### With GitHub Container Registry Images

Services pull from GHCR (production images):

```bash
# Linux/macOS
bash scripts/services/run-services-installed-app.sh

# Windows
scripts\services\run-services-installed-app.bat
```

### With Local Services

Build and run your own service images:

1. **Build services locally:**

   ```bash
   # Update VERSION to trigger builds
   echo "1.0.0-local" > services/expense-manager-service/VERSION
   git add services/expense-manager-service/VERSION
   git commit -m "chore: local build"
   git push
   ```

2. **Update docker/.env:**

   ```bash
   USE_LOCAL_IMAGES=true
   ```

3. **Run with local images:**

   ```bash
   bash scripts/services/run-services-installed-app.sh
   ```

## Service Profiles

### Minimal

- **Services**: Expense Manager only
- **Resources**: ~2GB RAM
- **Ports**: 5432, 8000
- **Fastest startup**

### Standard (Recommended)

- **Services**: Expense Manager + Bella Chat
- **Resources**: ~4GB RAM
- **Ports**: 5432, 6333, 8000, 8001, 5000
- **Full feature set**

### Full

- **Services**: All services + Monitoring
- **Resources**: ~6GB RAM
- **Ports**: 5432, 6333, 6334, 8000, 8001, 5000, 6006, 4317, 9090
- **Development mode**

## Configuration

### Environment Variables

Edit `docker/.env`:

```bash
# Service Selection
SERVICE_PROFILE=standard      # minimal, standard, full

# API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Feature Flags
ENABLE_AI_FEATURES=true
ENABLE_ANALYTICS=false
```

### Custom Service Images

Override default images in `docker/.env`:

```bash
EMS_IMAGE=ghcr.io/your-org/expense-manager-service:custom
BELLA_IMAGE=ghcr.io/your-org/bella-chat-service:custom
```

## Distribution

### Build Artifacts

After building, find outputs in:

```
dist/
├── linux/
│   └── *.AppImage           # Linux portable
├── mac/
│   └── *.dmg                # macOS installer
└── win/
    └── *.exe                # Windows installer
```

### Publishing

Configure in `package.json`:

```json
{
  "build": {
    "publish": {
      "provider": "github",
      "owner": "your-org",
      "repo": "bella-keys-personal-assist"
    }
  }
}
```

## Troubleshooting

### Build Issues

```bash
# Clear dependencies
rm -rf node_modules
npm install

# Verify Node version
node --version  # Should be 18+

# Check dependencies
npm ls
```

### Docker Issues

- Ensure Docker Desktop is running
- Check port availability
- Verify Docker daemon status

### Service Issues

```bash
# Check service logs
docker compose logs

# Verify environment variables
cat docker/.env

# Test health endpoints
curl http://localhost:8000/health
```

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `build.sh` / `build.bat` | Build Electron app for all platforms |
| `run.sh` / `run.bat` | Run with GHCR images |
| `run-desktop-app.sh` | Legacy script (deprecated) |

## Development

### Hot Reload

```bash
# Terminal 1: Run Electron in dev mode
npm run electron:dev

# Terminal 2: Start services
docker compose up -d
```

### Debugging

```bash
# Enable DevTools
npm run electron:dev -- --dev-tools

# Verbose logging
DEBUG=* npm run electron:dev
```

## See Also

- [Local Development](./local-development.md) - Docker Compose setup
- [CI/CD Pipeline](./ci-cd-pipeline.md) - GHCR image publishing
- [Troubleshooting](./troubleshooting.md) - Common issues
