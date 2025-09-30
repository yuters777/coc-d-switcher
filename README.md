# COC-D Switcher

Convert Elbit/Company COCs into Dutch MoD Certificate of Conformity format.

## Quick Start

Using Docker:
```bash
docker-compose up --build
```

Local Development:
```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Access Points
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs