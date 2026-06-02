# run-prod.ps1
# Production run script for Bella Keys on Windows

if (!(Test-Path "docker-compose.prod.yaml")) {
    Write-Host "Error: docker-compose.prod.yaml not found in the current directory." -ForegroundColor Red
    Write-Host "Please run this script from your Bella Keys installation directory." -ForegroundColor Yellow
    exit
}

# Step 1: Service Selection
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Step 1: Select Services" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  1. EMS only          " -NoNewline; Write-Host "- Auth + Expense Manager" -ForegroundColor Gray
Write-Host "  2. AI Chat           " -NoNewline; Write-Host "- Auth + EMS + Bella Chat + Qdrant  " -NoNewline -ForegroundColor Gray; Write-Host "[recommended]" -ForegroundColor Green
Write-Host "  3. AI Chat + Monitor " -NoNewline; Write-Host "- Everything above + Phoenix observability" -ForegroundColor Gray
Write-Host ""

$serviceChoice = Read-Host "Select services [1-3] (default: 2)"
if ([string]::IsNullOrWhiteSpace($serviceChoice)) { $serviceChoice = "2" }

$ProfileArgs    = @()
$AiChatEnabled  = $false
$ServiceLabel   = ""

switch ($serviceChoice) {
    "1" {
        $ServiceLabel  = "EMS only (auth-service, ems)"
    }
    "2" {
        $ProfileArgs   = @("--profile", "ai-chat")
        $AiChatEnabled = $true
        $ServiceLabel  = "AI Chat (auth-service, ems, bella-chat, ems-mcp, qdrant)"
    }
    "3" {
        $ProfileArgs   = @("--profile", "ai-chat", "--profile", "monitor")
        $AiChatEnabled = $true
        $ServiceLabel  = "AI Chat + Monitor (auth-service, ems, bella-chat, ems-mcp, qdrant, phoenix)"
    }
    default {
        Write-Host "Invalid selection. Defaulting to AI Chat." -ForegroundColor Yellow
        $ProfileArgs   = @("--profile", "ai-chat")
        $AiChatEnabled = $true
        $ServiceLabel  = "AI Chat (auth-service, ems, bella-chat, ems-mcp, qdrant)"
    }
}

# Step 2: Web UI (optional)
Write-Host ""
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Step 2: Web UI (optional)" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

$uiChoice = Read-Host "Enable the Web UI? [y/N]"

if ($uiChoice -match "^[Yy]$") {
    if ($AiChatEnabled) {
        Write-Host ""
        Write-Host "  Which services should the Web UI expose?"
        Write-Host "  1. EMS only"
        Write-Host "  2. EMS + AI Chat"
        Write-Host ""
        $uiScope = Read-Host "Select UI scope [1-2] (default: 2)"
        if ([string]::IsNullOrWhiteSpace($uiScope)) { $uiScope = "2" }

        if ($uiScope -eq "1") {
            $ProfileArgs  += @("--profile", "ui-ems")
            $ServiceLabel += " + Web UI (EMS only)"
        } else {
            $ProfileArgs  += @("--profile", "ui")
            $ServiceLabel += " + Web UI (EMS + AI Chat)"
        }
    } else {
        # EMS-only services — UI can only expose EMS
        $ProfileArgs  += @("--profile", "ui-ems")
        $ServiceLabel += " + Web UI (EMS only)"
    }
}

Write-Host ""
Write-Host "Active configuration: $ServiceLabel" -ForegroundColor Cyan
Write-Host ""

# Service Manager Loop
while ($true) {
    Write-Host "=============================================" -ForegroundColor Cyan
    Write-Host "  Bella Keys - Service Manager" -ForegroundColor Cyan
    Write-Host "  $ServiceLabel" -ForegroundColor DarkCyan
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
            docker compose -f docker-compose.prod.yaml @ProfileArgs up -d
        }
        "2" {
            Write-Host "Stopping services..." -ForegroundColor Yellow
            docker compose -f docker-compose.prod.yaml @ProfileArgs stop
        }
        "3" {
            docker compose -f docker-compose.prod.yaml @ProfileArgs logs -f
        }
        "4" {
            Write-Host "Restarting services..." -ForegroundColor Green
            docker compose -f docker-compose.prod.yaml @ProfileArgs restart
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
