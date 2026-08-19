@echo off
setlocal enabledelayedexpansion

set "SCRIPT_VERSION=1.0.0"
title Bella Keys - Production Manager v%SCRIPT_VERSION% (Windows Only)

rem Repository URLs for downloading latest production files
set "REPO_SCRIPT_URL=https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/scripts/deploy/bella-keys-manager.bat"
set "REPO_COMPOSE_URL=https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/docker/docker-compose.prod.yaml"
set "REPO_ENV_URL=https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/docker/.env.prod.example"
set "REPO_SQL_URL=https://raw.githubusercontent.com/shangar-t-a/bella-keys-personal-assist/main/scripts/database/init-db-prod.sql"

:INIT_CHECK
cls
echo =======================================================================
echo   Bella Keys - Production Manager v%SCRIPT_VERSION% (Windows Only)
echo =======================================================================
echo.

if not exist "docker-compose.prod.yaml" (
    echo [INFO] docker-compose.prod.yaml not found in current directory.
    echo [INFO] Attempting to download initial configuration from repository...
    echo.
    call :DOWNLOAD_CONFIGS
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to download initial setup files. Please check your internet connection.
        echo.
        pause
        exit /b 1
    )
)

if not exist ".env" (
    if exist ".env.example" (
        echo [INFO] .env file not found. Initializing .env from .env.example...
        copy /y .env.example .env >nul
        echo [SUCCESS] Initialized .env. Please verify database credentials in .env if needed.
        echo.
    ) else (
        echo [WARNING] Neither .env nor .env.example found.
    )
)

:SELECT_PROFILE
cls
echo =======================================================================
echo   Step 1: Select Service Profile
echo =======================================================================
echo.
echo   [1] EMS only          - Auth Service + Expense Manager [Default]
echo   [2] AI Chat           - Auth + EMS + Bella Chat + Qdrant [Experimental]
echo   [3] AI Chat + Monitor - Everything above + Phoenix Observability [Experimental]
echo.
set "SERVICE_CHOICE=1"
set /p "SERVICE_CHOICE=Select service profile [1-3] (default: 1): "

set "PROFILES="
set "AI_CHAT_ENABLED=false"
set "SERVICE_LABEL="

if "%SERVICE_CHOICE%"=="2" (
    set "PROFILES=--profile ai-chat"
    set "AI_CHAT_ENABLED=true"
    set "SERVICE_LABEL=AI Chat [Experimental] (auth-service, ems, bella-chat, ems-mcp, qdrant)"
) else if "%SERVICE_CHOICE%"=="3" (
    set "PROFILES=--profile ai-chat --profile monitor"
    set "AI_CHAT_ENABLED=true"
    set "SERVICE_LABEL=AI Chat + Monitor [Experimental] (auth-service, ems, bella-chat, ems-mcp, qdrant, phoenix)"
) else (
    set "SERVICE_LABEL=EMS only (auth-service, ems)"
)

echo.
echo =======================================================================
echo   Step 2: Web UI Scope Selection
echo =======================================================================
echo.
set "UI_CHOICE=N"
set /p "UI_CHOICE=Enable the Web UI container? [y/N] (default: N): "

if /i "%UI_CHOICE%"=="y" (
    if "%AI_CHAT_ENABLED%"=="true" (
        echo.
        echo   Which services should the Web UI expose?
        echo   [1] EMS only
        echo   [2] EMS + AI Chat
        echo.
        set "UI_SCOPE=2"
        set /p "UI_SCOPE=Select Web UI scope [1-2] (default: 2): "
        if "!UI_SCOPE!"=="1" (
            set "PROFILES=!PROFILES! --profile ui-ems"
            set "SERVICE_LABEL=!SERVICE_LABEL! + Web UI (EMS only)"
        ) else (
            set "PROFILES=!PROFILES! --profile ui"
            set "SERVICE_LABEL=!SERVICE_LABEL! + Web UI (EMS + AI Chat)"
        )
    ) else (
        set "PROFILES=!PROFILES! --profile ui-ems"
        set "SERVICE_LABEL=!SERVICE_LABEL! + Web UI (EMS only)"
    )
)

echo.
echo [INFO %TIME%] Active Profile configured: %SERVICE_LABEL%
echo.
timeout /t 2 >nul

:MAIN_MENU
cls
echo =======================================================================
echo   Bella Keys - Production Manager v%SCRIPT_VERSION% (Windows Only)
echo   Active Profile: %SERVICE_LABEL%
echo =======================================================================
echo.
echo   [1] Start Services
echo   [2] Stop Services
echo   [3] View Live Service Logs (Stream)
echo   [4] View Recent Service Logs (Last 100 lines)
echo   [5] Restart Services
echo   [6] Check Service Status
echo   [7] Update Services, Manager and Config (Self-update and pull images)
echo   [8] Change Service Profile / Web UI Scope
echo   [9] Exit
echo.

set "MENU_CHOICE=1"
set /p "MENU_CHOICE=Select an option [1-9] (default: 1): "

if "%MENU_CHOICE%"=="1" goto START_SERVICES
if "%MENU_CHOICE%"=="2" goto STOP_SERVICES
if "%MENU_CHOICE%"=="3" goto VIEW_LIVE_LOGS
if "%MENU_CHOICE%"=="4" goto VIEW_RECENT_LOGS
if "%MENU_CHOICE%"=="5" goto RESTART_SERVICES
if "%MENU_CHOICE%"=="6" goto CHECK_STATUS
if "%MENU_CHOICE%"=="7" goto UPDATE_SERVICES
if "%MENU_CHOICE%"=="8" goto SELECT_PROFILE
if "%MENU_CHOICE%"=="9" goto EXIT_SCRIPT

echo.
echo [ERROR] Invalid selection. Please try again.
echo.
pause
goto MAIN_MENU

:START_SERVICES
echo.
echo [LOG %TIME%] Starting containers for profile: %SERVICE_LABEL%...
docker compose -f docker-compose.prod.yaml %PROFILES% up -d
if %errorlevel% neq 0 (
    echo [ERROR %TIME%] Docker failed to start services. Ensure Docker Desktop is running.
) else (
    echo [SUCCESS %TIME%] Services started successfully.
)
echo.
pause
goto MAIN_MENU

:STOP_SERVICES
echo.
echo [LOG %TIME%] Stopping active containers...
docker compose -f docker-compose.prod.yaml %PROFILES% stop
echo [SUCCESS %TIME%] Services stopped.
echo.
pause
goto MAIN_MENU

:VIEW_LIVE_LOGS
echo.
echo [LOG %TIME%] Launching live log stream in a separate window...
start "Bella Keys - Live Logs" cmd /k "docker compose -f docker-compose.prod.yaml %PROFILES% logs -f"
echo [SUCCESS %TIME%] Live log window opened. You can close the log window anytime without affecting this manager.
echo.
pause
goto MAIN_MENU

:VIEW_RECENT_LOGS
echo.
echo [LOG %TIME%] Fetching last 100 log lines...
echo =======================================================================
docker compose -f docker-compose.prod.yaml %PROFILES% logs --tail=100
echo.
pause
goto MAIN_MENU

:RESTART_SERVICES
echo.
echo [LOG %TIME%] Restarting services...
docker compose -f docker-compose.prod.yaml %PROFILES% restart
echo [SUCCESS %TIME%] Services restarted.
echo.
pause
goto MAIN_MENU

:CHECK_STATUS
echo.
echo [LOG %TIME%] Active Container Status:
echo =======================================================================
docker compose -f docker-compose.prod.yaml %PROFILES% ps
echo.
pause
goto MAIN_MENU

:UPDATE_SERVICES
cls
echo =======================================================================
echo   Bella Keys - Updating Production Deployment and Manager v%SCRIPT_VERSION%
echo =======================================================================
echo.
echo [LOG %TIME%] Step 1/4: Checking for manager script self-update...
call :SELF_UPDATE_SCRIPT

echo.
echo [LOG %TIME%] Step 2/4: Downloading latest production configuration...
call :DOWNLOAD_CONFIGS
if %errorlevel% neq 0 (
    echo.
    echo [ERROR %TIME%] Update aborted due to network failure or disconnection.
    echo [INFO] Your existing deployment configuration remains untouched and active.
    echo.
    pause
    goto MAIN_MENU
)

call :SYNC_ENV_KEYS

echo.
echo [LOG %TIME%] Step 4/4: Pulling latest Docker images and recreating containers...
docker compose -f docker-compose.prod.yaml %PROFILES% pull
if %errorlevel% neq 0 (
    echo [WARNING %TIME%] Image pull reported warnings or incomplete layer downloads.
)

docker compose -f docker-compose.prod.yaml %PROFILES% up -d --remove-orphans
if %errorlevel% neq 0 (
    echo [ERROR %TIME%] Failed to recreate containers. Please inspect logs.
) else (
    echo.
    echo [SUCCESS %TIME%] Production update completed successfully!
)

echo.
pause
goto MAIN_MENU

:SELF_UPDATE_SCRIPT
echo [PROGRESS %TIME%] Checking for updated manager script...
curl.exe --fail --location --retry 3 --retry-delay 2 --connect-timeout 10 -s "%REPO_SCRIPT_URL%" -o "bella-keys-manager.bat.tmp"
if %errorlevel% neq 0 (
    echo [WARNING %TIME%] Could not check for script self-update (network timeout).
    if exist "bella-keys-manager.bat.tmp" del /f /q "bella-keys-manager.bat.tmp"
    exit /b 0
)

powershell -NoProfile -Command ^
    "$tmp = Get-Content 'bella-keys-manager.bat.tmp' -ErrorAction SilentlyContinue; ^
     if (-not $tmp) { exit 1 }; ^
     $match = $tmp | Select-String -Pattern 'set \"SCRIPT_VERSION=(.*?)\"'; ^
     if ($match) { ^
         $remoteVer = $match.Matches[0].Groups[1].Value; ^
         Write-Host ('[INFO] Remote manager script version: v' + $remoteVer + ' (Current: v%SCRIPT_VERSION%)'); ^
     } else { exit 1 }"

if %errorlevel% equ 0 (
    move /y "bella-keys-manager.bat.tmp" "%~nx0" >nul
    echo [SUCCESS %TIME%] Manager script self-updated successfully.
) else (
    if exist "bella-keys-manager.bat.tmp" del /f /q "bella-keys-manager.bat.tmp"
)
exit /b 0

:SYNC_ENV_KEYS
if not exist ".env" exit /b 0
echo.
echo [LOG %TIME%] Step 3/4: Syncing .env with new configuration keys...
powershell -NoProfile -Command "$envLines = Get-Content .env; $exampleLines = Get-Content .env.example; $added = 0; foreach ($line in $exampleLines) { if ([string]::IsNullOrWhiteSpace($line) -or $line.StartsWith('#')) { continue }; $varName = $line.Split('=')[0]; if (-not ($envLines | Select-String -Pattern ('^' + [regex]::Escape($varName) + '='))) { Add-Content -Path .env -Value $line; Write-Host '[INFO] Appended new environment variable:' $varName; $added++ } }; if ($added -gt 0) { Write-Host '[SUCCESS] Updated .env with' $added 'new variables.' } else { Write-Host '[INFO] .env is fully up to date.' }"
exit /b 0

:DOWNLOAD_CONFIGS
echo [PROGRESS %TIME%] Downloading docker-compose.prod.yaml...
curl.exe --fail --location --retry 3 --retry-delay 2 --connect-timeout 10 -s "%REPO_COMPOSE_URL%" -o "docker-compose.prod.yaml.tmp"
if %errorlevel% neq 0 (
    echo [ERROR %TIME%] Network error downloading docker-compose.prod.yaml.
    if exist "docker-compose.prod.yaml.tmp" del /f /q "docker-compose.prod.yaml.tmp"
    exit /b 1
)

echo [PROGRESS %TIME%] Downloading .env.prod.example...
curl.exe --fail --location --retry 3 --retry-delay 2 --connect-timeout 10 -s "%REPO_ENV_URL%" -o ".env.example.tmp"
if %errorlevel% neq 0 (
    echo [ERROR %TIME%] Network error downloading .env.prod.example.
    if exist "docker-compose.prod.yaml.tmp" del /f /q "docker-compose.prod.yaml.tmp"
    if exist ".env.example.tmp" del /f /q ".env.example.tmp"
    exit /b 1
)

if not exist "init-db-prod.sql" (
    echo [PROGRESS %TIME%] Downloading init-db-prod.sql...
    curl.exe --fail --location --retry 3 --retry-delay 2 --connect-timeout 10 -s "%REPO_SQL_URL%" -o "init-db-prod.sql.tmp"
    if !errorlevel! equ 0 (
        move /y "init-db-prod.sql.tmp" "init-db-prod.sql" >nul
    ) else (
        if exist "init-db-prod.sql.tmp" del /f /q "init-db-prod.sql.tmp"
    )
)

move /y "docker-compose.prod.yaml.tmp" "docker-compose.prod.yaml" >nul
move /y ".env.example.tmp" ".env.example" >nul
echo [SUCCESS %TIME%] Downloaded latest configuration files successfully.
exit /b 0

:EXIT_SCRIPT
echo.
echo [LOG %TIME%] Exiting Production Manager. Have a great day!
echo.
exit /b 0
