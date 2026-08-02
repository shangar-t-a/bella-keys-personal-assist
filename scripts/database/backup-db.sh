#!/usr/bin/env bash
# PostgreSQL database backup utility script

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
ENV_FILE="$REPO_ROOT/docker/.env"
BACKUP_DIR="$REPO_ROOT/backups"

PG_HOST="localhost"
PG_PORT="5432"
PG_USER="postgres"
PG_DB_NAME="expense_manager"
PG_PASS=""

# Load configuration from docker/.env if available
if [ -f "$ENV_FILE" ]; then
    echo "Reading database configuration from $ENV_FILE..."
    if grep -q "^EMS_PG_DB_USER=" "$ENV_FILE"; then
        PG_USER=$(grep "^EMS_PG_DB_USER=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
    if grep -q "^EMS_PG_DB_NAME=" "$ENV_FILE"; then
        PG_DB_NAME=$(grep "^EMS_PG_DB_NAME=" "$ENV_FILE" | cut -d'=' -f2- | tr -d '"' | tr -d "'")
    fi
fi

echo "============================================="
echo "  PostgreSQL Database Backup Utility"
echo "============================================="
echo "Host:     $PG_HOST"
echo "Port:     $PG_PORT"
echo "Database: $PG_DB_NAME"
echo "User:     $PG_USER"
echo "============================================="

read -p "Proceed with backup? [Y/n] (default: Y): " CONFIRM
CONFIRM="${CONFIRM:-Y}"
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Backup cancelled."
    exit 0
fi

read -s -p "Enter PostgreSQL password for user '$PG_USER' (or press Enter if blank): " PG_PASS
echo

if [ -n "$PG_PASS" ]; then
    export PGPASSWORD="$PG_PASS"
fi

mkdir -p "$BACKUP_DIR"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_${PG_DB_NAME}_${TIMESTAMP}.sql"

echo "Backing up database '$PG_DB_NAME' to $BACKUP_FILE..."

if pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -F c -b -v -f "$BACKUP_FILE" "$PG_DB_NAME" 2>/dev/null; then
    echo "✅ Backup completed successfully!"
    echo "Backup File: $BACKUP_FILE"
else
    echo "Attempting plain text format backup..."
    if pg_dump -h "$PG_HOST" -p "$PG_PORT" -U "$PG_USER" -f "$BACKUP_FILE" "$PG_DB_NAME"; then
        echo "✅ Backup completed successfully (SQL text format)!"
        echo "Backup File: $BACKUP_FILE"
    else
        echo "❌ pg_dump failed. Please check if pg_dump is installed and accessible in PATH."
        exit 1
    fi
fi

if [ -n "${PGPASSWORD:-}" ]; then
    unset PGPASSWORD
fi
