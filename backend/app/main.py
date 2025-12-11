import os
import re
import tempfile
import logging
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

# Security logging setup
security_logger = logging.getLogger("security")
security_logger.setLevel(logging.INFO)

# Constants for security limits
MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024  # 50MB max file size
MAX_TEMPLATE_SIZE_BYTES = 10 * 1024 * 1024  # 10MB max template size

# DOCX files are ZIP archives - magic bytes for ZIP format
DOCX_MAGIC_BYTES = b'PK\x03\x04'
PDF_MAGIC_BYTES = b'%PDF'

app = FastAPI(title="COC-D Switcher API")

# CORS configuration - SECURITY: Do not use wildcard "*" with credentials
# In production, strictly define allowed origins
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
# Strip whitespace and filter empty strings
cors_origins = [origin.strip() for origin in cors_origins if origin.strip()]

# SECURITY: Validate that no wildcard is used with credentials
allow_credentials = os.getenv("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"
if "*" in cors_origins and allow_credentials:
    security_logger.warning(
        "SECURITY WARNING: CORS wildcard origin with credentials is insecure. "
        "Disabling credentials for wildcard origins."
    )
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # Restrict to needed methods
    allow_headers=["*"],
)

jobs_db: Dict[str, Dict[str, Any]] = {}
UPLOAD_DIR = Path(tempfile.gettempdir()) / "coc-uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


# =============================================================================
# Security Helper Functions
# =============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent path traversal attacks.

    - Extracts only the base filename (removes directory components)
    - Removes dangerous characters
    - Validates against path traversal patterns

    Args:
        filename: User-provided filename

    Returns:
        Sanitized filename safe for file system operations

    Raises:
        HTTPException: If filename contains path traversal attempts
    """
    if not filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    # Extract only the base filename (removes any path components)
    safe_filename = Path(filename).name

    # Check for path traversal attempts
    if ".." in filename or filename != safe_filename:
        security_logger.warning(
            f"SECURITY: Path traversal attempt detected in filename: {filename}"
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid filename: path traversal not allowed"
        )

    # Remove any null bytes (can cause issues on some systems)
    safe_filename = safe_filename.replace('\x00', '')

    # Only allow alphanumeric, underscore, hyphen, and period
    if not re.match(r'^[\w\-. ]+$', safe_filename):
        security_logger.warning(
            f"SECURITY: Invalid characters in filename: {filename}"
        )
        raise HTTPException(
            status_code=400,
            detail="Invalid filename: contains disallowed characters"
        )

    return safe_filename


def validate_file_magic_bytes(content: bytes, expected_magic: bytes, file_type: str) -> None:
    """
    Validate file content by checking magic bytes (file header).

    This provides defense against file type spoofing where an attacker
    renames a malicious file to have a trusted extension.

    Args:
        content: File content bytes
        expected_magic: Expected magic bytes for the file type
        file_type: Human-readable file type name for error messages

    Raises:
        HTTPException: If magic bytes don't match expected value
    """
    if not content.startswith(expected_magic):
        security_logger.warning(
            f"SECURITY: File magic bytes mismatch. Expected {file_type}, "
            f"got header: {content[:10].hex()}"
        )
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. File must be a valid {file_type}."
        )


async def read_file_with_size_limit(
    file: UploadFile,
    max_size: int,
    file_type: str = "file"
) -> bytes:
    """
    Read uploaded file content with size limit validation.

    Reads file in chunks to prevent memory exhaustion from large files.

    Args:
        file: FastAPI UploadFile object
        max_size: Maximum allowed file size in bytes
        file_type: File type name for error messages

    Returns:
        File content as bytes

    Raises:
        HTTPException: If file exceeds size limit
    """
    chunks = []
    total_size = 0
    chunk_size = 64 * 1024  # 64KB chunks

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_size:
            security_logger.warning(
                f"SECURITY: File size limit exceeded. Type: {file_type}, "
                f"Limit: {max_size}, Received: >{total_size}"
            )
            raise HTTPException(
                status_code=413,
                detail=f"{file_type} file too large. Maximum size is {max_size // (1024*1024)}MB."
            )
        chunks.append(chunk)

    return b''.join(chunks)

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
    """Upload PDF files for a job.

    Security measures:
    - File size limits enforced (50MB max)
    - PDF magic bytes validation
    - Filenames are not user-controlled (UUID-based)
    """
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    files = {}

    # Save company COC if provided
    if company_coc:
        # Read with size limit
        content = await read_file_with_size_limit(
            company_coc, MAX_FILE_SIZE_BYTES, "PDF"
        )

        # Validate PDF magic bytes
        validate_file_magic_bytes(content, PDF_MAGIC_BYTES, "PDF")

        # Use UUID-based filename (not user-controlled) - secure by design
        coc_path = UPLOAD_DIR / f"{job_id}_coc.pdf"
        with open(coc_path, 'wb') as f:
            f.write(content)
        files['coc'] = str(coc_path)
        security_logger.info(f"SECURITY: PDF uploaded for job {job_id} (COC)")

    # Save packing slip if provided
    if packing_slip:
        # Read with size limit
        content = await read_file_with_size_limit(
            packing_slip, MAX_FILE_SIZE_BYTES, "PDF"
        )

        # Validate PDF magic bytes
        validate_file_magic_bytes(content, PDF_MAGIC_BYTES, "PDF")

        # Use UUID-based filename (not user-controlled) - secure by design
        ps_path = UPLOAD_DIR / f"{job_id}_packing.pdf"
        with open(ps_path, 'wb') as f:
            f.write(content)
        files['packing'] = str(ps_path)
        security_logger.info(f"SECURITY: PDF uploaded for job {job_id} (Packing Slip)")

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

    # Get template info
    default_template = template_manager.get_default_template()
    template_info = default_template if default_template else {"name": "Default", "version": "1.0"}

    # Update job with rendered file paths
    jobs_db[job_id]['rendered_files'] = {
        'docx': str(docx_path),
        'pdf': str(pdf_path)
    }
    jobs_db[job_id]['status'] = 'completed'
    jobs_db[job_id]['updated_at'] = datetime.utcnow().isoformat()

    return {
        "message": "Documents rendered successfully",
        "rendered_file": str(docx_path),
        "template_used": template_info,
        "files": {
            "docx": str(docx_path),
            "pdf": str(pdf_path)
        }
    }

@app.get("/api/jobs/{job_id}/download")
async def download_job(job_id: str):
    """Download the rendered DOCX file for a job"""
    if job_id not in jobs_db:
        raise HTTPException(status_code=404, detail="Job not found")

    job = jobs_db[job_id]

    # Check if files have been rendered
    if not job.get('rendered_files'):
        raise HTTPException(status_code=400, detail="No rendered files available for this job")

    # Get the DOCX file path
    docx_path = job['rendered_files'].get('docx')
    if not docx_path or not Path(docx_path).exists():
        raise HTTPException(status_code=404, detail="Rendered DOCX file not found")

    # Return the file with the correct filename
    filename = Path(docx_path).name
    return FileResponse(
        path=docx_path,
        media_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        filename=filename
    )


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
    """Upload a new template.

    Security measures (SAST fixes):
    - P1: Filename sanitization to prevent path traversal
    - P3: Magic bytes validation to verify actual file type
    - P4: File size limits enforced
    """
    # SECURITY P1: Sanitize filename to prevent path traversal attacks
    # This prevents filenames like "../../etc/cron.d/exploit"
    safe_filename = sanitize_filename(file.filename)

    # Validate file extension (first layer of defense)
    if not safe_filename.lower().endswith(".docx"):
        security_logger.warning(
            f"SECURITY: Template upload rejected - invalid extension: {safe_filename}"
        )
        raise HTTPException(status_code=400, detail="Only DOCX files allowed")

    # SECURITY P4: Read file with size limit
    content = await read_file_with_size_limit(
        file, MAX_TEMPLATE_SIZE_BYTES, "Template"
    )

    # SECURITY P3: Validate DOCX magic bytes (DOCX files are ZIP archives)
    # This prevents file type spoofing where a malicious file is renamed to .docx
    validate_file_magic_bytes(content, DOCX_MAGIC_BYTES, "DOCX")

    # Use UUID-based temp filename to ensure uniqueness and prevent overwrites
    temp_filename = f"{uuid.uuid4()}_{safe_filename}"
    temp_path = UPLOAD_DIR / temp_filename

    security_logger.info(
        f"SECURITY: Template upload - original: {file.filename}, "
        f"sanitized: {safe_filename}, temp: {temp_filename}"
    )

    try:
        with open(temp_path, "wb") as f:
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
