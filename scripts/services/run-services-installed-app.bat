@echo off
REM Run Bella Keys desktop app with services from GitHub Container Registry (Windows)
REM Run from repo root: scripts\run-desktop-app.bat

setlocal enabledelayedexpansion

REM Script configuration
set "REPO_ROOT=%~dp0..\.."
set "UI_DIR=%REPO_ROOT%\keys-personal-assist-ui"
set "BUILD_DIR=%REPO_ROOT%\build"
set "DOCKER_DIR=%REPO_ROOT%\docker"
set "ENV_FILE=%DOCKER_DIR%\.env"

REM Default configuration
set "REGISTRY=ghcr.io"
set "REPO_OWNER=shangar-t-a"
set "SERVICES_TO_RUN="

echo.
echo ==================================
echo * Bella Keys Desktop App Runner *
echo ==================================
echo.

goto :main

REM Service management functions
:check_docker
echo Checking Docker availability...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not in PATH
    echo Please install Docker Desktop for Windows
    pause
    exit /b 1
)

docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker daemon is not running
    echo Please start Docker Desktop
    pause
    exit /b 1
)

echo SUCCESS: Docker is available and running
goto :eof

:check_build_info
set "service_info=%BUILD_DIR%\service-info.json"

if not exist "%service_info%" (
    echo WARNING: No build information found. Using default configuration.
    set "SERVICES_TO_RUN=standard"
    goto :eof
)

echo * Reading build configuration...
REM Simple JSON parsing for services field
for /f "tokens=2 delims=:," %%a in ('findstr /c:"services" "%service_info%"') do (
    set "services_line=%%a"
)
set "SERVICES_TO_RUN=!services_line: =!"
set "SERVICES_TO_RUN=!SERVICES_TO_RUN:"=!"
echo Build configuration: !SERVICES_TO_RUN!
goto :eof

:show_service_menu
echo Select services to run:
echo 1) Use build configuration (!SERVICES_TO_RUN!)
echo 2) Minimal (Expense Manager only)
echo 3) Standard (Expense Manager + Bella Chat)
echo 4) Enhanced (Expense Manager + Bella Chat + Observability)
echo 5) Custom selection
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" (
    REM Use build configuration
) else if "%choice%"=="2" (
    set "SERVICES_TO_RUN=minimal"
) else if "%choice%"=="3" (
    set "SERVICES_TO_RUN=standard"
) else if "%choice%"=="4" (
    set "SERVICES_TO_RUN=enhanced"
) else if "%choice%"=="5" (
    call :select_custom_services
) else (
    echo Invalid choice. Using: !SERVICES_TO_RUN!
)
goto :eof

:select_custom_services
echo.
echo Custom Service Selection:
echo.

set /p include_bella="Include Bella Chat service? (y/N): "
if /i "%include_bella%"=="y" (
    set "bella_chat=true"
) else (
    set "bella_chat=false"
)

set /p include_ems="Include Expense Manager service? (Y/n): "
if /i "%include_ems%"=="n" (
    set "expense_manager=false"
) else (
    set "expense_manager=true"
)

REM Bella Chat Observability (only if Bella Chat is enabled)
if /i "%bella_chat%"=="true" (
    set /p include_obs="Include Bella Chat Observability (Phoenix, Arize)? (y/N): "
    if /i "%include_obs%"=="y" (
        set "bella_chat_observability=true"
    ) else (
        set "bella_chat_observability=false"
    )
) else (
    set "bella_chat_observability=false"
)

REM Determine service profile
if /i "%bella_chat_observability%"=="true" (
    set "SERVICES_TO_RUN=enhanced"
) else if /i "%bella_chat%"=="true" and /i "%expense_manager%"=="true" (
    set "SERVICES_TO_RUN=standard"
) else if /i "%expense_manager%"=="true" (
    set "SERVICES_TO_RUN=minimal"
) else (
    echo At least Expense Manager must be selected
    call :select_custom_services
)
goto :eof

:pull_services
echo * Pulling services from GitHub Container Registry...

REM Always pull expense manager
echo Pulling expense-manager-service...
docker pull "%REGISTRY%/%REPO_OWNER%/expense-manager-service:latest"
if %errorlevel% neq 0 (
    echo WARNING: Could not pull expense-manager-service, will build locally
)

REM Pull bella chat if needed
set "should_pull_bella=false"
if "%SERVICES_TO_RUN%"=="standard" set "should_pull_bella=true"
if "%SERVICES_TO_RUN%"=="enhanced" set "should_pull_bella=true"

if "%should_pull_bella%"=="true" (
    echo Pulling bella-chat-service...
    docker pull "%REGISTRY%/%REPO_OWNER%/bella-chat-service:latest"
    if %errorlevel% neq 0 (
        echo WARNING: Could not pull bella-chat-service, will build locally
    )
    
    echo Pulling qdrant...
    docker pull qdrant/qdrant:latest
    if %errorlevel% neq 0 (
        echo WARNING: Could not pull qdrant
    )
)

REM Pull observability services if enhanced profile
if "%SERVICES_TO_RUN%"=="enhanced" (
    echo Pulling phoenix...
    docker pull arizephoenix/phoenix:latest
    if %errorlevel% neq 0 (
        echo WARNING: Could not pull phoenix
    )
)

echo SUCCESS: Service pull completed
goto :eof

:setup_environment
echo * Setting up environment...

REM Create .env file if it doesn't exist
if not exist "%ENV_FILE%" (
    echo Creating .env file from template...
    copy "%DOCKER_DIR%\.env.example" "%ENV_FILE%" >nul
    echo WARNING: Please review and update %ENV_FILE% with your configuration
)

echo Environment setup completed
goto :eof

:start_services
echo * Starting backend services...

cd /d "%DOCKER_DIR%"

REM Stop any existing services
echo Stopping existing services...
docker compose down 2>nul

REM Start services based on profile
if "%SERVICES_TO_RUN%"=="minimal" (
    echo Starting minimal services ^(Expense Manager only^)...
    docker compose -f docker-compose.prod.yaml up -d expense-manager-service
) else if "%SERVICES_TO_RUN%"=="standard" (
    echo Starting standard services ^(Expense Manager + Bella Chat^)...
    docker compose -f docker-compose.prod.yaml --profile bella up -d
) else if "%SERVICES_TO_RUN%"=="enhanced" (
    echo Starting enhanced services ^(Expense Manager + Bella Chat + Observability^)...
    docker compose -f docker-compose.prod.yaml --profile bella --profile full up -d
) else (
    echo ERROR: Unknown service profile: %SERVICES_TO_RUN%
    pause
    exit /b 1
)

REM Wait for services to be ready
echo * Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check service health
call :check_service_health
goto :eof

:check_service_health
echo * Checking service health...

set "healthy=true"

REM Check expense manager
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo SUCCESS: Expense Manager Service is healthy
) else (
    echo ERROR: Expense Manager Service is not responding
    set "healthy=false"
)

REM Check bella chat if enabled
if "%SERVICES_TO_RUN%"=="standard" or "%SERVICES_TO_RUN%"=="enhanced" (
    curl -s http://localhost:5000/health >nul 2>&1
    if %errorlevel% equ 0 (
        echo SUCCESS: Bella Chat Service is healthy
    ) else (
        echo ERROR: Bella Chat Service is not responding
        set "healthy=false"
    )
)

if "%healthy%"=="false" (
    echo WARNING: Some services are not healthy. The app may not work properly.
    echo Check docker logs for more information: docker compose logs
)
goto :eof

:launch_electron_app
echo * Launching Electron app...

REM Check if the app is built
if not exist "%BUILD_DIR%\win-unpacked\Bella Keys.exe" (
    echo ERROR: Packaged Electron app not found in build directory.
    echo Please run scripts\build-electron.bat first to build for production.
    pause
    exit /b 1
)

REM Launch the app
echo Starting Bella Keys desktop app...
start "" "%BUILD_DIR%\win-unpacked\Bella Keys.exe"
goto :eof

:cleanup
echo * Cleaning up...
cd /d "%DOCKER_DIR%"
docker compose down
echo SUCCESS: Services stopped
goto :eof

REM Main execution
:main
echo Starting Bella Keys desktop app...
echo.

REM Check prerequisites
call :check_docker
echo.

REM Check build configuration
call :check_build_info
echo.

REM Show service selection menu
call :show_service_menu
echo.

REM Pull services
call :pull_services
echo.

REM Setup environment
call :setup_environment
echo.

REM Start services
call :start_services
echo.

REM Launch app
call :launch_electron_app

goto :eof

REM Run main function
call :main

echo.
echo Press any key to exit...
pause >nul