#!/usr/bin/env bash
# run_capture.sh — End-to-end user journey capture orchestrator.
#
# Starts the full Bella Keys dev stack, seeds demo data directly into the DB,
# runs the Playwright screenshot capture, then optionally stops the stack.
#
# Usage (from repo root):
#   bash scripts/screenshots/run_capture.sh
#
# Options:
#   --keep-up     Skip docker compose down at the end (useful during dev)
#   --skip-seed   Skip demo data seeding (use existing DB data)
#   --skip-down   Alias for --keep-up
#
# Env var overrides (forwarded to capture_screens.py):
#   BASE_URL           default: http://localhost:3000
#   SCREENSHOT_USER    default: demo
#   SCREENSHOT_PASS    default: demo
#   EMS_PG_DATABASE_URL   overrides DB URL for seeder

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCKER_DIR="$REPO_ROOT/docker"

KEEP_UP=false
SKIP_SEED=false

for arg in "$@"; do
    case $arg in
        --keep-up|--skip-down) KEEP_UP=true ;;
        --skip-seed)           SKIP_SEED=true ;;
    esac
done

# Colour helpers
_info()  { echo -e "\033[0;36m[capture]\033[0m $*"; }
_ok()    { echo -e "\033[0;32m[capture]\033[0m ✓ $*"; }
_err()   { echo -e "\033[0;31m[capture]\033[0m ✗ $*" >&2; }
_step()  { echo -e "\n\033[1;35m══ Step $* \033[0m"; }

# Health-check helper: polls an HTTP endpoint until 200 or timeout
wait_healthy() {
    local name="$1" url="$2" max_seconds="${3:-90}"
    local elapsed=0
    _info "Waiting for $name at $url (up to ${max_seconds}s)…"
    while true; do
        if curl -sf --max-time 3 "$url" > /dev/null 2>&1; then
            _ok "$name is healthy"
            return 0
        fi
        if (( elapsed >= max_seconds )); then
            _err "$name did not become healthy within ${max_seconds}s"
            return 1
        fi
        sleep 3
        elapsed=$(( elapsed + 3 ))
        echo -n "."
    done
}

# Step 1: Start Docker services
_step "1/5 — Start Docker services (ai-chat profile)"
cd "$DOCKER_DIR"

docker compose --profile ai-chat up -d

_ok "docker compose up issued"

# Step 2: Wait for services to be healthy
_step "2/5 — Wait for services to be healthy"

wait_healthy "auth-service"  "http://localhost:8002/health" 90
wait_healthy "EMS"           "http://localhost:8000/health" 90
wait_healthy "bella-chat"    "http://localhost:5000/health" 120

# Give the UI (nginx) a moment to stabilise
_info "Waiting 5s for UI to stabilise…"
sleep 5

# Step 3: Seed demo data into PostgreSQL
_step "3/5 — Seed demo data into PostgreSQL"

cd "$SCRIPT_DIR"

if [ "$SKIP_SEED" = true ]; then
    _info "Skipping seed (--skip-seed passed)"
else
    _info "Running seed_portfolio_data.py…"
    uv run seed_portfolio_data.py
    _ok "Portfolio data seeded"
fi

# Step 4: Run Playwright capture
_step "4/5 — Run Playwright capture"

_info "Running capture_screens.py…"
uv run capture_screens.py
_ok "Screenshots captured — see docs/screens/"

# Step 5: Shutdown
_step "5/5 — Shutdown"

if [ "$KEEP_UP" = true ]; then
    _info "Keeping stack up (--keep-up passed). Run 'docker compose --profile ai-chat down' when done."
else
    _info "Stopping Docker services…"
    cd "$DOCKER_DIR"
    docker compose --profile ai-chat down
    _ok "Stack stopped"
fi

echo ""
_ok "User journey capture complete!"
_info "Open docs/screens/user-journey.html to view the portfolio page."
