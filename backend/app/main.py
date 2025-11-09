import os
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import json
import tempfile
from datetime import datetime
from pathlib import Path

from .schemas import JobData, ValidationResult, ConversionOutput
from .extract import extract_from_pdfs
from .validate import validate_conversion
from .render import render_docx, convert_to_pdf
from .config import load_config
from . import templates

app = FastAPI(title="COC-D Switcher API")

logger = logging.getLogger("uvicorn")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Custom handler to log validation errors for debugging"""
    body = None
    try:
        body = await request.body()
        body_text = body.decode('utf-8') if body else "empty"
    except:
        body_text = "could not decode"

    logger.error(f"Validation error on {request.method} {request.url.path}")
    logger.error(f"Request body: {body_text}")
    logger.error(f"Errors: {exc.errors()}")

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body_text}
    )

cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://10.2.11.7:5173,http://127.0.0.1:5173").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

jobs_db: Dict[str, Dict[str, Any]] = {}
# Use cross-platform temp directory or local uploads folder
UPLOAD_DIR = Path(tempfile.gettempdir()) / "coc-uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class JobCreate(BaseModel):
    name: str
    submitted_by: str

@app.get("/")
async def root():
    return {"message": "COC-D Switcher API", "docs": "/docs"}

@app.post("/api/jobs")
async def create_job(job: JobCreate):
    logger.info(f"Creating job: name={job.name}, submitted_by={job.submitted_by}")

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
    logger.info(f"Job created successfully: {job_id}")
    return {"job_id": job_id}

@app.get("/api/jobs")
async def list_jobs():
    return list(jobs_db.values())

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs_db[job_id]

@app.post("/api/jobs/{job_id}/files")
async def upload_job_files(
    job_id: str,
    company_coc: UploadFile = File(...),
    packing_slip: UploadFile = File(...)
):
    """Upload COC and Packing Slip PDF files for a job"""
    logger.info(f"Uploading files for job {job_id}")

    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    # Validate file types
    if not company_coc.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Company COC must be a PDF file")
    if not packing_slip.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Packing slip must be a PDF file")

    # Create job-specific directory
    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    # Save files
    coc_path = job_dir / f"company_coc_{company_coc.filename}"
    packing_path = job_dir / f"packing_slip_{packing_slip.filename}"

    try:
        # Write COC file
        coc_content = await company_coc.read()
        coc_path.write_bytes(coc_content)
        logger.info(f"Saved COC file: {coc_path}")

        # Write packing slip file
        packing_content = await packing_slip.read()
        packing_path.write_bytes(packing_content)
        logger.info(f"Saved packing slip file: {packing_path}")

        # Update job record
        jobs_db[job_id]["files"] = {
            "company_coc": str(coc_path),
            "packing_slip": str(packing_path)
        }
        jobs_db[job_id]["status"] = "files_uploaded"
        jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()

        logger.info(f"Files uploaded successfully for job {job_id}")

        return {
            "message": "Files uploaded successfully",
            "job_id": job_id,
            "files": {
                "company_coc": company_coc.filename,
                "packing_slip": packing_slip.filename
            }
        }
    except Exception as e:
        logger.error(f"Error uploading files: {e}")
        # Clean up on error
        if coc_path.exists():
            coc_path.unlink()
        if packing_path.exists():
            packing_path.unlink()
        raise HTTPException(status_code=500, detail=f"Failed to upload files: {str(e)}")

# Template Management Endpoints
@app.get("/api/templates")
async def list_templates():
    """List all available templates"""
    template_list = templates.list_templates()
    return {"templates": template_list}

@app.get("/api/templates/default")
async def get_default_template():
    """Get the default template"""
    template = templates.get_default_template()
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
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only DOCX files allowed")

    # Save uploaded file to temp location
    temp_file = Path(tempfile.mktemp(suffix=".docx"))
    try:
        content = await file.read()
        temp_file.write_bytes(content)

        # Add template to system
        set_default = set_as_default.lower() in ("true", "1", "yes")
        template_info = templates.add_template(
            file_path=temp_file,
            name=name,
            version=version,
            set_as_default=set_default
        )

        return {
            "message": "Template uploaded successfully",
            "template": template_info
        }
    finally:
        # Clean up temp file
        if temp_file.exists():
            temp_file.unlink()

@app.put("/api/templates/{template_id}/set-default")
async def set_default_template(template_id: str):
    """Set a template as the default"""
    success = templates.set_default_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"message": "Template set as default"}

@app.get("/api/templates/{template_id}/download")
async def download_template(template_id: str):
    """Download a template file"""
    template = templates.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    template_path = Path(template["path"])
    if not template_path.exists():
        raise HTTPException(status_code=404, detail="Template file not found")

    return FileResponse(
        path=str(template_path),
        filename=template["filename"],
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    """Delete a template"""
    success = templates.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot delete template (not found or last remaining template)")
    return {"message": "Template deleted successfully"}
