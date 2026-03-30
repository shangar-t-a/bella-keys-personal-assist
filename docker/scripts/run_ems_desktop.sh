#!/usr/bin/env bash
# Launches the Expense Manager desktop app (Electron + EMS backend only).
# Run from repo root: bash docker/scripts/run_ems_electron.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
UI_DIR="$REPO_ROOT/keys-personal-assist-ui"
ENV_FILE="$REPO_ROOT/docker/.env"

echo "Starting EMS backend services..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build

echo "Launching Electron app..."
cd "$UI_DIR"
npm run dev:electron
