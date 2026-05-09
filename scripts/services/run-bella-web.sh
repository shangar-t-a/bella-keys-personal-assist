#!/usr/bin/env bash
# Launches the Bella Keys web app (React UI + backend services via Docker).
# Run from repo root: bash docker/scripts/run_bella_web.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
ENV_FILE="$REPO_ROOT/docker/.env"

echo "Starting all services (web UI + backends)..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile bella --profile web up -d --build

echo "Bella Keys web app is running at http://localhost:3000"
