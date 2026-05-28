#!/usr/bin/env bash
# Unified developer runner for launching different service configurations.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/docker/docker-compose.yaml"
ENV_FILE="$REPO_ROOT/docker/.env"
UI_DIR="$REPO_ROOT/keys-personal-assist-ui"

# Validate docker/.env file
if [ ! -f "$ENV_FILE" ]; then
    echo "ERROR: Environment file $ENV_FILE not found."
    echo "Please run bash scripts/setup.sh first to configure your environment."
    exit 1
fi

CHOICE="${1:-}"

# Interactive Menu
show_menu() {
    echo "===================================="
    echo "*      Bella Keys Dev Launcher     *"
    echo "===================================="
    echo
    echo "Select a development configuration:"
    echo "1) EMS + Web UI"
    echo "2) Bella Chat + Web UI"
    echo "3) EMS + Desktop (Electron)"
    echo "4) Bella Chat + Desktop (Electron)"
    echo
    read -p "Enter your choice (1-4): " menu_choice
    case "$menu_choice" in
        1) CHOICE="ems-web" ;;
        2) CHOICE="bella-web" ;;
        3) CHOICE="ems-desktop" ;;
        4) CHOICE="bella-desktop" ;;
        *) echo "Invalid choice." ; show_menu ;;
    esac
}

if [ -z "$CHOICE" ]; then
    show_menu
fi

cleanup() {
    if [[ "$CHOICE" == "ems-desktop" || "$CHOICE" == "bella-desktop" ]]; then
        echo
        echo "Stopping backend services..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    fi
}

trap cleanup EXIT INT TERM

case "$CHOICE" in
    "ems-web")
        echo "Starting EMS services (Web UI + backend)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile ems-web up -d --build
        ;;
    "bella-web")
        echo "Starting all services (Web UI + backends)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile bella --profile web up -d --build
        ;;
    "ems-desktop")
        echo "Starting EMS backend services..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d --build
        echo "Launching Electron app in development..."
        cd "$UI_DIR"
        node "$REPO_ROOT/scripts/electron/setup-electron.js"
        npm run dev:electron
        ;;
    "bella-desktop")
        echo "Starting backend services (EMS + Bella)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" --profile bella up -d --build
        echo "Launching Electron app in development..."
        cd "$UI_DIR"
        node "$REPO_ROOT/scripts/electron/setup-electron.js"
        npm run dev:electron
        ;;
    *)
        echo "Invalid configuration choice: $CHOICE"
        echo "Valid choices: ems-web, bella-web, ems-desktop, bella-desktop"
        exit 1
        ;;
esac
