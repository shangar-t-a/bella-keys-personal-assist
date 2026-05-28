#!/usr/bin/env bash
# Runs database migrations for the expense manager service.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="$REPO_ROOT/services/expense-manager-service"

if [ -z "${DATABASE_URL:-}" ]; then
    if [ -f "$REPO_ROOT/docker/.env" ]; then
        # Parse EMS_PG_DATABASE_URL line
        DB_URL=$(grep "^EMS_PG_DATABASE_URL=" "$REPO_ROOT/docker/.env" | cut -d'=' -f2-)
        if [ -n "$DB_URL" ]; then
            # Replace host.docker.internal with localhost
            export DATABASE_URL="${DB_URL/host.docker.internal/localhost}"
            echo "Loaded DATABASE_URL from docker/.env (with host adapted to localhost)."
        fi
    fi
fi

if [ -z "${DATABASE_URL:-}" ]; then
    echo "WARNING: DATABASE_URL is not set in environment or docker/.env."
    echo "Migrations might fail."
fi

echo "Running database migrations..."
cd "$SERVICE_DIR"
uv run alembic -c app/infrastructures/postgres_db/alembic.ini upgrade head
