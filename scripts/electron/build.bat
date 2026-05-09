@echo off
REM Build Electron app with optional service selection (Windows)
REM Run from repo root: scripts\build-electron.bat

setlocal enabledelayedexpansion

REM Script configuration
set "REPO_ROOT=%~dp0..\.."
set "UI_DIR=%REPO_ROOT%\keys-personal-assist-ui"
set "BUILD_DIR=%REPO_ROOT%\build"

echo.
echo ==================================
echo * Bella Keys Electron Build Script *
echo ==================================
echo.

REM Create build directory
if not exist "%BUILD_DIR%" mkdir "%BUILD_DIR%"

REM Service selection functions
:show_service_menu
echo Select services to include in the build:
echo 1) Minimal (Expense Manager only) - Lightweight
echo 2) Standard (Expense Manager + Bella Chat) - Recommended
echo 3) Enhanced (Expense Manager + Bella Chat + Observability) - Heavy resources
echo 4) Custom - Choose individual services
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" (
    set "SERVICES=minimal"
    set "VITE_BELLA_CHAT_ENABLED=false"
    set "VITE_EXPENSE_MANAGER_ENABLED=true"
    set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false"
    goto :continue
) else if "%choice%"=="2" (
    set "SERVICES=standard"
    set "VITE_BELLA_CHAT_ENABLED=true"
    set "VITE_EXPENSE_MANAGER_ENABLED=true"
    set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false"
    goto :continue
) else if "%choice%"=="3" (
    set "SERVICES=enhanced"
    set "VITE_BELLA_CHAT_ENABLED=true"
    set "VITE_EXPENSE_MANAGER_ENABLED=true"
    set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=true"
    goto :continue
) else if "%choice%"=="4" (
    set "SERVICES=custom"
    call :select_custom_services
    goto :continue
) else (
    echo Invalid choice. Using standard configuration.
    set "SERVICES=standard"
    set "VITE_BELLA_CHAT_ENABLED=true"
    set "VITE_EXPENSE_MANAGER_ENABLED=true"
    set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false"
    goto :continue
)

:select_custom_services
echo.
echo Custom Service Selection:
echo.

set /p include_bella="Include Bella Chat service? (y/N): "
if /i "%include_bella%"=="y" set "VITE_BELLA_CHAT_ENABLED=true" else set "VITE_BELLA_CHAT_ENABLED=false"

set /p include_ems="Include Expense Manager service? (Y/n): "
if /i "%include_ems%"=="n" (
    set "VITE_EXPENSE_MANAGER_ENABLED=false"
) else (
    set "VITE_EXPENSE_MANAGER_ENABLED=true"
)

REM Bella Chat Observability (only if Bella Chat is enabled)
if /i "%VITE_BELLA_CHAT_ENABLED%"=="true" (
    set /p include_obs="Include Bella Chat Observability (Phoenix, Arize)? (y/N): "
    if /i "%include_obs%"=="y" set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=true" else set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false"
) else (
    set "VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=false"
)
goto :eof

:continue
echo.
echo * Configuring build environment...

REM Create .env.production file
(
echo # Production build configuration
echo VITE_APP_ENV=electron
echo VITE_BELLA_CHAT_ENABLED=%VITE_BELLA_CHAT_ENABLED%
echo VITE_EXPENSE_MANAGER_ENABLED=%VITE_EXPENSE_MANAGER_ENABLED%
echo VITE_BELLA_CHAT_OBSERVABILITY_ENABLED=%VITE_BELLA_CHAT_OBSERVABILITY_ENABLED%
echo VITE_BUILD_TIMESTAMP=%date% %time%
echo VITE_BUILD_SERVICES=%SERVICES%
) > "%UI_DIR%\.env.production"

echo Environment configured for: %SERVICES%
echo Bella Chat: %VITE_BELLA_CHAT_ENABLED%
echo Expense Manager: %VITE_EXPENSE_MANAGER_ENABLED%
echo Bella Chat Observability: %VITE_BELLA_CHAT_OBSERVABILITY_ENABLED%
echo.

REM Build UI
echo * Building UI components...

cd /d "%UI_DIR%"

REM Install dependencies if needed
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
    if %errorlevel% neq 0 (
        echo ERROR: npm install failed
        exit /b 1
    )
)

REM Clean previous build artifacts
echo Cleaning previous build artifacts...
if exist "out" rmdir /s /q "out" >nul 2>&1
if exist "dist" rmdir /s /q "dist" >nul 2>&1
if exist "release" rmdir /s /q "release" >nul 2>&1

REM Build for production
echo Building Electron app...
call npm run build:electron

if %errorlevel% neq 0 (
    echo ERROR: Electron build failed
    exit /b 1
)

REM Verify Electron build output
if not exist "out\main\index.js" (
    echo ERROR: Electron main entry file not found after build
    exit /b 1
)

if not exist "out\preload\index.mjs" (
    echo ERROR: Electron preload file not found after build
    exit /b 1
)

if not exist "out\renderer\index.html" (
    echo ERROR: Electron renderer build not found
    exit /b 1
)

echo SUCCESS: Electron build completed successfully
echo.

REM Package app
echo * Packaging Electron app...

REM Set environment variables to disable code signing
set CSC_LINK=
set CSC_KEY_PASSWORD=
set CSC_IDENTITY_AUTO_DISCOVERY=false

REM Cache clearing removed to prevent winCodeSign re-download issues

call npm run dist

if %errorlevel% neq 0 (
    echo ERROR: App packaging failed
    exit /b 1
)

REM Verify packaged app
if not exist "release\win-unpacked\resources\app.asar" (
    echo ERROR: Packaged app.asar not found
    exit /b 1
)

echo SUCCESS: App packaged successfully

REM Move artifacts to build directory
if exist "release" (
    echo Moving production artifacts to build directory...
    REM Copy only the installer and portable version
    xcopy /Y "release\*.exe" "%BUILD_DIR%\" >nul 2>&1
    REM Copy the unpacked folder for run script usage
    if exist "release\win-unpacked" (
        if exist "%BUILD_DIR%\win-unpacked" rmdir /s /q "%BUILD_DIR%\win-unpacked"
        xcopy /E /I /Y "release\win-unpacked\*" "%BUILD_DIR%\win-unpacked\" >nul 2>&1
    )
)

echo.
echo * Creating service information...

REM Create service info file
(
echo {
echo   "buildTimestamp": "%date% %time%",
echo   "services": "%SERVICES%",
echo   "features": {
echo     "bellaChat": %VITE_BELLA_CHAT_ENABLED%,
echo     "expenseManager": %VITE_EXPENSE_MANAGER_ENABLED%,
echo     "bellaChatObservability": %VITE_BELLA_CHAT_OBSERVABILITY_ENABLED%
echo   },
echo   "requirements": {
echo     "docker": true,
echo     "ports": {
if "%VITE_EXPENSE_MANAGER_ENABLED%"=="true" (
echo       "expenseManager": "8000",
) else (
echo       "expenseManager": null,
)
if "%VITE_BELLA_CHAT_ENABLED%"=="true" (
echo       "bellaChat": "5000",
) else (
echo       "bellaChat": null,
)
if "%VITE_BELLA_CHAT_ENABLED%"=="true" (
echo       "qdrant": "6333",
) else (
echo       "qdrant": null,
)
if "%VITE_EXPENSE_MANAGER_ENABLED%"=="true" (
echo       "postgres": "5432",
) else (
echo       "postgres": null,
)
if "%VITE_BELLA_CHAT_ENABLED%"=="true" if "%VITE_BELLA_CHAT_OBSERVABILITY_ENABLED%"=="true" (
echo       "phoenix": "6006",
echo       "arizeGrpc": "4317",
) else (
echo       "phoenix": null,
echo       "arizeGrpc": null,
)
echo       "build": "stable"
echo     }
echo   }
echo }
) > "%BUILD_DIR%\service-info.json"

echo.
echo * Build completed successfully! *
echo Build artifacts located in: %BUILD_DIR%
echo.
echo Next steps:
echo 1. Run the app with: scripts\services\run-services-installed-app.bat
echo 2. Check service-info.json for required services
echo.

echo Press any key to exit...
pause >nul
