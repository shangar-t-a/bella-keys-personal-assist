#!/usr/bin/env bash
# Production runner and service manager script for Bella Keys

set -euo pipefail

if [ ! -f "docker-compose.prod.yaml" ]; then
    echo "Error: docker-compose.prod.yaml not found in the current directory."
    echo "Please run this script from your Bella Keys installation directory."
    exit 1
fi

# Step 1: Service Selection
echo ""
echo "============================================="
echo "  Step 1: Select Services"
echo "============================================="
echo ""
echo "  1. EMS only          - Auth + Expense Manager"
echo "  2. AI Chat           - Auth + EMS + Bella Chat + Qdrant  [recommended]"
echo "  3. AI Chat + Monitor - Everything above + Phoenix observability"
echo ""

read -p "Select services [1-3] (default: 2): " SERVICE_CHOICE
SERVICE_CHOICE="${SERVICE_CHOICE:-2}"

PROFILES=()
AI_CHAT_ENABLED=false
SERVICE_LABEL=""

case "$SERVICE_CHOICE" in
    1)
        SERVICE_LABEL="EMS only (auth-service, ems)"
        ;;
    2)
        PROFILES+=("--profile" "ai-chat")
        AI_CHAT_ENABLED=true
        SERVICE_LABEL="AI Chat (auth-service, ems, bella-chat, ems-mcp, qdrant)"
        ;;
    3)
        PROFILES+=("--profile" "ai-chat" "--profile" "monitor")
        AI_CHAT_ENABLED=true
        SERVICE_LABEL="AI Chat + Monitor (auth-service, ems, bella-chat, ems-mcp, qdrant, phoenix)"
        ;;
    *)
        echo "Invalid selection. Defaulting to AI Chat."
        PROFILES+=("--profile" "ai-chat")
        AI_CHAT_ENABLED=true
        SERVICE_LABEL="AI Chat (auth-service, ems, bella-chat, ems-mcp, qdrant)"
        ;;
esac

# Step 2: Web UI (optional)
echo ""
echo "============================================="
echo "  Step 2: Web UI (optional)"
echo "============================================="
echo ""

read -p "Enable the Web UI? [y/N] (default: N): " UI_CHOICE
UI_CHOICE="${UI_CHOICE:-N}"

if [[ "$UI_CHOICE" =~ ^[Yy]$ ]]; then
    if [ "$AI_CHAT_ENABLED" = true ]; then
        echo ""
        echo "  Which services should the Web UI expose?"
        echo "  1. EMS only"
        echo "  2. EMS + AI Chat"
        echo ""
        read -p "Select UI scope [1-2] (default: 2): " UI_SCOPE
        UI_SCOPE="${UI_SCOPE:-2}"

        if [ "$UI_SCOPE" = "1" ]; then
            PROFILES+=("--profile" "ui-ems")
            SERVICE_LABEL="$SERVICE_LABEL + Web UI (EMS only)"
        else
            PROFILES+=("--profile" "ui")
            SERVICE_LABEL="$SERVICE_LABEL + Web UI (EMS + AI Chat)"
        fi
    else
        PROFILES+=("--profile" "ui-ems")
        SERVICE_LABEL="$SERVICE_LABEL + Web UI (EMS only)"
    fi
fi

echo ""
echo "Active configuration: $SERVICE_LABEL"
echo ""

# Service Manager Loop
while true; do
    echo "============================================="
    echo "  Bella Keys - Service Manager"
    echo "  $SERVICE_LABEL"
    echo "============================================="
    echo ""
    echo "1. Start Services"
    echo "2. Stop Services"
    echo "3. View Service Logs"
    echo "4. Restart Services"
    echo "5. Exit"
    echo ""

    read -p "Select an option [1-5] (default: 1): " CHOICE
    CHOICE="${CHOICE:-1}"

    case "$CHOICE" in
        1)
            echo "Starting services..."
            docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" up -d
            ;;
        2)
            echo "Stopping services..."
            docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" stop
            ;;
        3)
            docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" logs -f
            ;;
        4)
            echo "Restarting services..."
            docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" restart
            ;;
        5)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac

    echo ""
    read -p "Press [Enter] to continue..."
done
