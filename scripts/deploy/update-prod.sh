#!/bin/bash
# update-prod.sh
# Production update script for Bella Keys

echo "Updating Bella Keys deployment files and services..."
if [ ! -f "docker-compose-prod.yaml" ]; then
    echo "Error: docker-compose-prod.yaml not found in the current directory."
    echo "Please run this script from your Bella Keys installation directory."
    exit 1
fi

REPO_BASE="https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main"

echo "Downloading latest configuration files..."
curl -sSL "$REPO_BASE/docker/docker-compose-prod.yaml" -o docker-compose-prod.yaml
curl -sSL "$REPO_BASE/scripts/deploy/run-prod.ps1" -o run-prod.ps1
curl -sSL "$REPO_BASE/scripts/deploy/update-prod.sh" -o update-prod.sh.tmp
curl -sSL "$REPO_BASE/docker/.env.example" -o .env.example

# Check for new variables in .env.example that are missing in .env
if [ -f ".env" ]; then
    echo "Checking for new environment variables..."
    NEW_VARS_FOUND=0
    
    # Read each line of .env.example
    while IFS= read -r line || [[ -n "$line" ]]; do
        # Skip empty lines and comments
        if [[ -z "$line" ]] || [[ "$line" == \#* ]]; then
            continue
        fi
        
        # Extract variable name
        VAR_NAME=$(echo "$line" | cut -d '=' -f 1)
        
        # Check if variable exists in .env
        if ! grep -q "^${VAR_NAME}=" .env; then
            echo "New variable found: $VAR_NAME"
            # Append the new variable to the end of the .env file
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

echo "Pulling latest Docker images..."
docker compose -f docker-compose-prod.yaml pull

echo "Restarting services..."
docker compose -f docker-compose-prod.yaml up -d --remove-orphans

# Replace the current update script with the newly downloaded one for next time
mv update-prod.sh.tmp update-prod.sh
chmod +x update-prod.sh

echo "Update complete."
