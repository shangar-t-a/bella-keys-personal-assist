# Bella Deploy Manager (`bella-deploy`)

A lightweight, zero-dependency, cross-platform CLI tool for managing production deployments, Docker container lifecycles, and environment synchronization for Bella Keys.

---

## Installation via `uv tool`

Install globally on Windows, macOS, or Linux:

```bash
uv tool install "git+https://github.com/shangar-t-a/bella-keys-personal-assist#subdirectory=tools/deploy-manager"
```

### Upgrading the Tool

```bash
uv tool upgrade bella-deploy-manager
```

---

## Usage

### 1. Interactive Production Manager Menu

Run `bella-deploy` in any directory where you want to manage your production deployment:

```bash
bella-deploy
```

If the directory does not yet contain configuration files, `bella-deploy` will automatically prompt and download `docker-compose.prod.yaml`, `.env.example`, and `init-db-prod.sql` from GitHub.

### 2. Direct CLI Subcommands

```bash
# Start services
bella-deploy start --profile ems
bella-deploy start --profile ai-chat --with-ui

# Inspect active container status
bella-deploy status

# View live service logs
bella-deploy logs -f

# View recent service logs (last 100 lines)
bella-deploy logs --tail 100

# Restart services
bella-deploy restart

# Stop services
bella-deploy stop

# Update deployment (fetch remote configs, reconcile .env, pull new images, and restart)
bella-deploy update
```

---

## One-Shot Execution (`uvx`)

Run the manager without installing:

```bash
uvx --from "git+https://github.com/shangar-t-a/bella-keys-personal-assist#subdirectory=tools/deploy-manager" bella-deploy
```
