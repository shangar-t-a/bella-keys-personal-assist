#!/bin/bash
# update-prod.sh
# Production update script for Bella Keys

echo "Updating Bella Keys deployment files and services..."
if [ ! -f "docker-compose.prod.yaml" ]; then
    echo "Error: docker-compose.prod.yaml not found in the current directory."
    echo "Please run this script from your Bella Keys installation directory."
    exit 1
fi

REPO_BASE="https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main"

echo "Downloading latest configuration files..."
curl -sSL "$REPO_BASE/docker/docker-compose.prod.yaml" -o docker-compose.prod.yaml
curl -sSL "$REPO_BASE/scripts/deploy/run-prod.ps1" -o run-prod.ps1
curl -sSL "$REPO_BASE/scripts/deploy/update-prod.sh" -o update-prod.sh.tmp
curl -sSL "$REPO_BASE/docker/.env.prod.example" -o .env.example

# Check for new variables in .env.example that are missing in .env
if [ -f ".env" ]; then
    echo "Checking for new environment variables..."
    NEW_VARS_FOUND=0

    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ -z "$line" ]] || [[ "$line" == \#* ]]; then
            continue
        fi
        VAR_NAME=$(echo "$line" | cut -d '=' -f 1)
        if ! grep -q "^${VAR_NAME}=" .env; then
            echo "New variable found: $VAR_NAME"
            echo "$line" >> .env
            NEW_VARS_FOUND=1
        fi
    done < .env.example

    if [ "$NEW_VARS_FOUND" -eq 1 ]; then
        echo ""
        echo "WARNING: New environment variables have been automatically appended to your .env file."
        echo "Please review your .env file to ensure the default values are correct before proceeding."
        read -p "Press [Enter] to continue or Ctrl+C to abort and edit the file..."
    else
        echo "No new environment variables found."
    fi
fi

# Step 1: Service Selection
echo ""
echo "============================================="
echo "  Step 1: Select Services"
echo "============================================="
echo ""
echo "  1. EMS only          — Auth + Expense Manager"
echo "  2. AI Chat           — Auth + EMS + Bella Chat + Qdrant  [recommended]"
echo "  3. AI Chat + Monitor — Everything above + Phoenix observability"
echo ""
read -p "Select services [1-3] (default: 2): " SERVICE_CHOICE
SERVICE_CHOICE="${SERVICE_CHOICE:-2}"

PROFILES=()
AI_CHAT_ENABLED=false

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
read -p "Enable the Web UI? [y/N]: " UI_CHOICE

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
        # EMS-only services selected — UI can only expose EMS
        PROFILES+=("--profile" "ui-ems")
        SERVICE_LABEL="$SERVICE_LABEL + Web UI (EMS only)"
    fi
fi

# Deploy
echo ""
echo "Active configuration: $SERVICE_LABEL"
echo ""

echo "Pulling latest Docker images..."
docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" pull

echo "Restarting services..."
docker compose -f docker-compose.prod.yaml "${PROFILES[@]}" up -d --remove-orphans

mv update-prod.sh.tmp update-prod.sh
chmod +x update-prod.sh

echo "Update complete."
