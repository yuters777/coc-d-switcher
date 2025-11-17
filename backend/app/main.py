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

@app.post("/api/jobs/{job_id}/files")
async def upload_files(
    job_id: str,
    company_coc: UploadFile = File(None),
    packing_slip: UploadFile = File(None)
):
    """Upload PDF files for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    files = {}

    # Save company COC if provided
    if company_coc:
        coc_path = UPLOAD_DIR / f"{job_id}_coc.pdf"
        with open(coc_path, 'wb') as f:
            content = await company_coc.read()
            f.write(content)
        files['coc'] = str(coc_path)

    # Save packing slip if provided
    if packing_slip:
        ps_path = UPLOAD_DIR / f"{job_id}_packing.pdf"
        with open(ps_path, 'wb') as f:
            content = await packing_slip.read()
            f.write(content)
        files['packing'] = str(ps_path)

    # Update job with file paths
    jobs_db[job_id]['files'] = files
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    return {"message": "Files uploaded successfully", "files": files}

@app.post("/api/jobs/{job_id}/parse")
async def parse_documents(job_id: str):
    """Parse uploaded PDF documents and extract data"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    # Check if files have been uploaded
    if not job.get('files'):
        raise HTTPException(status_code=400, detail="No files uploaded for this job")

    # Extract data from PDFs
    coc_path = job['files'].get('coc')
    packing_path = job['files'].get('packing')

    extracted_data = extract_from_pdfs(coc_path, packing_path)

    # Update job with extracted data
    jobs_db[job_id]['extracted_data'] = extracted_data
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    # Return wrapped in expected structure for frontend
    return {"extracted_data": extracted_data}

@app.post("/api/jobs/{job_id}/manual")
async def save_manual_data(job_id: str, manual_data: dict):
    """Save manually entered data for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    # Update job with manual data
    jobs_db[job_id]['manual_data'] = manual_data
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    return {"message": "Manual data saved", "manual_data": manual_data}

@app.post("/api/jobs/{job_id}/validate")
async def validate_job(job_id: str):
    """Validate conversion data for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    # Prepare conversion data
    conv_data = {
        "extracted_data": job.get('extracted_data'),
        "manual_data": job.get('manual_data'),
        "template_vars": {}
    }

    # Validate the conversion
    validation_result = validate_conversion(conv_data)

    # Update job with validation results
    jobs_db[job_id]['validation'] = validation_result
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    return validation_result

@app.post("/api/jobs/{job_id}/render")
async def render_job(job_id: str):
    """Render final documents for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    # Prepare conversion data for rendering
    conv_json = {
        "extracted_data": job.get('extracted_data'),
        "manual_data": job.get('manual_data'),
        "template_vars": job.get('extracted_data', {}).get('template_vars', {}),
        "part_I": job.get('extracted_data', {}).get('part_I', {}),
        "part_II": job.get('extracted_data', {}).get('part_II', {})
    }

    # Merge manual data into template_vars if available
    if job.get('manual_data'):
        conv_json['template_vars'].update(job['manual_data'])
        conv_json['manual_data'] = job['manual_data']

    # Render DOCX
    docx_path = render_docx(conv_json, job_id)

    # Convert to PDF
    pdf_path = convert_to_pdf(docx_path)

    # Update job with rendered file paths
    jobs_db[job_id]['rendered_files'] = {
        'docx': str(docx_path),
        'pdf': str(pdf_path)
    }
    jobs_db[job_id]['status'] = 'completed'
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    return {
        "message": "Documents rendered successfully",
        "files": {
            "docx": str(docx_path),
            "pdf": str(pdf_path)
        }
    }

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
