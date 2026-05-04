# Docker Build Workflow

This document describes the GitHub Actions workflow for building and pushing Docker images to GitHub Container Registry (GHCR).

## Overview

Each service has its own manual dispatch workflow that can also be auto-triggered by updating the service's VERSION file.

## Workflow Structure

### Files

- `.github/workflows/reusable-docker-build.yml` - Reusable build job called by service workflows
- `.github/workflows/build-expense-manager.yml` - Expense Manager Service workflow
- `.github/workflows/build-bella-chat.yml` - Bella Chat Service workflow
- `.github/workflows/build-ems-mcp.yml` - EMS MCP Server workflow
- `.github/workflows/build-keys-ui.yml` - Keys Personal Assist UI workflow

### Version Files

Each service has a `VERSION` file in its root directory:

- `services/expense-manager-service/VERSION`
- `services/bella-chat-service/VERSION`
- `mcps/ems-mcp-server/VERSION`
- `keys-personal-assist-ui/VERSION`

## Usage

### Manual Build

1. Go to **Actions** tab in GitHub
2. Select the service workflow (e.g., "Build Expense Manager Service")
3. Click **Run workflow**
4. Enter a version tag (e.g., `1.0.0`, `latest`) or leave empty to use the current VERSION file
5. Click **Run workflow**

### Auto-Trigger Build

1. Update the VERSION file locally:

   ```bash
   echo "1.2.3" > services/expense-manager-service/VERSION
   ```

2. Commit and push the change:

   ```bash
   git add services/expense-manager-service/VERSION
   git commit -m "chore(ems): bump version to 1.2.3"
   git push
   ```

3. The workflow auto-triggers and builds/pushes the image with the new version

## Image Registry

Images are pushed to GitHub Container Registry (GHCR) with two tags:

- Version tag: `ghcr.io/<owner>/<service>:<version>` (e.g., `1.0.0`)
- Latest tag: `ghcr.io/<owner>/<service>:latest` (always points to most recent build)

Examples:

- `ghcr.io/<owner>/expense-manager-service:1.0.0`
- `ghcr.io/<owner>/expense-manager-service:latest`
- `ghcr.io/<owner>/bella-chat-service:1.0.0`
- `ghcr.io/<owner>/bella-chat-service:latest`
- `ghcr.io/<owner>/ems-mcp-server:1.0.0`
- `ghcr.io/<owner>/ems-mcp-server:latest`
- `ghcr.io/<owner>/keys-personal-assist-ui:1.0.0`
- `ghcr.io/<owner>/keys-personal-assist-ui:latest`

## Authentication

The workflow uses the automatically provided `GITHUB_TOKEN` for authentication. No additional secrets are required.

## Docker Compose Integration

To use the built images in `docker/docker-compose.yaml`, update the image references:

```yaml
expense-manager-service:
  image: ghcr.io/<owner>/expense-manager-service:1.0.0

bella-chat-service:
  image: ghcr.io/<owner>/bella-chat-service:1.0.0

ems-mcp-server:
  image: ghcr.io/<owner>/ems-mcp-server:1.0.0

keys-personal-assist-ui:
  image: ghcr.io/<owner>/keys-personal-assist-ui:1.0.0
```
