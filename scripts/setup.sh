#!/usr/bin/env bash
# Automates setting up the development environment, environment files, dependencies, and database.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Default configurations
AUTO_CONFIRM=false
DB_USER="postgres"
DB_HOST="localhost"
DB_PORT="5432"
AUTH_PASS="auth_password"
EMS_PASS="ems_password"
EMS_TEST_PASS="test123"
ARIZE_PASS="arize_password"
LANGGRAPH_PASS="langgraph_password"
RUN_DB_OPT=""

AUTH_PASS_ARG=""
EMS_PASS_ARG=""
EMS_TEST_PASS_ARG=""
ARIZE_PASS_ARG=""
LANGGRAPH_PASS_ARG=""

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -y|--yes)
            AUTO_CONFIRM=true
            shift
            ;;
        --db-user)
            DB_USER="$2"
            shift 2
            ;;
        --db-host)
            DB_HOST="$2"
            shift 2
            ;;
        --db-port)
            DB_PORT="$2"
            shift 2
            ;;
        --auth-pass)
            AUTH_PASS_ARG="$2"
            AUTH_PASS="$2"
            shift 2
            ;;
        --ems-pass)
            EMS_PASS_ARG="$2"
            EMS_PASS="$2"
            shift 2
            ;;
        --ems-test-pass)
            EMS_TEST_PASS_ARG="$2"
            EMS_TEST_PASS="$2"
            shift 2
            ;;
        --arize-pass)
            ARIZE_PASS_ARG="$2"
            ARIZE_PASS="$2"
            shift 2
            ;;
        --langgraph-pass)
            LANGGRAPH_PASS_ARG="$2"
            LANGGRAPH_PASS="$2"
            shift 2
            ;;
        --init-db)
            RUN_DB_OPT="yes"
            shift
            ;;
        --no-init-db)
            RUN_DB_OPT="no"
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [-y|--yes] [--db-user USER] [--db-host HOST] [--db-port PORT] [--auth-pass PASS] [--ems-pass PASS] [--ems-test-pass PASS] [--arize-pass PASS] [--langgraph-pass PASS] [--init-db|--no-init-db]"
            exit 1
            ;;
    esac
done

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Determine if database initialization is enabled
RUN_DB=false
if [ "$RUN_DB_OPT" = "yes" ]; then
    RUN_DB=true
elif [ "$RUN_DB_OPT" = "no" ]; then
    RUN_DB=false
elif [ "$AUTO_CONFIRM" = true ]; then
    # In non-interactive mode, DB init defaults to true unless explicitly disabled
    RUN_DB=true
fi

# Validation for non-interactive mode with DB initialization enabled
if [ "$AUTO_CONFIRM" = true ] && [ "$RUN_DB" = true ]; then
    MISSING_ARGS=()
    if [ -z "$AUTH_PASS_ARG" ]; then MISSING_ARGS+=("--auth-pass"); fi
    if [ -z "$EMS_PASS_ARG" ]; then MISSING_ARGS+=("--ems-pass"); fi
    if [ -z "$EMS_TEST_PASS_ARG" ]; then MISSING_ARGS+=("--ems-test-pass"); fi
    if [ -z "$ARIZE_PASS_ARG" ]; then MISSING_ARGS+=("--arize-pass"); fi
    if [ -z "$LANGGRAPH_PASS_ARG" ]; then MISSING_ARGS+=("--langgraph-pass"); fi
    
    if [ ${#MISSING_ARGS[@]} -ne 0 ]; then
        echo -e "${RED}❌ Error: In non-interactive mode with database initialization enabled, you must provide all passwords.${NC}"
        echo -e "Missing required arguments: ${MISSING_ARGS[*]}"
        echo -e "Use --no-init-db to skip database setup, or provide the missing passwords."
        exit 1
    fi
fi

# Helper function to get password interactively
# Arguments:
#   1: Password label (e.g. "ems_user")
#   2: Current value (if provided via CLI)
# Returns the password via stdout
prompt_password() {
    local label="$1"
    local provided_val="$2"
    local input_val=""

    if [ -n "$provided_val" ]; then
        # If provided via command line, use it as default
        read -s -p "Password for $label (current: $provided_val): " input_val >&2
        echo >&2
        echo "${input_val:-$provided_val}"
    else
        # If not provided, force the user to type a password
        while [ -z "$input_val" ]; do
            read -s -p "Enter password for $label: " input_val >&2
            echo >&2
            if [ -z "$input_val" ]; then
                echo -e "${RED}⚠️ Password cannot be empty. Please enter a password.${NC}" >&2
            fi
        done
        echo "$input_val"
    fi
}

# Prerequisites check
check_prerequisites() {
    echo -e "${BLUE}📋 Setup Prerequisites Checklist${NC}"
    echo "----------------------------------"
    echo "Before proceeding, please ensure you have the following installed:"
    echo -e "  1. ${GREEN}Python 3.13+${NC}"
    echo -e "  2. ${GREEN}uv Package Manager${NC} (Recommended: https://docs.astral.sh/uv/)"
    echo -e "  3. ${GREEN}Node.js & npm${NC}"
    echo -e "  4. ${GREEN}Docker & Docker Compose${NC} (Required for services)"
    echo -e "  5. ${GREEN}PostgreSQL${NC} (Required on host, port 5432)"
    echo
    
    if [ "$AUTO_CONFIRM" = true ]; then
        echo "Auto-confirming setup checklist..."
        return
    fi
    
    read -p "Do you want to continue with the setup? (Y/n) [default: Y]: " response
    if [ -z "$response" ]; then
        echo "Continuing with setup (default)..."
        response="Y"
    elif [[ "$response" =~ ^[Yy]$ ]]; then
        echo "Continuing with setup..."
    else
        echo -e "${RED}❌ Setup aborted by user.${NC}"
        exit 1
    fi
}

# Run prerequisites check
check_prerequisites
echo

echo -e "${BLUE}====================================${NC}"
echo -e "${BLUE}*   Bella Keys Environment Setup   *${NC}"
echo -e "${BLUE}====================================${NC}"
echo

# Helper function to setup environment files with warning
setup_env_file() {
    local src="$1"
    local dest="$2"
    local name="$3"

    if [ -f "$dest" ]; then
        if [ "$AUTO_CONFIRM" = true ]; then
            echo "Skipping overwrite of existing $name environment file in non-interactive mode."
            return
        fi

        echo -e "${YELLOW}⚠️  Warning: $name environment file already exists at: $dest${NC}"
        read -p "Do you want to overwrite it with the default template? (y/N) [default: N]: " overwrite_response
        if [ -z "$overwrite_response" ]; then
            echo "Keeping existing $name (default)."
            overwrite_response="N"
        elif [[ "$overwrite_response" =~ ^[Yy]$ ]]; then
            echo "Overwriting $name..."
            cp "$src" "$dest"
        else
            echo "Keeping existing $name..."
        fi
    else
        echo "Copying template to $dest..."
        cp "$src" "$dest"
    fi
}

echo -e "${BLUE}[1/3] Setting up environment files...${NC}"
setup_env_file "$REPO_ROOT/docker/.env.example" "$REPO_ROOT/docker/.env" "docker/.env"
setup_env_file "$REPO_ROOT/services/expense-manager-service/.env.sample" "$REPO_ROOT/services/expense-manager-service/.env" "expense-manager-service/.env"
setup_env_file "$REPO_ROOT/services/bella-chat-service/.env.sample" "$REPO_ROOT/services/bella-chat-service/.env" "bella-chat-service/.env"
setup_env_file "$REPO_ROOT/services/etl-pipelines/.env.sample" "$REPO_ROOT/services/etl-pipelines/.env" "etl-pipelines/.env"
setup_env_file "$REPO_ROOT/mcps/ems-mcp-server/.env.sample" "$REPO_ROOT/mcps/ems-mcp-server/.env" "ems-mcp-server/.env"
setup_env_file "$REPO_ROOT/keys-personal-assist-ui/.env.example" "$REPO_ROOT/keys-personal-assist-ui/.env" "keys-personal-assist-ui/.env"

# Sync passwords in newly copied environment files
if command -v python &> /dev/null || command -v python3 &> /dev/null; then
    PY_CMD="python"
    if ! command -v python &> /dev/null; then
        PY_CMD="python3"
    fi
    if $PY_CMD --version &> /dev/null; then
        echo "Syncing database passwords in environment files..."
        $PY_CMD "$REPO_ROOT/scripts/update-env-passwords.py" \
            --repo-root "$REPO_ROOT" \
            --ems-pass "$EMS_PASS" \
            --ems-test-pass "$EMS_TEST_PASS" \
            --arize-pass "$ARIZE_PASS" \
            --langgraph-pass "$LANGGRAPH_PASS" \
            --auth-pass "$AUTH_PASS" || {
                echo -e "${YELLOW}Warning: Failed to sync environment passwords via Python.${NC}"
            }
    else
        echo -e "${YELLOW}Warning: Python was found in PATH but is not functional (e.g. Windows Store alias). Please manually update the passwords in your .env files.${NC}"
    fi
else
    echo -e "${YELLOW}Warning: Python not found. Please manually update the passwords in your .env files.${NC}"
fi
echo

echo -e "${BLUE}[2/3] Installing/syncing dependencies...${NC}"
if command -v uv &> /dev/null; then
    echo -e "${GREEN}uv package manager found. Syncing Python dependencies...${NC}"
    
    echo "Syncing Expense Manager Service..."
    (cd "$REPO_ROOT/services/expense-manager-service" && uv sync --all-groups)
    
    echo "Syncing Bella Chat Service..."
    (cd "$REPO_ROOT/services/bella-chat-service" && uv sync --all-groups)
    
    echo "Syncing ETL Pipelines..."
    (cd "$REPO_ROOT/services/etl-pipelines" && uv sync --all-groups)
    
    echo "Syncing EMS MCP Server..."
    (cd "$REPO_ROOT/mcps/ems-mcp-server" && uv sync --all-groups)
else
    echo -e "${YELLOW}WARNING: 'uv' package manager not found. Skipping Python dependency sync.${NC}"
    echo "Please install uv (https://docs.astral.sh/uv/getting-started/installation/) or run 'pip install' manually."
fi

if command -v npm &> /dev/null; then
    echo -e "${GREEN}NPM found. Installing UI dependencies...${NC}"
    (cd "$REPO_ROOT/keys-personal-assist-ui" && npm install --legacy-peer-deps)
else
    echo -e "${YELLOW}WARNING: 'npm' not found. Skipping UI dependency install.${NC}"
fi
echo

echo -e "${BLUE}[3/3] Database Initialization...${NC}"
if command -v psql &> /dev/null; then
    # In interactive mode, if RUN_DB is false and no explicit DB choice was passed, prompt the user
    if [ "$AUTO_CONFIRM" = false ] && [ -z "$RUN_DB_OPT" ]; then
        read -p "Do you want to initialize the PostgreSQL databases now? (y/N) [default: N]: " response
        if [ -z "$response" ]; then
            RUN_DB=false
            echo "Skipping database initialization (default)."
        elif [[ "$response" =~ ^[Yy]$ ]]; then
            RUN_DB=true
            echo "Proceeding with database initialization..."
        else
            RUN_DB=false
            echo "Skipping database initialization..."
        fi
    fi

    if [ "$RUN_DB" = true ]; then
        if [ "$AUTO_CONFIRM" = false ]; then
            read -p "Enter PostgreSQL username (default: $DB_USER): " input_user
            DB_USER=${input_user:-$DB_USER}
            read -p "Enter PostgreSQL host (default: $DB_HOST): " input_host
            DB_HOST=${input_host:-$DB_HOST}
            read -p "Enter PostgreSQL port (default: $DB_PORT): " input_port
            DB_PORT=${input_port:-$DB_PORT}

            echo -e "${YELLOW}🔑 Database User Passwords:${NC}"
            AUTH_PASS=$(prompt_password "auth_user" "$AUTH_PASS_ARG")
            EMS_PASS=$(prompt_password "ems_user" "$EMS_PASS_ARG")
            EMS_TEST_PASS=$(prompt_password "ems_test_user" "$EMS_TEST_PASS_ARG")
            ARIZE_PASS=$(prompt_password "arize_user" "$ARIZE_PASS_ARG")
            LANGGRAPH_PASS=$(prompt_password "langgraph_user" "$LANGGRAPH_PASS_ARG")
        fi

        echo "Running init-db.sql..."
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" \
             -v ems_pass="$EMS_PASS" \
             -v ems_test_pass="$EMS_TEST_PASS" \
             -v arize_pass="$ARIZE_PASS" \
             -v langgraph_pass="$LANGGRAPH_PASS" \
             -v auth_pass="$AUTH_PASS" \
             -f "$REPO_ROOT/scripts/database/init-db.sql"
             
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}Database initialized successfully.${NC}"
            
            # Automatically update the environment files with the chosen passwords!
            if command -v python &> /dev/null || command -v python3 &> /dev/null; then
                PY_CMD="python"
                if ! command -v python &> /dev/null; then
                    PY_CMD="python3"
                fi
                if $PY_CMD --version &> /dev/null; then
                    echo "Updating passwords in environment files..."
                    $PY_CMD "$REPO_ROOT/scripts/update-env-passwords.py" \
                        --repo-root "$REPO_ROOT" \
                        --ems-pass "$EMS_PASS" \
                        --ems-test-pass "$EMS_TEST_PASS" \
                        --arize-pass "$ARIZE_PASS" \
                        --langgraph-pass "$LANGGRAPH_PASS" \
                        --auth-pass "$AUTH_PASS" || {
                            echo -e "${YELLOW}Warning: Failed to sync environment passwords via Python.${NC}"
                        }
                    echo -e "${GREEN}Environment files updated with database passwords.${NC}"
                else
                    echo -e "${YELLOW}Warning: Python was found in PATH but is not functional (e.g. Windows Store alias). Please manually update the passwords in your .env files.${NC}"
                fi
            else
                echo -e "${YELLOW}Warning: Python not found. Please manually update the passwords in your .env files.${NC}"
            fi
            
            # Automatically run database migrations for the Expense Manager Service (EMS)
            if [ -f "$REPO_ROOT/scripts/db-migrate.sh" ]; then
                echo "Running initial database migrations for Expense Manager Service..."
                DATABASE_URL="postgresql+asyncpg://ems_user:${EMS_PASS}@${DB_HOST}:${DB_PORT}/expense_manager_dev" \
                    bash "$REPO_ROOT/scripts/db-migrate.sh" || {
                        echo -e "${YELLOW}Warning: Failed to run initial database migrations automatically.${NC}"
                        echo -e "You can run them manually later using: ${BLUE}bash scripts/db-migrate.sh${NC}"
                    }
            fi
        else
            echo -e "${RED}ERROR: Database initialization failed.${NC}"
        fi
    else
        echo "Skipping database initialization."
    fi
else
    echo -e "${YELLOW}Note: 'psql' utility not found. If you have PostgreSQL installed,${NC}"
    echo "make sure it is in your PATH to initialize the database,"
    echo "or run the scripts/database/init-db.sql script manually."
fi

echo
echo -e "${BLUE}====================================${NC}"
echo -e "${GREEN}Setup completed!${NC}"
echo
echo -e "${YELLOW}📢 NEXT STEPS (CRITICAL):${NC}"
echo -e "1. ${RED}Configure Environment Variables:${NC}"
echo -e "   Open and edit the following files to add required secrets (e.g. GOOGLE_API_KEY):"
echo -e "   - ${BLUE}docker/.env${NC} (Primary config for Docker Compose)"
echo -e "   - ${BLUE}services/expense-manager-service/.env${NC}"
echo -e "   - ${BLUE}services/bella-chat-service/.env${NC}"
echo -e "   - ${BLUE}services/etl-pipelines/.env${NC}"
echo -e "   - ${BLUE}mcps/ems-mcp-server/.env${NC}"
echo -e "   - ${BLUE}keys-personal-assist-ui/.env${NC}"
echo
echo -e "2. ${GREEN}Run the Application:${NC}"
echo -e "   - Developer mode: run ${BLUE}bash scripts/run-dev.sh [profile]${NC}"
echo -e "   - Production mode: run ${BLUE}bash scripts/run-desktop-app.sh${NC}"
echo -e "${BLUE}====================================${NC}"
