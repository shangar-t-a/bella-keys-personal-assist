# scripts/database/backup-db.ps1
# PowerShell script to backup the native PostgreSQL database

$RepoRoot = Split-Path -Path $PSScriptRoot -Parent
$EnvFile = Join-Path -Path $RepoRoot -ChildPath "docker\.env"
$BackupDir = Join-Path -Path $RepoRoot -ChildPath "backups"

# Defaults
$PgHost = "localhost"
$PgPort = "5432"
$PgUser = "postgres"
$PgDbName = "expense_manager"
$PgPass = ""

# Load configurations from .env if it exists
if (Test-Path $EnvFile) {
    Write-Host "Reading database configuration from $EnvFile..." -ForegroundColor Cyan
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^([^#\s][^=]*)=(.*)$') {
            $name = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            # Remove optional quotes
            if ($value -match '^"(.*)"$') { $value = $Matches[1] }
            elseif ($value -match "^'(.*)'$") { $value = $Matches[1] }
            
            switch ($name) {
                "EMS_PG_DB_USER" { $PgUser = $value }
                "EMS_PG_DB_NAME" { $PgDbName = $value }
            }
        }
    }
}

# Prompt user for confirmation/override
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  PostgreSQL Database Backup Utility" -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "Host:     $PgHost"
Write-Host "Port:     $PgPort"
Write-Host "Database: $PgDbName"
Write-Host "User:     $PgUser"
Write-Host "=============================================" -ForegroundColor Cyan

$Confirm = Read-Host "Proceed with backup? (Y/n)"
if ($Confirm -eq "n" -or $Confirm -eq "N") {
    Write-Host "Backup cancelled." -ForegroundColor Yellow
    exit
}

# Prompt for password
$PgPass = Read-Host -Prompt "Enter PostgreSQL password for user '$PgUser' (input hidden or blank if no password)"
# Set PGPASSWORD environment variable for pg_dump
if ($PgPass) {
    $env:PGPASSWORD = $PgPass
}

if (!(Test-Path $BackupDir)) {
    New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$BackupFile = Join-Path -Path $BackupDir -ChildPath "backup_${PgDbName}_${Timestamp}.sql"

Write-Host "Backing up database '$PgDbName' to $BackupFile..." -ForegroundColor Green

try {
    & pg_dump -h $PgHost -p $PgPort -U $PgUser -F c -b -v -f $BackupFile $PgDbName 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Backup completed successfully!" -ForegroundColor Green
        Write-Host "Backup File: $BackupFile" -ForegroundColor Cyan
    } else {
        # Fallback to plain text SQL if custom format fails
        Write-Host "Attempting plain text format backup..." -ForegroundColor Yellow
        & pg_dump -h $PgHost -p $PgPort -U $PgUser -f $BackupFile $PgDbName
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Backup completed successfully (SQL text format)!" -ForegroundColor Green
            Write-Host "Backup File: $BackupFile" -ForegroundColor Cyan
        } else {
            Write-Host "❌ pg_dump failed with exit code $LASTEXITCODE. Please check if pg_dump is installed and in your PATH." -ForegroundColor Red
        }
    }
}
catch {
    Write-Host "❌ Failed to execute pg_dump. Make sure pg_dump is installed and added to the environment PATH." -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
}
finally {
    # Clear the password from environment variables
    if ($PgPass) {
        Remove-Item Env:\PGPASSWORD
    }
}
