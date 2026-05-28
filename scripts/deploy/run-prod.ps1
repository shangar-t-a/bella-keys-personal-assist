# run-prod.ps1
# Production run script for Bella Keys on Windows

if (!(Test-Path "docker-compose-prod.yaml")) {
    Write-Host "Error: docker-compose-prod.yaml not found in the current directory." -ForegroundColor Red
    Write-Host "Please run this script from your Bella Keys installation directory." -ForegroundColor Yellow
    exit
}

while ($true) {
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "  Bella Keys - Service Manager" -ForegroundColor Cyan
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. Start Services"
    Write-Host "2. Stop Services"
    Write-Host "3. View Service Logs"
    Write-Host "4. Restart Services"
    Write-Host "5. Exit"
    Write-Host ""
    
    $choice = Read-Host "Select an option"

    switch ($choice) {
        "1" { 
            Write-Host "Starting services..." -ForegroundColor Green
            docker compose -f docker-compose-prod.yaml up -d
        }
        "2" { 
            Write-Host "Stopping services..." -ForegroundColor Yellow
            docker compose -f docker-compose-prod.yaml stop
        }
        "3" { 
            docker compose -f docker-compose-prod.yaml logs -f 
        }
        "4" { 
            Write-Host "Restarting services..." -ForegroundColor Green
            docker compose -f docker-compose-prod.yaml restart 
        }
        "5" { 
            exit 
        }
        default { 
            Write-Host "Invalid option. Please try again." -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Read-Host "Press Enter to continue"
}
