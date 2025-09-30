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
