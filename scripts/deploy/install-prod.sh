#!/bin/bash
# install-prod.sh
# Production setup script for Bella Keys

echo "============================================="
echo "  Bella Keys - Production Setup Workflow"
echo "============================================="
echo ""
echo "PREREQUISITE CHECK"
echo "Please ensure the following are installed and running natively on this PC:"
echo "1. Docker (and docker compose)"
echo "2. PostgreSQL"
echo "3. Ollama"
echo ""
read -p "Are all prerequisites installed and running? (y/N): " PREREQ </dev/tty
if [[ "$PREREQ" != "y" && "$PREREQ" != "Y" ]]; then
    echo "Please install the prerequisites and run this script again."
    exit 1
fi

echo ""
DEFAULT_PATH="$HOME/.keys_sandbox/bella-keys"
read -p "Enter installation path [$DEFAULT_PATH]: " INSTALL_PATH </dev/tty
INSTALL_PATH=${INSTALL_PATH:-$DEFAULT_PATH}

# Expand tilde if present
INSTALL_PATH="${INSTALL_PATH/#\~/$HOME}"

echo "Creating directory at $INSTALL_PATH..."
mkdir -p "$INSTALL_PATH"
cd "$INSTALL_PATH" || exit 1

echo "Downloading configuration files..."
REPO_BASE="https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main"
curl -sSL "$REPO_BASE/docker/docker-compose-prod.yaml" -o docker-compose-prod.yaml
curl -sSL "$REPO_BASE/docker/.env.example" -o .env.example
curl -sSL "$REPO_BASE/scripts/database/init-db.sql" -o init-db.sql
curl -sSL "$REPO_BASE/scripts/deploy/run-prod.ps1" -o run-prod.ps1
curl -sSL "$REPO_BASE/scripts/deploy/update-prod.sh" -o update-prod.sh
chmod +x update-prod.sh

if [ ! -f "docker-compose-prod.yaml" ]; then
    echo "Failed to download configuration files. Please check your internet connection or the repository status."
    exit 1
fi

echo ""
echo "CONFIGURATION SETUP"
echo "How would you like to configure your .env file?"
echo "1) Interactive Setup (Prompt for values with defaults)"
echo "2) Offline Setup (Auto-generate and pause for manual editing)"
read -p "Select an option (1/2): " ENV_OPTION </dev/tty

if [ ! -f ".env" ]; then
    cp .env.example .env
fi

if [ "$ENV_OPTION" == "1" ]; then
    echo "Interactive Setup selected..."
    
    read -p "Enter EMS_PG_DB_PASSWORD [default_password]: " EMS_PASS </dev/tty
    EMS_PASS=${EMS_PASS:-default_password}
    
    read -p "Enter ARIZE_PG_DB_PASSWORD [default_password]: " ARIZE_PASS </dev/tty
    ARIZE_PASS=${ARIZE_PASS:-default_password}
    
    read -p "Enter LANGGRAPH_PG_DB_PASSWORD [default_password]: " LANGGRAPH_PASS </dev/tty
    LANGGRAPH_PASS=${LANGGRAPH_PASS:-default_password}
    
    # Use perl or sed to replace securely. Since bash can be on Mac or Linux/Windows Git Bash, sed -i has different syntax.
    # We will use temporary files for safety across platforms.
    sed "s/EMS_PG_DB_PASSWORD=.*/EMS_PG_DB_PASSWORD=$EMS_PASS/" .env > .env.tmp && mv .env.tmp .env
    sed "s/ARIZE_PG_DB_PASSWORD=.*/ARIZE_PG_DB_PASSWORD=$ARIZE_PASS/" .env > .env.tmp && mv .env.tmp .env
    sed "s/LANGGRAPH_PG_DB_PASSWORD=.*/LANGGRAPH_PG_DB_PASSWORD=$LANGGRAPH_PASS/" .env > .env.tmp && mv .env.tmp .env
    
    echo ".env updated interactively."
else
    echo "Offline Setup selected."
    echo "An .env file has been generated from .env.example in $INSTALL_PATH."
    echo "Please open this file in your favorite text editor, update the necessary variables (like database passwords), and save."
    read -p "Press [Enter] when you are done editing the .env file to continue..." </dev/tty
fi

echo ""
echo "DATABASE INITIALIZATION"
echo "The native PostgreSQL database must be initialized with the correct schemas and users."
echo "An initialization script has been downloaded to: $INSTALL_PATH/init-db.sql"
echo ""
echo "If you have 'psql' installed locally, we can attempt to run this automatically."
read -p "Would you like to run the database initialization via local psql now? (y/N): " RUN_PSQL </dev/tty

if [[ "$RUN_PSQL" == "y" || "$RUN_PSQL" == "Y" ]]; then
    read -p "Enter PostgreSQL host [localhost]: " PG_HOST </dev/tty
    PG_HOST=${PG_HOST:-localhost}
    read -p "Enter PostgreSQL admin user [postgres]: " PG_USER </dev/tty
    PG_USER=${PG_USER:-postgres}
    
    echo "Running psql... you may be prompted for the $PG_USER password multiple times."
    # We use grep in the sed script to pull the passwords to pass to psql if we used variables in the init-db.sql
    # Wait, the init-db.sql uses :'ems_pass' variables.
    
    EMS_PASS_VAL=$(grep "EMS_PG_DB_PASSWORD=" .env | cut -d '=' -f2)
    ARIZE_PASS_VAL=$(grep "ARIZE_PG_DB_PASSWORD=" .env | cut -d '=' -f2)
    LANGGRAPH_PASS_VAL=$(grep "LANGGRAPH_PG_DB_PASSWORD=" .env | cut -d '=' -f2)
    
    psql -h "$PG_HOST" -U "$PG_USER" -f init-db.sql \
        -v ems_pass="$EMS_PASS_VAL" \
        -v ems_test_pass="$EMS_PASS_VAL" \
        -v arize_pass="$ARIZE_PASS_VAL" \
        -v langgraph_pass="$LANGGRAPH_PASS_VAL"
        
    if [ $? -eq 0 ]; then
        echo "Database initialized successfully."
    else
        echo "Failed to initialize database via psql. You may need to run init-db.sql manually."
    fi
else
    echo "Skipping automatic database initialization."
    echo "Please ensure you run $INSTALL_PATH/init-db.sql against your native PostgreSQL instance before continuing."
    read -p "Press [Enter] once you have initialized the database..." </dev/tty
fi

echo ""
echo "DEPLOYMENT"
echo "Pulling latest images and starting services..."
docker compose -f docker-compose-prod.yaml pull
docker compose -f docker-compose-prod.yaml up -d

echo ""
echo "======================================================"
echo " Bella Keys production setup is complete!"
echo " Directory: $INSTALL_PATH"
echo " Use run-prod.ps1 to start/stop the services in the future."
echo "======================================================"
