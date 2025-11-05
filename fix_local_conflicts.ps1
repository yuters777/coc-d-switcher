# PowerShell script to fix local merge conflicts
# This will reset the main.py file to the correct version from the repository

Write-Host "Fixing local merge conflicts..." -ForegroundColor Yellow

# Stop any running backend servers
Write-Host "If the server is running, please press CTRL+C to stop it first" -ForegroundColor Red
Read-Host "Press Enter when ready to continue"

# Navigate to project root
Set-Location C:\Projects\coc-d-switcher

# Show current status
Write-Host "`nCurrent git status:" -ForegroundColor Cyan
git status

# Discard local changes to main.py and restore from repository
Write-Host "`nResetting backend/app/main.py to repository version..." -ForegroundColor Yellow
git checkout HEAD -- backend/app/main.py

# Verify the fix
Write-Host "`nVerifying the file is clean..." -ForegroundColor Cyan
git status

Write-Host "`nDone! The file has been restored to the clean version." -ForegroundColor Green
Write-Host "Now you can restart the backend server:" -ForegroundColor Cyan
Write-Host "  cd backend" -ForegroundColor White
Write-Host "  .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor White
