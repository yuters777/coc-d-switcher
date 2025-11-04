# Start the frontend development server on all network interfaces
# Usage: Run this script in PowerShell from the project root directory

Write-Host "Starting COC-D Switcher Frontend..." -ForegroundColor Green

# Navigate to frontend directory
Set-Location "$PSScriptRoot\frontend"

# Install dependencies if needed
if (-not (Test-Path "node_modules")) {
    Write-Host "Installing dependencies..." -ForegroundColor Yellow
    npm install
}

# Start the dev server (Vite will use config from vite.config.ts with host: 0.0.0.0)
Write-Host "Starting frontend dev server on 0.0.0.0:5173..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
npm run dev
