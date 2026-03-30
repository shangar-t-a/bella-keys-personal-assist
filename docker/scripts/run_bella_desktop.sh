#!/usr/bin/env bash
# Launches the Bella Keys desktop app (Electron + backend services).
# Run from repo root: bash docker/scripts/run_bella_desktop.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
UI_DIR="$REPO_ROOT/keys-personal-assist-ui"
ENV_FILE="$REPO_ROOT/docker/.env"

echo "Starting backend services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile bella up -d --build

echo "Launching Electron app..."
cd "$UI_DIR"
npm run dev:electron
