# COC-D Switcher

Convert Elbit/Company COCs into Dutch MoD Certificate of Conformity format.

## Quick Start

Using Docker:
```bash
docker-compose up --build
```

Local Development:

### Windows (PowerShell)

**Option 1: Using startup scripts (recommended)**

1. Open **two PowerShell terminals** in the project root directory
2. In the **first terminal** (Backend):
   ```powershell
   .\start-backend.ps1
   ```
3. In the **second terminal** (Frontend):
   ```powershell
   .\start-frontend.ps1
   ```

**Note:** If you get an execution policy error, run this command first:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Option 2: Manual setup**
```powershell
# Backend (Terminal 1)
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (Terminal 2)
cd frontend
npm install
npm run dev
```

### Linux/Mac (Bash)

**Option 1: Using startup scripts (recommended)**
```bash
# Backend (in one terminal)
./start-backend.sh

# Frontend (in another terminal)
./start-frontend.sh
```

**Option 2: Manual setup**
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Access Points
The services are configured to listen on all network interfaces (0.0.0.0):
- Frontend: http://localhost:5173 or http://[your-ip]:5173
- Backend API: http://localhost:8000 or http://[your-ip]:8000
- API Docs: http://localhost:8000/docs or http://[your-ip]:8000/docs

Replace `[your-ip]` with your machine's IP address (e.g., 21.0.0.26)