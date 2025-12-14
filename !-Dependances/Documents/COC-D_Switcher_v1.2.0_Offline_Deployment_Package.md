# COC-D Switcher v1.2.0 - Offline Deployment Package

## Overview

This package contains the COC-D Switcher application configured for offline (air-gapped) deployment. All dependencies are included for installation without internet access, with cryptographic hash verification against official package repositories.

## Prerequisites

Before installation, ensure the target system has:

- **Python 3.10+** (https://python.org)
- **Node.js 18+** (https://nodejs.org)
- **Windows 10/11** or Windows Server 2019+

## Quick Start

1. Extract this package to `C:\Apps\COC-D-Switcher`
2. Open PowerShell as Administrator
3. Run: `.\install.ps1`
4. After installation completes, run: `.\start_app.ps1`

## Installation Scripts

| Script | Description |
|--------|-------------|
| `install.ps1` | Complete installation (runs all steps) |
| `install_backend.ps1` | Install Python backend only |
| `install_frontend.ps1` | Install Node.js frontend only |
| `verify_installation.ps1` | Check installation status |
| `start_app.ps1` | Launch both servers + open browser |
| `start_backend.ps1` | Start API server only |
| `start_frontend.ps1` | Start frontend only |

## Manual Installation

### Backend (Standard)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --no-index --find-links=offline_packages -r requirements-secure.txt
```

### Backend (With Hash Verification - Recommended)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --require-hashes --no-index --find-links=offline_packages -r requirements-hashed.txt
```

The `--require-hashes` flag ensures all packages match their official PyPI SHA256 hashes, detecting any tampering or corruption during transfer.

### Frontend

```powershell
cd frontend
xcopy /E /I ..\backend\offline_packages\node_modules_backup node_modules
npm run build  # Optional: pre-build production assets
```

## Access Points

| Service | URL |
|---------|-----|
| Application | http://localhost:5173 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## Package Contents

```
COC-D-Offline-v1.2.0/
├── backend/
│   ├── app/                       # FastAPI application
│   ├── templates/                 # DOCX templates
│   ├── offline_packages/          # Python wheel files (59 packages)
│   │   └── node_modules_backup/   # Node.js packages (188 packages)
│   ├── requirements.txt           # Core dependencies
│   ├── requirements-secure.txt    # All dependencies with pinned versions
│   ├── requirements-hashed.txt    # Dependencies with PyPI SHA256 hashes
│   ├── hash_verification_log.txt  # Audit trail of hash verification
│   └── verify_pypi_hashes.ps1     # Script to re-verify against PyPI
├── frontend/
│   ├── src/                       # React source code
│   ├── package.json
│   ├── package-lock.json          # npm dependencies with SHA512 integrity
│   └── vite.config.ts
├── install.ps1
├── install_backend.ps1
├── install_frontend.ps1
├── start_app.ps1
├── start_backend.ps1
├── start_frontend.ps1
├── verify_installation.ps1
└── README.md
```

## Security Features

### Supply Chain Verification

| Layer | Control | Status |
|-------|---------|--------|
| 1 | Official Source (PyPI/npm) | ✓ Verified |
| 2 | Exact Version Pinning | ✓ requirements-secure.txt |
| 3 | SHA256 Hash Verification | ✓ requirements-hashed.txt |
| 4 | Vulnerability Scanning | ✓ pip-audit completed |

### Package Verification Results

- **Python packages:** 59/59 verified against official PyPI hashes
- **Node.js packages:** 188 packages with SHA512 integrity via package-lock.json
- **Vulnerabilities:** 6 remediated, 1 accepted (see Security Report)
- **Final Risk Rating:** LOW

### Re-Verification (Requires Internet)

To re-verify packages against PyPI before deployment:

```powershell
cd backend
.\verify_pypi_hashes.ps1
```

## Security Notes

- All Python packages verified against official PyPI SHA256 hashes (December 14, 2025)
- All Node.js packages include SHA512 integrity hashes in package-lock.json
- 6 vulnerabilities remediated via package upgrades
- 1 accepted risk documented (pdfminer.six pickle deserialization - mitigated by air-gapped environment)
- Application binds to localhost only - no external network access
- See `COC-D_Secure_Python_Package_Sources_Report.docx` for full security documentation

## Troubleshooting

### "Python not found"
Ensure Python is installed and added to PATH. Run `python --version` to verify.

### "Node.js not found"
Ensure Node.js is installed and added to PATH. Run `node --version` to verify.

### "Package installation failed"
Check that `offline_packages` directory contains .whl files and wasn't corrupted during transfer.

### "Hash mismatch" error during installation
Package files may be corrupted. Re-transfer from source and verify with `verify_pypi_hashes.ps1`.

### Backend won't start
- Ensure virtual environment is activated
- Check port 8000 is not in use: `netstat -ano | findstr :8000`

### Frontend won't start
- Ensure node_modules was copied correctly
- Check port 5173 is not in use: `netstat -ano | findstr :5173`

## Related Documentation

- `COC-D_Secure_Python_Package_Sources_Report.docx` - Full security assessment
- `hash_verification_log.txt` - Package verification audit trail
- `requirements-hashed.txt` - Requirements with SHA256 hashes

## Support

For issues or questions, contact the development team.

---
Version: 1.2.0  
Date: December 2025  
Security Verification Date: December 14, 2025
