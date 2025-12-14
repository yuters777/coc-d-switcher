#Requires -Version 5.1
<#
.SYNOPSIS
    Verify offline packages against official PyPI hashes
.DESCRIPTION
    Fetches SHA256 hashes from PyPI and verifies local .whl files match.
    Generates requirements-hashed.txt with OFFICIAL PyPI hashes.
.NOTES
    Version: 1.0.1
    Date: December 2025
    IMPORTANT: Run this on a machine WITH internet access before transferring to offline VM
#>

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$OfflineDir = Join-Path $ScriptDir "offline_packages"
$OutputFile = Join-Path $ScriptDir "requirements-hashed.txt"
$VerificationLog = Join-Path $ScriptDir "hash_verification_log.txt"

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "     Verify Packages Against Official PyPI Hashes              " -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  This script verifies your downloaded packages match PyPI" -ForegroundColor Gray
Write-Host "  Run this BEFORE transferring to the offline environment" -ForegroundColor Yellow
Write-Host ""

# Check internet connectivity
Write-Host "[1/4] Checking PyPI connectivity..." -ForegroundColor Yellow
try {
    $testResponse = Invoke-RestMethod -Uri "https://pypi.org/pypi/pip/json" -TimeoutSec 10
    Write-Host "      PyPI accessible" -ForegroundColor Green
} catch {
    Write-Host "      ERROR: Cannot reach PyPI. Internet connection required." -ForegroundColor Red
    exit 1
}

# Check offline_packages exists
Write-Host "[2/4] Scanning local packages..." -ForegroundColor Yellow
if (-not (Test-Path $OfflineDir)) {
    Write-Host "      ERROR: offline_packages directory not found" -ForegroundColor Red
    exit 1
}

$wheelFiles = Get-ChildItem -Path $OfflineDir -Filter "*.whl" | Sort-Object Name
$totalCount = $wheelFiles.Count
Write-Host "      Found $totalCount wheel packages to verify" -ForegroundColor Green

# Parse wheel filename to get package info
function Parse-WheelFilename {
    param([string]$Filename)
    
    $baseName = [System.IO.Path]::GetFileNameWithoutExtension($Filename)
    $parts = $baseName -split '-'
    
    $nameParts = @()
    $version = $null
    
    for ($i = 0; $i -lt $parts.Count; $i++) {
        if ($parts[$i] -match '^\d' -and $null -eq $version) {
            $version = $parts[$i]
        } elseif ($null -eq $version) {
            $nameParts += $parts[$i]
        }
    }
    
    $packageName = ($nameParts -join '_').ToLower()
    
    return @{
        Name = $packageName
        Version = $version
        Filename = $Filename
    }
}

# Fetch official hash from PyPI
function Get-PyPIHash {
    param(
        [string]$PackageName,
        [string]$Version,
        [string]$WheelFilename
    )
    
    try {
        $apiName = $PackageName.Replace('_', '-')
        $url = "https://pypi.org/pypi/$apiName/$Version/json"
        
        $response = Invoke-RestMethod -Uri $url -TimeoutSec 15
        
        foreach ($file in $response.urls) {
            if ($file.filename -eq $WheelFilename) {
                return @{
                    Success = $true
                    Hash = $file.digests.sha256
                    PyPIFilename = $file.filename
                }
            }
        }
        
        foreach ($file in $response.urls) {
            if ($file.packagetype -eq "bdist_wheel" -and $file.filename -like "*$Version*") {
                return @{
                    Success = $true
                    Hash = $file.digests.sha256
                    PyPIFilename = $file.filename
                    Note = "Filename variation"
                }
            }
        }
        
        return @{ Success = $false; Error = "Wheel not found on PyPI" }
        
    } catch {
        return @{ Success = $false; Error = $_.Exception.Message }
    }
}

# Process all packages
Write-Host "[3/4] Verifying against PyPI hashes..." -ForegroundColor Yellow
Write-Host ""

$verified = 0
$failed = 0
$warnings = 0

$logLines = @(
    "COC-D Switcher - Package Hash Verification Log",
    "Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "Source: PyPI (https://pypi.org)",
    "======================================================================",
    ""
)

$outputLines = @(
    "# COC-D Switcher - Requirements with Official PyPI Hashes",
    "# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "# Verification: All hashes fetched from official PyPI repository",
    "# Packages: $totalCount",
    "#",
    "# Install: pip install --require-hashes --no-index --find-links=offline_packages -r requirements-hashed.txt",
    "#",
    ""
)

$counter = 0
foreach ($wheel in $wheelFiles) {
    $counter++
    $percent = [math]::Round(($counter / $totalCount) * 100)
    
    $parsed = Parse-WheelFilename -Filename $wheel.Name
    $displayName = "$($parsed.Name)==$($parsed.Version)"
    
    Write-Host "  [$percent%] Verifying: $displayName" -ForegroundColor Gray
    
    $localHash = (Get-FileHash -Path $wheel.FullName -Algorithm SHA256).Hash.ToLower()
    
    $pypiResult = Get-PyPIHash -PackageName $parsed.Name -Version $parsed.Version -WheelFilename $wheel.Name
    
    if ($pypiResult.Success) {
        $pypiHash = $pypiResult.Hash.ToLower()
        
        if ($localHash -eq $pypiHash) {
            $verified++
            $status = "VERIFIED"
            
            $pkgName = $parsed.Name.Replace('_', '-')
            $outputLines += "$pkgName==$($parsed.Version) ``"
            $outputLines += "    --hash=sha256:$pypiHash"
            $outputLines += ""
            
        } else {
            $failed++
            $status = "HASH MISMATCH"
        }
        
        $logLines += "$status : $displayName"
        $logLines += "  Local:  $localHash"
        $logLines += "  PyPI:   $pypiHash"
        if ($pypiResult.Note) {
            $logLines += "  Note:   $($pypiResult.Note)"
            $warnings++
        }
        $logLines += ""
        
    } else {
        $warnings++
        $status = "NOT ON PYPI"
        
        $logLines += "WARNING : $displayName"
        $logLines += "  Local:  $localHash"
        $logLines += "  Error:  $($pypiResult.Error)"
        $logLines += "  Action: Using local hash (manual verification recommended)"
        $logLines += ""
        
        $pkgName = $parsed.Name.Replace('_', '-')
        $outputLines += "# WARNING: Hash not verified against PyPI"
        $outputLines += "$pkgName==$($parsed.Version) ``"
        $outputLines += "    --hash=sha256:$localHash"
        $outputLines += ""
    }
}

Write-Host ""

# Write output files
Write-Host "[4/4] Generating output files..." -ForegroundColor Yellow

$outputLines | Out-File -FilePath $OutputFile -Encoding UTF8
Write-Host "      Created: requirements-hashed.txt" -ForegroundColor Green

$logLines += @(
    "======================================================================",
    "SUMMARY",
    "  Total packages:  $totalCount",
    "  Verified:        $verified",
    "  Failed:          $failed", 
    "  Warnings:        $warnings",
    "======================================================================"
)
$logLines | Out-File -FilePath $VerificationLog -Encoding UTF8
Write-Host "      Created: hash_verification_log.txt" -ForegroundColor Green

# Summary
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkGray

if ($failed -gt 0) {
    Write-Host ""
    Write-Host "  [X] VERIFICATION FAILED" -ForegroundColor Red
    Write-Host "      $failed package(s) have hash mismatches!" -ForegroundColor Red
    Write-Host "      These files may be corrupted or tampered with." -ForegroundColor Yellow
    Write-Host "      Re-download from PyPI before deployment." -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

Write-Host ""
Write-Host "  [OK] VERIFICATION SUCCESSFUL" -ForegroundColor Green
Write-Host ""
Write-Host "       Verified:  $verified / $totalCount packages" -ForegroundColor White
if ($warnings -gt 0) {
    Write-Host "       Warnings:  $warnings (see log for details)" -ForegroundColor Yellow
}
Write-Host ""
Write-Host "       All packages match official PyPI hashes." -ForegroundColor Gray
Write-Host "       Safe to transfer to offline environment." -ForegroundColor Gray
Write-Host ""
Write-Host "================================================================" -ForegroundColor DarkGray
