#!/usr/bin/env bash
# Runs backend unit and integration tests.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$REPO_ROOT/services/expense-manager-service"

echo "Running backend unit and integration tests..."
cd "$SERVICE_DIR"
uv run --group test pytest "$@"
