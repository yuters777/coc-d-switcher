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
import logging

from .schemas import JobData, ValidationResult, ConversionOutput
from .extract import extract_from_pdfs
from .validate import validate_conversion
from .render import render_docx, convert_to_pdf
from .config import load_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
    """Root endpoint"""
    try:
        return {"message": "COC-D Switcher API", "docs": "/docs"}
    except Exception as e:
        logger.error(f"Error in root endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/jobs")
async def create_job(job: JobCreate):
    """Create a new job"""
    try:
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
        logger.info(f"Created job {job_id}")
        return {"job_id": job_id}
    except Exception as e:
        logger.error(f"Error creating job: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create job: {str(e)}")

@app.get("/api/jobs")
async def list_jobs():
    """List all jobs"""
    try:
        return list(jobs_db.values())
    except Exception as e:
        logger.error(f"Error listing jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list jobs")

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str):
    """Get a specific job by ID"""
    try:
        if not job_id:
            raise HTTPException(status_code=400, detail="Job ID is required")
        if job_id not in jobs_db:
            raise HTTPException(status_code=404, detail="Job not found")
        return jobs_db[job_id]
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get job")
