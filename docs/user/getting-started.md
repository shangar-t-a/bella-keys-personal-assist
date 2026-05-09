# Getting Started

Get up and running with Bella Keys Personal Assist.

## Choose Your Path

### Option 1: I Downloaded the Installer (Recommended)

For most users - download pre-built app and run services locally.

**What you need:**

- Docker Desktop installed
- The installer file you downloaded

**Steps:**

1. **Install the app**
   - Run the downloaded installer
   - Follow installation prompts

2. **Start backend services**

   ```bash
   # From the folder where you extracted/cloned the app
   bash scripts/services/run-services-installed-app.sh
   ```

   This starts the backend services that the installed app connects to.

3. **Open the app**
   - Launch Bella Keys from your applications menu
   - The app will connect to services running at <http://localhost>

4. **When done**

   ```bash
   # Stop services
   docker compose -f docker/docker-compose.yaml down
   ```

### Option 2: I'm a Developer

For developers who want to modify the code.

**What you need:**

- Node.js 18+
- Docker Desktop
- Git

**Steps:**

1. **Clone repository**

   ```bash
   git clone <repo-url>
   cd bella-keys-personal-assist
   ```

2. **Configure environment**

   ```bash
   cp docker/.env.example docker/.env
   # Edit docker/.env with your API keys
   ```

3. **Start development**

   ```bash
   # Terminal 1: Run backend services
   docker compose -f docker/docker-compose.yaml up -d

   # Terminal 2: Run desktop app in dev mode
   npm install
   npm run electron:dev
   ```

See [Local Development Guide](../build/local-development.md) for details.

### Option 3: I Want to Build from Source

For advanced users who want to build the installer themselves.

```bash
# Clone and build
git clone <repo-url>
cd bella-keys-personal-assist
bash scripts/electron/build.sh

# Install the built app from dist/ folder
# Then run services
bash scripts/services/run-services-installed-app.sh
```

## Quick Reference

| Task | Command |
|------|---------|
| Start services for installed app | `bash scripts/services/run-services-installed-app.sh` |
| Stop all services | `docker compose -f docker/docker-compose.yaml down` |
| View service logs | `docker compose -f docker/docker-compose.yaml logs -f` |
| Build installer from source | `bash scripts/electron/build.sh` |

## Troubleshooting

### "Cannot connect to services"

Make sure Docker Desktop is running and you've started services:

```bash
bash scripts/services/run-services-installed-app.sh
```

### "Port already in use"

Change ports in `docker/.env`:

```bash
EMS_PORT=8001
KEYS_UI_PORT=5001
```

### "App says 'Service unavailable'"

Check services are healthy:

```bash
docker compose ps
# Should show services as "healthy"
```

## Next Steps

- [Install Guide](./install-guide.md) - Detailed installation steps
- [Run Services](./run-services.md) - All service configuration options
- [Build from Source](./build-from-source.md) - Complete build instructions
- [Troubleshooting](./troubleshooting.md) - Common issues
