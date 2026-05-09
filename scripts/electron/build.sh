#!/usr/bin/env bash
# Build Electron app with optional service selection
# Run from repo root: bash scripts/build-electron.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script configuration
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
UI_DIR="$REPO_ROOT/keys-personal-assist-ui"
BUILD_DIR="$REPO_ROOT/build"

echo -e "${BLUE}🔨 Bella Keys Electron Build Script${NC}"
echo "=================================="

# Prevent running on Windows Git Bash/MSYS (unless forced)
if [[ "${1:-}" != "-f" ]]; then
    if [[ "$(uname)" == *"MINGW"* ]] || [[ "$(uname)" == *"MSYS"* ]] || [[ "$(uname)" == *"CYGWIN"* ]]; then
        echo -e "${RED}❌ ERROR: You are running the Linux/macOS shell script on Windows.${NC}"
        echo -e "${YELLOW}The Windows environment (like Git Bash) cannot correctly extract electron-builder dependencies (such as winCodeSign) due to symlink privilege issues.${NC}"
        echo
        echo -e "Please open ${GREEN}Command Prompt${NC} or ${GREEN}PowerShell${NC} and run:"
        echo -e "  ${BLUE}.\\scripts\\build-electron.bat${NC}"
        echo
        echo -e "${BLUE}Tip: If you are sure you want to proceed in this environment, use the -f flag:${NC}"
        echo -e "  ${BLUE}bash scripts/build-electron.sh -f${NC}"
        exit 1
    fi
elif [[ "$(uname)" == *"MINGW"* ]] || [[ "$(uname)" == *"MSYS"* ]] || [[ "$(uname)" == *"CYGWIN"* ]]; then
    echo -e "${YELLOW}⚠️  WARNING: Bypassing Windows environment check due to -f flag.${NC}"
    echo -e "${YELLOW}Ensure you have sufficient privileges to create symbolic links if required.${NC}"
    echo
fi

# Create build directory
mkdir -p "$BUILD_DIR"

# Service selection functions
show_service_menu() {
    echo -e "${YELLOW}Select services to include in the build:${NC}"
    echo "1) Minimal (Expense Manager only) - Lightweight"
    echo "2) Standard (Expense Manager + Bella Chat) - Recommended"
    echo "3) Enhanced (Expense Manager + Bella Chat + Observability) - Heavy resources"
    echo "4) Custom - Choose individual services"
    echo
    read -p "Enter your choice (1-4): " choice
    
    case $choice in
        1)
            SERVICES="minimal"
            VITE_BELLA_CHAT_ENABLED=false
            VITE_EXPENSE_MANAGER_ENABLED=true
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false
            ;;
        2)
            SERVICES="standard"
            VITE_BELLA_CHAT_ENABLED=true
            VITE_EXPENSE_MANAGER_ENABLED=true
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false
            ;;
        3)
            SERVICES="enhanced"
            VITE_BELLA_CHAT_ENABLED=true
            VITE_EXPENSE_MANAGER_ENABLED=true
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=true
            ;;
        4)
            SERVICES="custom"
            select_custom_services
            ;;
        *)
            echo -e "${RED}Invalid choice. Using standard configuration.${NC}"
            SERVICES="standard"
            VITE_BELLA_CHAT_ENABLED=true
            VITE_EXPENSE_MANAGER_ENABLED=true
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false
            ;;
    esac
}

select_custom_services() {
    echo -e "${YELLOW}Custom Service Selection:${NC}"
    
    # Bella Chat
    read -p "Include Bella Chat service? (y/N): " include_bella
    if [[ "${include_bella,,}" =~ ^(yes|y)$ ]]; then
        VITE_BELLA_CHAT_ENABLED=true
    else
        VITE_BELLA_CHAT_ENABLED=false
    fi
    
    # Expense Manager
    read -p "Include Expense Manager service? (Y/n): " include_ems
    if [[ "${include_ems,,}" =~ ^(no|n)$ ]]; then
        VITE_EXPENSE_MANAGER_ENABLED=false
    else
        VITE_EXPENSE_MANAGER_ENABLED=true
    fi
    
    # Bella Chat Observability (only if Bella Chat is enabled)
    if [ "$VITE_BELLA_CHAT_ENABLED" = true ]; then
        read -p "Include Bella Chat Observability (Phoenix, Arize)? (y/N): " include_obs
        if [[ "${include_obs,,}" =~ ^(yes|y)$ ]]; then
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=true
        else
            VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false
        fi
    else
        VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false
    fi
}

# Build configuration functions
configure_environment() {
    echo -e "${BLUE}🔧 Configuring build environment...${NC}"
    
    # Create .env.production file
    cat > "$UI_DIR/.env.production" << EOF
# Production build configuration
VITE_APP_ENV=electron
VITE_BELLA_CHAT_ENABLED=$VITE_BELLA_CHAT_ENABLED
VITE_EXPENSE_MANAGER_ENABLED=$VITE_EXPENSE_MANAGER_ENABLED
VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=$VITE_BELLA_CHAT_OBSERVABILITY_ENABLED
VITE_BUILD_TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
VITE_BUILD_SERVICES=$SERVICES
EOF
    
    echo "Environment configured for: $SERVICES"
    echo "Bella Chat: $VITE_BELLA_CHAT_ENABLED"
    echo "Expense Manager: $VITE_EXPENSE_MANAGER_ENABLED"
    echo "Bella Chat Observability: $VITE_BELLA_CHAT_OBSERVABILITY_ENABLED"
}

# Build functions
build_ui() {
    echo -e "${BLUE}🏗️  Building UI components...${NC}"
    
    cd "$UI_DIR"
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "Installing dependencies..."
        npm ci
    fi
    
    # Build for production
    echo "Building Electron app..."
    npm run build:electron
    
    if [ $? -eq 0 ]; then
        # Verify Electron build output
        if [ ! -f "out/main/index.js" ]; then
            echo -e "${RED}❌ Electron main entry file not found after build${NC}"
            exit 1
        fi
        
        if [ ! -f "out/preload/index.mjs" ]; then
            echo -e "${RED}❌ Electron preload file not found after build${NC}"
            exit 1
        fi
        
        if [ ! -f "out/renderer/index.html" ]; then
            echo -e "${RED}❌ Electron renderer build not found${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ Electron build completed successfully${NC}"
    else
        echo -e "${RED}❌ Electron build failed${NC}"
        exit 1
    fi
}

package_app() {
    echo -e "${BLUE}📦 Packaging Electron app...${NC}"
    
    cd "$UI_DIR"
    
    # Set environment variables to disable code signing completely
    export CSC_LINK=""
    export CSC_KEY_PASSWORD=""
    export CSC_IDENTITY_AUTO_DISCOVERY=false
    export CSC_IDENTITY=""
    
    # Disable code signing for all platforms
    export WIN_CSC_LINK=""
    export WIN_CSC_KEY_PASSWORD=""
    export WIN_CSC_IDENTITY=""
    
    # Clear electron-builder cache to avoid signing tool symbolic link issues
    if [ -d "$HOME/.cache/electron-builder" ]; then
        echo "Clearing electron-builder cache to avoid symbolic link issues..."
        rm -rf "$HOME/.cache/electron-builder"
    fi
    
    # Build without code signing
    echo "Building without code signing to avoid Windows permission issues..."
    npm run dist -- --publish=never
    
    if [ $? -eq 0 ]; then
        # Verify packaged app
        if [ ! -f "release/win-unpacked/resources/app.asar" ] && [ ! -f "release/linux-unpacked/resources/app.asar" ] && [ ! -f "release/mac/Bella Keys.app/Contents/Resources/app.asar" ]; then
            echo -e "${RED}❌ Packaged app.asar not found${NC}"
            exit 1
        fi
        
        echo -e "${GREEN}✅ App packaged successfully${NC}"
        
        # Move artifacts to build directory
        if [ -d "release" ]; then
            cp -r release/* "$BUILD_DIR/" 2>/dev/null || true
        fi
    else
        echo -e "${RED}❌ App packaging failed${NC}"
        exit 1
    fi
}

create_service_info() {
    echo -e "${BLUE}📋 Creating service information...${NC}"
    
    cat > "$BUILD_DIR/service-info.json" << EOF
{
  "buildTimestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "services": "$SERVICES",
  "features": {
    "bellaChat": $VITE_BELLA_CHAT_ENABLED,
    "expenseManager": $VITE_EXPENSE_MANAGER_ENABLED,
    "bellaChatObservability": $VITE_BELLA_CHAT_OBSERVABILITY_ENABLED
  },
  "requirements": {
    "docker": true,
    "ports": {
      "expenseManager": $([ "$VITE_EXPENSE_MANAGER_ENABLED" = true ] && echo "8000" || echo "null"),
      "bellaChat": $([ "$VITE_BELLA_CHAT_ENABLED" = true ] && echo "5000" || echo "null"),
      "qdrant": $([ "$VITE_BELLA_CHAT_ENABLED" = true ] && echo "6333" || echo "null"),
      "postgres": $([ "$VITE_EXPENSE_MANAGER_ENABLED" = true ] && echo "5432" || echo "null"),
      "phoenix": $([ "$VITE_BELLA_CHAT_ENABLED" = true ] && [ "$VITE_BELLA_CHAT_OBSERVABILITY_ENABLED" = true ] && echo "6006" || echo "null"),
      "arizeGrpc": $([ "$VITE_BELLA_CHAT_ENABLED" = true ] && [ "$VITE_BELLA_CHAT_OBSERVABILITY_ENABLED" = true ] && echo "4317" || echo "null")
    }
  }
}
EOF
}

# Main execution
main() {
    echo -e "${BLUE}Starting build process...${NC}"
    echo
    
    # Show service selection menu
    show_service_menu
    echo
    
    # Configure environment
    configure_environment
    echo
    
    # Build UI
    build_ui
    echo
    
    # Package app
    package_app
    echo
    
    # Create service info
    create_service_info
    echo
    
    echo -e "${GREEN}🎉 Build completed successfully!${NC}"
    echo -e "${BLUE}Build artifacts located in: $BUILD_DIR${NC}"
    echo
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Run the app with: bash scripts/services/run-services-installed-app.sh"
    echo "2. Check service-info.json for required services"
    echo
}

# Run main function
main "$@"
