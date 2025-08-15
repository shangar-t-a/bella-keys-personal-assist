@echo off

set CURRENT_DIR=%cd%

echo Launching the application...

echo Starting Personal Assistant Service...

cd /d "%CURRENT_DIR%"
cd "expense-manager-service"
start "Expense Manager Service" cmd /k "uv run python app\main.py"

echo Service started successfully...

echo Launching Personal Assistant UI...

cd /d "%CURRENT_DIR%"
cd "keys-personal-assist-ui"
start "Personal Assistant UI" cmd /k "npm run dev"

echo UI launched successfully...
