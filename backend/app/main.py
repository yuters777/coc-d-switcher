import os
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
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
from . import templates as template_manager

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


# Template Management API
@app.get("/api/templates")
async def list_templates():
    """List all available templates"""
    templates = template_manager.list_templates()
    return {"templates": templates}


@app.get("/api/templates/default")
async def get_default_template():
    """Get the default template"""
    template = template_manager.get_default_template()
    if not template:
        raise HTTPException(status_code=404, detail="No templates available")
    return template


@app.post("/api/templates/upload")
async def upload_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    version: str = Form(...),
    set_as_default: str = Form("false")
):
    """Upload a new template"""
    # Validate file type
    if not file.filename.endswith(".docx"):
        raise HTTPException(status_code=400, detail="Only DOCX files allowed")

    # Save file temporarily
    temp_path = UPLOAD_DIR / file.filename
    try:
        with open(temp_path, "wb") as f:
            content = await file.read()
            f.write(content)

        # Add template
        is_default = set_as_default.lower() == "true"
        template_info = template_manager.add_template(
            file_path=temp_path,
            name=name,
            version=version,
            set_as_default=is_default
        )

        return {"message": "Template uploaded successfully", "template": template_info}
    finally:
        # Clean up temp file
        if temp_path.exists():
            temp_path.unlink()


@app.get("/api/templates/{template_id}/download")
async def download_template(template_id: str):
    """Download a template file"""
    template = template_manager.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    file_path = Path(template["path"])
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Template file not found")

    return FileResponse(
        path=str(file_path),
        filename=template["filename"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )


@app.put("/api/templates/{template_id}/set-default")
async def set_default_template(template_id: str):
    """Set a template as default"""
    success = template_manager.set_default_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template set as default"}


@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    success = template_manager.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete template (not found or is the only template)")
    return {"message": "Template deleted successfully"}
