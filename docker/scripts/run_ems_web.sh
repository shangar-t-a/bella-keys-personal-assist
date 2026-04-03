#!/usr/bin/env bash
# Launches the Expense Manager web app (React UI + EMS backend only).
# Run from repo root: bash docker/scripts/run_ems_web.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
ENV_FILE="$REPO_ROOT/docker/.env"

echo "Starting EMS services (web UI + backend)..."
docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile ems-web up -d --build

echo "Expense Manager web app is running at http://localhost:3000"
