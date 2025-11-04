import os
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

@app.post("/api/jobs/{job_id}/files")
async def upload_files(
    job_id: str,
    company_coc: Optional[UploadFile] = File(None),
    packing_slip: Optional[UploadFile] = File(None)
):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    files = {}
    if company_coc:
        coc_path = job_dir / "company_coc.pdf"
        with open(coc_path, "wb") as f:
            f.write(await company_coc.read())
        files["company_coc"] = str(coc_path)

    if packing_slip:
        packing_path = job_dir / "packing_slip.pdf"
        with open(packing_path, "wb") as f:
            f.write(await packing_slip.read())
        files["packing_slip"] = str(packing_path)

    jobs_db[job_id]["files"] = files
    jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()

    return {"message": "Files uploaded", "files": files}

@app.post("/api/jobs/{job_id}/parse")
async def parse_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]
    files = job.get("files", {})

    company_coc_path = files.get("company_coc")
    packing_slip_path = files.get("packing_slip")

    extracted = extract_from_pdfs(company_coc_path, packing_slip_path)

    jobs_db[job_id]["extracted_data"] = extracted
    jobs_db[job_id]["status"] = "extracted"
    jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()

    return extracted

@app.post("/api/jobs/{job_id}/validate")
async def validate_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]
    extracted_data = job.get("extracted_data")

    if not extracted_data:
        # If no extracted data, extract first
        files = job.get("files", {})
        extracted_data = extract_from_pdfs(
            files.get("company_coc"),
            files.get("packing_slip")
        )
        jobs_db[job_id]["extracted_data"] = extracted_data

    validation = validate_conversion(extracted_data)
    jobs_db[job_id]["validation"] = validation
    jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()

    return validation

@app.post("/api/jobs/{job_id}/render")
async def render_job(job_id: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]
    extracted_data = job.get("extracted_data")

    if not extracted_data:
        raise HTTPException(status_code=400, detail="No extracted data. Run parse first.")

    job_dir = UPLOAD_DIR / job_id
    job_dir.mkdir(exist_ok=True)

    # Render DOCX
    docx_path = job_dir / "output.docx"
    render_docx(extracted_data, str(docx_path))

    # Render PDF
    pdf_path = job_dir / "output.pdf"
    convert_to_pdf(str(docx_path), str(pdf_path))

    jobs_db[job_id]["rendered_files"] = {
        "docx": str(docx_path),
        "pdf": str(pdf_path)
    }
    jobs_db[job_id]["status"] = "completed"
    jobs_db[job_id]["updated_at"] = datetime.utcnow().isoformat()

    return {"message": "Rendered", "docx": str(docx_path), "pdf": str(pdf_path)}

@app.get("/api/jobs/{job_id}/download/{file_type}")
async def download_file(job_id: str, file_type: str):
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]
    rendered_files = job.get("rendered_files", {})

    if file_type not in rendered_files:
        raise HTTPException(status_code=404, detail=f"{file_type} file not found")

    file_path = rendered_files[file_type]

    if not Path(file_path).exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        file_path,
        media_type="application/octet-stream",
        filename=f"output.{file_type}"
    )

# Template management endpoints
TEMPLATES_DIR = Path("/tmp/coc-templates")
TEMPLATES_DIR.mkdir(exist_ok=True)

templates_db: Dict[str, Dict[str, Any]] = {}
default_template_id: Optional[str] = None

@app.get("/api/templates")
async def list_templates():
    return list(templates_db.values())

@app.get("/api/templates/default")
async def get_default_template():
    if not default_template_id or default_template_id not in templates_db:
        raise HTTPException(status_code=404, detail="No templates available")
    return templates_db[default_template_id]

@app.post("/api/templates/upload")
async def upload_template(file: UploadFile = File(...)):
    if not file.filename.endswith('.docx'):
        raise HTTPException(status_code=400, detail="Only .docx files are allowed")

    template_id = str(uuid.uuid4())
    template_path = TEMPLATES_DIR / f"{template_id}.docx"

    with open(template_path, "wb") as f:
        f.write(await file.read())

    templates_db[template_id] = {
        "id": template_id,
        "filename": file.filename,
        "path": str(template_path),
        "uploaded_at": datetime.utcnow().isoformat(),
        "is_default": len(templates_db) == 0
    }

    global default_template_id
    if len(templates_db) == 1:
        default_template_id = template_id

    return templates_db[template_id]

@app.post("/api/templates/{template_id}/set-default")
async def set_default_template(template_id: str):
    if template_id not in templates_db:
        raise HTTPException(status_code=404, detail="Template not found")

    global default_template_id

    # Unset previous default
    if default_template_id and default_template_id in templates_db:
        templates_db[default_template_id]["is_default"] = False

    # Set new default
    templates_db[template_id]["is_default"] = True
    default_template_id = template_id

    return {"message": "Default template updated", "template_id": template_id}

@app.get("/api/templates/{template_id}/download")
async def download_template(template_id: str):
    if template_id not in templates_db:
        raise HTTPException(status_code=404, detail="Template not found")

    template = templates_db[template_id]
    template_path = template["path"]

    if not Path(template_path).exists():
        raise HTTPException(status_code=404, detail="Template file not found on disk")

    return FileResponse(
        template_path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=template["filename"]
    )

@app.delete("/api/templates/{template_id}")
async def delete_template(template_id: str):
    if template_id not in templates_db:
        raise HTTPException(status_code=404, detail="Template not found")

    if len(templates_db) == 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last template")

    template = templates_db[template_id]
    is_default = template.get("is_default", False)

    # Delete file
    template_path = Path(template["path"])
    if template_path.exists():
        template_path.unlink()

    # Remove from database
    del templates_db[template_id]

    # If deleted template was default, set a new default
    global default_template_id
    if is_default and templates_db:
        new_default_id = list(templates_db.keys())[0]
        templates_db[new_default_id]["is_default"] = True
        default_template_id = new_default_id

    return {"message": "Template deleted"}
