# Start the backend server on all network interfaces
# Usage: Run this script in PowerShell from the project root directory

Write-Host "Starting COC-D Switcher Backend..." -ForegroundColor Green

# Navigate to backend directory
Set-Location "$PSScriptRoot\backend"

# Check if virtual environment exists
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

# Install dependencies if needed
if (-not (Test-Path "venv\.deps_installed")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    New-Item -Path "venv\.deps_installed" -ItemType File -Force | Out-Null
}

# Start the server
Write-Host "Starting backend server on 0.0.0.0:8000..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
