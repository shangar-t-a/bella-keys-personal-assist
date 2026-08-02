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

# Step 1: Service Selection
show_menu() {
    echo "===================================="
    echo "*      Bella Keys Dev Launcher     *"
    echo "===================================="
    echo
    echo "Select a development configuration:"
    echo
    echo "  1. EMS only          - Auth + Expense Manager  [default]"
    echo "  2. AI Chat           - Auth + EMS + Bella Chat + Qdrant"
    echo "  3. AI Chat + Monitor - Everything above + Phoenix observability"
    echo
    read -p "Select services [1-3] (default: 1): " service_choice
    service_choice="${service_choice:-1}"

    AI_CHAT_ENABLED=false
    case "$service_choice" in
        1) PROFILES=()             ; SERVICE_LABEL="EMS only" ;;
        2) PROFILES=("ai-chat")    ; AI_CHAT_ENABLED=true ; SERVICE_LABEL="AI Chat" ;;
        3) PROFILES=("ai-chat" "monitor") ; AI_CHAT_ENABLED=true ; SERVICE_LABEL="AI Chat + Monitor" ;;
        *) echo "Invalid choice: $service_choice" ; show_menu ; return ;;
    esac

    # Step 2: Launch mode
    echo
    echo "How do you want to run the UI?"
    echo
    echo "  1. Web UI (Docker/nginx)"
    echo "  2. Desktop (Electron)"
    echo "  3. No UI (backend only)"
    echo
    read -p "Select launch mode [1-3] (default: 2): " ui_choice
    ui_choice="${ui_choice:-2}"

    case "$ui_choice" in
        1)
            if [ "$AI_CHAT_ENABLED" = true ]; then
                echo
                echo "  Which services should the Web UI expose?"
                echo "  1. EMS only"
                echo "  2. EMS + AI Chat"
                echo
                read -p "Select UI scope [1-2] (default: 1): " ui_scope
                ui_scope="${ui_scope:-1}"
                if [ "$ui_scope" = "1" ]; then
                    PROFILES+=("ui-ems")
                    CHOICE="web-ui-ems"
                else
                    PROFILES+=("ui")
                    CHOICE="web-ui"
                fi
            else
                PROFILES+=("ui-ems")
                CHOICE="web-ui-ems"
            fi
            ;;
        2) CHOICE="desktop" ;;
        3) CHOICE="backend-only" ;;
        *) echo "Invalid choice: $ui_choice" ; show_menu ; return ;;
    esac
}

if [ -z "$CHOICE" ]; then
    PROFILES=()
    AI_CHAT_ENABLED=false
    SERVICE_LABEL=""
    show_menu
fi

# Build --profile flags from array
build_profile_args() {
    local args=()
    for p in "${PROFILES[@]:-}"; do
        if [ -n "$p" ]; then
            args+=("--profile" "$p")
        fi
    done
    echo "${args[@]:-}"
}

cleanup() {
    if [[ "$CHOICE" == "desktop" ]]; then
        echo
        echo "Stopping backend services..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    fi
}

trap cleanup EXIT INT TERM

PROFILE_ARGS=$(build_profile_args)

case "$CHOICE" in
    "web-ui"|"web-ui-ems")
        echo "Starting services ($SERVICE_LABEL + Web UI)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" $PROFILE_ARGS up -d --build
        ;;
    "desktop")
        echo "Starting backend services ($SERVICE_LABEL)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" $PROFILE_ARGS up -d --build
        echo "Launching Electron app in development..."
        cd "$UI_DIR"
        node "$REPO_ROOT/scripts/electron/setup-electron.js"
        npm run dev:electron

        echo ""
        echo "========================================================"
        echo " Electron app is running in development mode."
        echo " Press [Enter] to shut down backend services and exit."
        echo "========================================================"
        read -r
        ;;
    "backend-only")
        echo "Starting backend services ($SERVICE_LABEL)..."
        docker compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" $PROFILE_ARGS up -d --build
        ;;
    *)
        echo "Invalid configuration choice: $CHOICE"
        exit 1
        ;;
esac
