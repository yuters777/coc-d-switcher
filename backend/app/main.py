import os
import tempfile
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
from .templates import list_templates, add_template, set_default_template, delete_template

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
# Use cross-platform temporary directory
UPLOAD_DIR = Path(tempfile.gettempdir()) / "coc-uploads"
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)

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

# Template Management Endpoints
@app.get("/api/templates")
async def get_templates():
    """Get list of all templates"""
    templates = list_templates()
    return {"templates": templates}

@app.post("/api/templates")
async def upload_template(
    file: UploadFile = File(...),
    name: str = None,
    version: str = None,
    set_as_default: bool = False
):
    """Upload a new template"""
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files are supported")

    # Save uploaded file temporarily
    temp_path = UPLOAD_DIR / f"template_{uuid.uuid4()}_{file.filename}"
    with open(temp_path, 'wb') as f:
        content = await file.read()
        f.write(content)

    try:
        template = add_template(
            temp_path,
            name or file.filename,
            version or "1.0",
            set_as_default
        )
        return template
    except Exception as e:
        temp_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/templates/{template_id}/default")
async def set_template_default(template_id: str):
    """Set a template as default"""
    success = set_default_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template set as default"}

@app.delete("/api/templates/{template_id}")
async def remove_template(template_id: str):
    """Delete a template"""
    success = delete_template(template_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete template")
    return {"message": "Template deleted"}
