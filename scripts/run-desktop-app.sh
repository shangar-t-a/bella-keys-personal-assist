#!/usr/bin/env bash
# Run Bella Keys desktop app with services from GitHub Container Registry
# Run from repo root: bash scripts/run-desktop-app.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UI_DIR="$REPO_ROOT/keys-personal-assist-ui"
BUILD_DIR="$REPO_ROOT/build"
DOCKER_DIR="$REPO_ROOT/docker"
ENV_FILE="$DOCKER_DIR/.env"

# Default configuration
REGISTRY="ghcr.io"
REPO_OWNER="shangar-t-a"  # Update this to match your GitHub username
SERVICES_TO_RUN=""

echo -e "${BLUE}🚀 Bella Keys Desktop App Runner${NC}"
echo "=================================="

# Service management functions
check_prerequisites_prompt() {
    echo -e "${YELLOW}📋 Prerequisites Checklist:${NC}"
    echo -e "  1. ${BLUE}Docker Desktop / Engine${NC} (Must be installed and running)"
    echo -e "  2. ${BLUE}PostgreSQL${NC} (Must be running on your host machine on port 5432)"
    echo -e "  3. ${BLUE}Environment Setup${NC} (Run 'bash scripts/setup.sh' to configure files and databases)"
    echo -e "  4. ${BLUE}Packaged Electron App${NC} (Must be built - run 'bash scripts/electron/build.sh' or build.bat first)"
    echo -e "  5. ${BLUE}Ollama${NC} (Optional - required if using local-first AI models)"
    echo
    
    read -p "Have you installed and started all the required prerequisites? (y/N): " response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${RED}❌ Aborted. Please install and run all prerequisites before launching the app.${NC}"
        echo "For detailed setup instructions, please refer to: docs/user/setup-guide.md"
        exit 1
    fi
}

check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed or not in PATH${NC}"
        echo "Please install Docker Desktop or Docker Engine"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        echo -e "${RED}❌ Docker daemon is not running${NC}"
        echo "Please start Docker Desktop or Docker service"
        exit 1
    fi
    
    echo -e "${GREEN}✅ Docker is available and running${NC}"
}

check_build_info() {
    local service_info="$BUILD_DIR/service-info.json"
    
    if [ ! -f "$service_info" ]; then
        echo -e "${YELLOW}⚠️  No build information found. Using default configuration.${NC}"
        SERVICES_TO_RUN="standard"
        return
    fi
    
    echo -e "${BLUE}📋 Reading build configuration...${NC}"
    SERVICES_TO_RUN=$(grep -o '"services": *"[^"]*"' "$service_info" 2>/dev/null | awk -F'"' '{print $4}' || echo "standard")
    if [ -z "$SERVICES_TO_RUN" ]; then SERVICES_TO_RUN="standard"; fi
    echo "Build configuration: $SERVICES_TO_RUN"
}

show_service_menu() {
    echo -e "${YELLOW}Select services to run:${NC}"
    echo "1) Use build configuration ($SERVICES_TO_RUN)"
    echo "2) Minimal (Expense Manager only)"
    echo "3) Standard (Expense Manager + Bella Chat)"
    echo "4) Enhanced (Expense Manager + Bella Chat + Observability)"
    echo "5) Custom selection"
    echo
    read -p "Enter your choice (1-5): " choice
    
    case $choice in
        1)
            # Use build configuration
            ;;
        2)
            SERVICES_TO_RUN="minimal"
            ;;
        3)
            SERVICES_TO_RUN="standard"
            ;;
        4)
            SERVICES_TO_RUN="enhanced"
            ;;
        5)
            select_custom_services
            ;;
        *)
            echo -e "${RED}Invalid choice. Using: $SERVICES_TO_RUN${NC}"
            ;;
    esac
}

select_custom_services() {
    echo -e "${YELLOW}Custom Service Selection:${NC}"
    
    local bella_chat=false
    local expense_manager=true
    local bella_chat_observability=false
    
    read -p "Include Bella Chat service? (y/N): " include_bella
    if [[ "${include_bella,,}" =~ ^(yes|y)$ ]]; then
        bella_chat=true
    fi
    
    read -p "Include Expense Manager service? (Y/n): " include_ems
    if [[ "${include_ems,,}" =~ ^(no|n)$ ]]; then
        expense_manager=false
    fi
    
    # Bella Chat Observability (only if Bella Chat is enabled)
    if $bella_chat; then
        read -p "Include Bella Chat Observability (Phoenix, Arize)? (y/N): " include_obs
        if [[ "${include_obs,,}" =~ ^(yes|y)$ ]]; then
            bella_chat_observability=true
        fi
    fi
    
    # Determine service profile
    if $bella_chat_observability; then
        SERVICES_TO_RUN="enhanced"
    elif $bella_chat && $expense_manager; then
        SERVICES_TO_RUN="standard"
    elif $expense_manager; then
        SERVICES_TO_RUN="minimal"
    else
        echo -e "${RED}At least Expense Manager must be selected${NC}"
        select_custom_services
    fi
}

pull_services() {
    echo -e "${BLUE}📥 Pulling services from GitHub Container Registry...${NC}"
    
    # Always pull expense manager
    echo "Pulling expense-manager-service..."
    docker pull "$REGISTRY/$REPO_OWNER/expense-manager-service:latest" || {
        echo -e "${YELLOW}⚠️  Could not pull expense-manager-service, will build locally${NC}"
    }
    
    # Pull bella chat if needed
    if [[ "$SERVICES_TO_RUN" == "standard" || "$SERVICES_TO_RUN" == "enhanced" ]]; then
        echo "Pulling bella-chat-service..."
        docker pull "$REGISTRY/$REPO_OWNER/bella-chat-service:latest" || {
            echo -e "${YELLOW}⚠️  Could not pull bella-chat-service, will build locally${NC}"
        }
        
        echo "Pulling qdrant..."
        docker pull qdrant/qdrant:latest || {
            echo -e "${YELLOW}⚠️  Could not pull qdrant${NC}"
        }
    fi
    
    # Pull observability services if enhanced profile
    if [[ "$SERVICES_TO_RUN" == "enhanced" ]]; then
        echo "Pulling phoenix..."
        docker pull arizephoenix/phoenix:latest || {
            echo -e "${YELLOW}⚠️  Could not pull phoenix${NC}"
        }
    fi
    
    echo -e "${GREEN}✅ Service pull completed${NC}"
}

setup_environment() {
    echo -e "${BLUE}🔧 Setting up environment...${NC}"
    
    # Create .env file if it doesn't exist
    if [ ! -f "$ENV_FILE" ]; then
        echo "Creating .env file from template..."
        cp "$DOCKER_DIR/.env.example" "$ENV_FILE"
        echo -e "${YELLOW}⚠️  Please review and update $ENV_FILE with your configuration${NC}"
    fi
    
    # Source environment variables
    set -a
    source "$ENV_FILE"
    set +a
}

start_services() {
    echo -e "${BLUE}🔄 Starting backend services...${NC}"
    
    cd "$DOCKER_DIR"
    
    # Stop any existing services
    echo "Stopping existing services..."
    docker compose down 2>/dev/null || true
    
    # Start services based on profile
    case $SERVICES_TO_RUN in
        "minimal")
            echo "Starting minimal services (Expense Manager only)..."
            docker compose -f docker-compose.prod.yaml up -d expense-manager-service
            ;;
        "standard")
            echo "Starting standard services (Expense Manager + Bella Chat)..."
            docker compose -f docker-compose.prod.yaml --profile bella up -d
            ;;
        "enhanced")
            echo "Starting enhanced services (Expense Manager + Bella Chat + Observability)..."
            docker compose -f docker-compose.prod.yaml --profile bella --profile full up -d
            ;;
        *)
            echo -e "${RED}Unknown service profile: $SERVICES_TO_RUN${NC}"
            exit 1
            ;;
    esac
    
    # Wait for services to be ready
    echo -e "${BLUE}⏳ Waiting for services to be ready...${NC}"
    sleep 10
    
    # Check service health
    check_service_health
}

check_service_health() {
    echo -e "${BLUE}🏥 Checking service health...${NC}"
    
    local healthy=true
    
    # Check expense manager
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Expense Manager Service is healthy${NC}"
    else
        echo -e "${RED}❌ Expense Manager Service is not responding${NC}"
        healthy=false
    fi
    
    # Check bella chat if enabled
    if [[ "$SERVICES_TO_RUN" == "standard" || "$SERVICES_TO_RUN" == "enhanced" ]]; then
        if curl -s http://localhost:5000/health > /dev/null 2>&1; then
            echo -e "${GREEN}✅ Bella Chat Service is healthy${NC}"
        else
            echo -e "${RED}❌ Bella Chat Service is not responding${NC}"
            healthy=false
        fi
    fi
    
    if [ "$healthy" = false ]; then
        echo -e "${YELLOW}⚠️  Some services are not healthy. The app may not work properly.${NC}"
        echo "Check docker logs for more information: docker compose logs"
    fi
}

launch_electron_app() {
    echo -e "${BLUE}🖥️  Launching Electron app...${NC}"
    
    local app_launched=false
    
    if [ "$(uname)" == "Darwin" ] && [ -d "$BUILD_DIR/mac/Bella Keys.app" ]; then
        echo "Starting Bella Keys desktop app (macOS)..."
        open "$BUILD_DIR/mac/Bella Keys.app"
        app_launched=true
    elif [ -f "$BUILD_DIR/linux-unpacked/bella-keys" ]; then
        echo "Starting Bella Keys desktop app (Linux)..."
        "$BUILD_DIR/linux-unpacked/bella-keys" &
        app_launched=true
    elif [ -f "$BUILD_DIR/win-unpacked/Bella Keys.exe" ]; then
        echo "Starting Bella Keys desktop app (Windows)..."
        "$BUILD_DIR/win-unpacked/Bella Keys.exe" &
        app_launched=true
    fi
    
    if [ "$app_launched" = false ]; then
        echo -e "${RED}❌ Packaged Electron app not found in build directory.${NC}"
        echo "Please run bash scripts/electron/build.sh first to build for production."
        exit 1
    fi
}

cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    cd "$DOCKER_DIR"
    docker compose down
    echo -e "${GREEN}✅ Services stopped${NC}"
}

# Set up signal handlers
trap cleanup EXIT INT TERM

# Main execution
main() {
    # Prompt and confirm prerequisites
    check_prerequisites_prompt
    echo
    
    echo -e "${BLUE}Starting Bella Keys desktop app...${NC}"
    echo
    
    # Check Docker service
    check_docker
    echo
    
    # Check build configuration
    check_build_info
    echo
    
    # Show service selection menu
    show_service_menu
    echo
    
    # Pull services
    pull_services
    echo
    
    # Setup environment
    setup_environment
    echo
    
    # Start services
    start_services
    echo
    
    # Launch app
    launch_electron_app
}

# Run main function
main "$@"
