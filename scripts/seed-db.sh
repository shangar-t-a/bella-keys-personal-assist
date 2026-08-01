#!/usr/bin/env bash
# Runs database seeder to populate sample portfolio data into PostgreSQL.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SCREENSHOTS_DIR="$REPO_ROOT/scripts/screenshots"

echo "Seeding database with sample demo data..."
cd "$SCREENSHOTS_DIR"
uv run seed_demo_data.py
