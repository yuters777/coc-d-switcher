#!/usr/bin/env python3
"""
COC-D Switcher Complete Project Generator
This creates all necessary files for the application
"""

import os
import json
from pathlib import Path


def create_file(path, content):
    """Create a file with the given content"""
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"✓ Created {path}")


def create_project():
    """Create all project files"""

    print("🚀 Creating COC-D Switcher project...")
    print("=" * 50)

    files = {}

    # Backend core files
    files['backend/app/main.py'] = create_main_py()
    files['backend/app/schemas.py'] = create_schemas_py()
    files['backend/app/extract.py'] = create_extract_py()
    files['backend/app/validate.py'] = create_validate_py()
    files['backend/app/render.py'] = create_render_py()
    files['backend/app/config.py'] = create_config_py()
    files['backend/app/__init__.py'] = ''
    files['backend/tests/__init__.py'] = ''
    files['backend/requirements.txt'] = create_requirements()
    files['backend/Dockerfile'] = create_backend_dockerfile()

    # Frontend core files
    files['frontend/src/App.tsx'] = create_app_tsx()
    files['frontend/src/main.tsx'] = create_main_tsx()
    files['frontend/src/index.css'] = create_index_css()
    files['frontend/package.json'] = create_package_json()
    files['frontend/index.html'] = create_index_html()
    files['frontend/vite.config.ts'] = create_vite_config()
    files['frontend/tsconfig.json'] = create_tsconfig()
    files['frontend/Dockerfile'] = create_frontend_dockerfile()
    files['frontend/nginx.conf'] = create_nginx_conf()
    files['frontend/tailwind.config.cjs'] = create_tailwind_config()
    files['frontend/postcss.config.cjs'] = create_postcss_config()

    # Sample data
    files['backend/app/fixtures/sample_data.json'] = create_sample_data()

    # Config files
    files['.gitignore'] = create_gitignore()
    files['docker-compose.yml'] = create_docker_compose()
    files['README.md'] = create_readme()

    # Create all files
    for path, content in files.items():
        create_file(path, content)

    print("=" * 50)
    print("✅ Project created successfully!")
    print("\nNext steps:")
    print("1. Place DOCX template in backend/templates/")
    print("2. Run: git init")
    print("3. Run: git add .")
    print("4. Run: git commit -m 'Initial project setup'")
    print("5. Run: git remote add origin https://github.com/yulers777/coc-d-switcher.git")
    print("6. Run: git push -u origin main")


def create_main_py():
    return '''import os
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import json
from datetime import datetime
from pathlib import Path

from .schemas import JobData, ValidationResult, ConversionOutput
from .extract import extract_from_pdfs
from .validate import validate_conversion
from .render import render_docx, convert_to_pdf
from .config import load_config

app = FastAPI(title="COC-D Switcher API")

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs_db: Dict[str, Dict[str, Any]] = {}
UPLOAD_DIR = Path("/tmp/coc-uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class JobCreate(BaseModel):
    name: str
    submitted_by: str

@app.get("/")
async def root():
    return {"message": "COC-D Switcher API", "docs": "/docs"}

@app.post("/api/jobs")
async def create_job(job: JobCreate):
    job_id = str(uuid.uuid4())
    jobs_db[job_id] = {
        "id": job_id,
        "name": job.name,
        "submitted_by": job.submitted_by,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "files": {},
        "extracted_data": None,
        "validation": None,
        "rendered_files": {}
    }
    return {"job_id": job_id}

@app.get("/api/jobs")
async def list_jobs():
    return list(jobs_db.values())

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]
'''


def create_schemas_py():
    return '''from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class SupplierBlock(BaseModel):
    name: str
    address: str
    contact: str
    email: str

class AcquirerBlock(BaseModel):
    name: str
    address_lines: List[str]

class Item(BaseModel):
    contract_item: str
    product_description_or_part: str
    quantity: int
    shipment_document: str
    undelivered_quantity: Optional[int] = None

class ValidationIssue(BaseModel):
    code: str
    message: str
    where: str

class ValidationResult(BaseModel):
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]

class ConversionOutput(BaseModel):
    pass  # Full implementation would go here

class JobData(BaseModel):
    id: str
    name: str
    submitted_by: str
    status: str
    created_at: datetime
    updated_at: datetime
'''


def create_extract_py():
    return '''import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .config import load_config

def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """Extract data from PDFs"""
    config = load_config()

    result = {
        "extracted": {"from_packing_slip": {}, "from_company_coc": {}},
        "part_I": {},
        "part_II": {},
        "render_vars": {
            "docx_template": "COC_SV_Del165_20.03.2025.docx",
            "output_filename": "",
            "date_format": "DD/MMM/YYYY"
        },
        "validation": {"errors": [], "warnings": []}
    }

    # Implementation would extract from actual PDFs
    # For now, return sample structure
    return result

def normalize_date(date_str: str) -> str:
    """Normalize date to DD/MMM/YYYY format"""
    if not date_str:
        return ""
    # Implementation would handle various date formats
    return date_str
'''


def create_validate_py():
    return '''from typing import Dict, Any, List
import re
from datetime import datetime

def validate_conversion(data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Validate conversion data with enhanced rules"""

    errors = []
    warnings = []

    part_i = data.get("part_I", {})

    # Check serial count matches quantity
    serials = part_i.get("serials", [])
    items = part_i.get("items", [])

    if items and serials:
        quantity = items[0].get("quantity", 0)
        if len(serials) != quantity:
            errors.append({
                "code": "SERIAL_COUNT_MISMATCH",
                "message": f"Serial count ({len(serials)}) does not match quantity ({quantity})",
                "where": "part_I.serials"
            })

    # Check contract number present
    if not part_i.get("contract_number"):
        errors.append({
            "code": "MISSING_CONTRACT",
            "message": "Contract number is missing",
            "where": "part_I.contract_number"
        })

    return {"errors": errors, "warnings": warnings}
'''


def create_render_py():
    return '''from pathlib import Path
from typing import Dict, Any
import json
import os

TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "templates/COC_SV_Del165_20.03.2025.docx")

def render_docx(conv_json: Dict[str, Any], job_id: str) -> Path:
    """Render DOCX from conversion data"""
    out_path = Path(f"/tmp/coc-{job_id}.docx")

    # In production, use docxtpl with actual template
    # For now, create placeholder
    with open(out_path, 'w') as f:
        json.dump(conv_json, f, indent=2)

    return out_path

def convert_to_pdf(docx_path: Path) -> Path:
    """Convert DOCX to PDF"""
    pdf_path = docx_path.with_suffix(".pdf")

    # In production, use LibreOffice headless conversion
    # For now, create placeholder
    pdf_path.write_text(f"PDF version of {docx_path.name}")

    return pdf_path
'''


def create_config_py():
    return '''import json
from pathlib import Path

def load_config() -> dict:
    """Load configuration"""
    default_config = {
        "supplier_block": {
            "name": "Elbit Systems C4I and Cyber Ltd",
            "address": "2 Hamachshev, Netanya, Israel",
            "contact": "Ido Shilo",
            "email": "Ido.Shilo@elbitsystems.com"
        },
        "contract_mod_text": [
            "AMENDMENT 15-12-2020 VOSS additional order call off solution and deliveries 11-12-2020",
            "10-01-2022 Amendment to the Agreement TCP 187, TCP 192, TCP 193 DMO signed",
            "Approved TCP's list"
        ],
        "deviations_text": [
            "See remarks in Box 14.",
            "ELB_VOS_POR001",
            "ELB_VOS_CE0003",
            "ELB_VOS_SEC001",
            "ELB_VOS_CE0004"
        ],
        "gqar_defaults": {
            "name": "R. Kompier",
            "phone": "+31 620415178",
            "email": "R.Kompier@mindef.nl",
            "statement": ""
        },
        "signers": {
            "qa_manager": "Ronen Shamir, SmartVest QA Manager",
            "signature_mark": "QM.Elbit"
        },
        "delivery_id": "Del165",
        "output_filename_pattern": "COC_SV_{DeliveryID}_{DD.MM.YYYY}.docx"
    }

    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)

    return default_config
'''


def create_requirements():
    return '''fastapi==0.104.1
uvicorn==0.24.0
pydantic==2.5.0
pdfplumber==0.10.3
python-multipart==0.0.6
pytest==7.4.3
python-docx==0.8.11
docxtpl==0.16.7'''


def create_backend_dockerfile():
    return '''FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \\
    libreoffice \\
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app app/
COPY templates templates/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]'''


def create_app_tsx():
    return '''import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <nav className="bg-blue-600 text-white p-4">
          <div className="container mx-auto">
            <h1 className="text-2xl font-bold">COC-D Switcher</h1>
          </div>
        </nav>

        <div className="container mx-auto p-6">
          <h2 className="text-3xl font-bold mb-6">Dashboard</h2>
          <p>Application is ready for development</p>
        </div>
      </div>
    </Router>
  );
}

export default App;'''


def create_main_tsx():
    return '''import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);'''


def create_index_css():
    return '''@tailwind base;
@tailwind components;
@tailwind utilities;'''


def create_package_json():
    return '''{
  "name": "coc-d-switcher-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.18.0",
    "react-redux": "^8.1.3",
    "@reduxjs/toolkit": "^1.9.7"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@vitejs/plugin-react": "^4.1.0",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "tailwindcss": "^3.3.5",
    "typescript": "^5.2.2",
    "vite": "^4.5.0"
  }
}'''


def create_index_html():
    return '''<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>COC-D Switcher</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>'''


def create_vite_config():
    return '''import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
  },
});'''


def create_tsconfig():
    return '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}'''


def create_frontend_dockerfile():
    return '''FROM node:18-alpine as builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]'''


def create_nginx_conf():
    return '''server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;

  location / {
    try_files $uri /index.html;
  }

  location /api {
    proxy_pass http://backend:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
  }
}'''


def create_tailwind_config():
    return '''module.exports = {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {}
  },
  plugins: []
};'''


def create_postcss_config():
    return '''module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {}
  }
};'''


def create_sample_data():
    return '''{
  "extracted": {
    "from_packing_slip": {
      "sold_to": {"name": "NETHERLANDS MINISTRY OF DEFENCE"},
      "ship_to": {"name": "BCD"},
      "contract_number": "697.12.5011.01",
      "part_no": "20580903700",
      "description": "PNR-1000N WPTT",
      "customer_item": "20000646041",
      "quantity": 2,
      "shipment_document": "Packing Slip 6SH264587",
      "date": "20-03-2025",
      "serials": ["NL13721", "NL13722"]
    },
    "from_company_coc": {
      "customer": "NETHERLANDS MINISTRY OF DEFENCE",
      "shipment_no": "6SH264587",
      "order": "697.12.5011.01",
      "coc_no": "COC011285",
      "date": "20/Mar/2025",
      "serials": ["NL13721", "NL13722"],
      "qa_signer": "YESHAYA ORLY"
    }
  },
  "part_I": {
    "supplier_serial_no": "COC_SV_Del165_20.03.2025.docx",
    "contract_number": "697.12.5011.01",
    "applicable_to": "6SH264587",
    "items": [{
      "contract_item": "1",
      "product_description_or_part": "20580903700; PNR-1000N WPTT; Customer Item 20000646041",
      "quantity": 2,
      "shipment_document": "Packing Slip 6SH264587"
    }],
    "remarks": "SW Ver. # 2.2.15.45",
    "date": "20/Mar/2025",
    "serials": ["NL13721", "NL13722"]
  },
  "part_II": {
    "supplier_coc_serial_no": "COC_SV_Del165_20.03.2025.docx",
    "contract_number": "697.12.5011.01"
  },
  "render_vars": {
    "docx_template": "COC_SV_Del165_20.03.2025.docx",
    "output_filename": "COC_SV_Del165_20.03.2025.docx",
    "date_format": "DD/MMM/YYYY"
  },
  "validation": {"errors": [], "warnings": []}
}'''


def create_gitignore():
    return '''# Python
__pycache__/
*.py[cod]
.venv/
venv/
.pytest_cache/

# Node
node_modules/
dist/
.npm
*.log

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Project
/tmp/
*.pdf
*.docx
!templates/*.docx

# Environment
.env'''


def create_docker_compose():
    return '''version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend/app:/app/app
      - ./backend/templates:/app/templates
    environment:
      - PYTHONUNBUFFERED=1
      - CORS_ORIGINS=http://localhost:5173
      - TEMPLATE_PATH=/app/templates/COC_SV_Del165_20.03.2025.docx

  frontend:
    build: ./frontend
    ports:
      - "5173:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://localhost:8000'''


def create_readme():
    lines = [
        "# COC-D Switcher",
        "",
        "Convert Elbit/Company COCs into Dutch MoD Certificate of Conformity format.",
        "",
        "## Quick Start",
        "",
        "Using Docker:",
        "```bash",
        "docker-compose up --build",
        "```",
        "",
        "Local Development:",
        "```bash",
        "# Backend",
        "cd backend",
        "python3 -m venv venv",
        "source venv/bin/activate",
        "pip install -r requirements.txt",
        "uvicorn app.main:app --reload --port 8000",
        "",
        "# Frontend",
        "cd frontend",
        "npm install",
        "npm run dev",
        "```",
        "",
        "## Access Points",
        "- Frontend: http://localhost:5173",
        "- Backend API: http://localhost:8000",
        "- API Docs: http://localhost:8000/docs"
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    create_project()