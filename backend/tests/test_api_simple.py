import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

# Mock pdfplumber before importing app
import unittest.mock as mock
sys.modules['pdfplumber'] = mock.MagicMock()

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "COC-D Switcher API" in response.json()["message"]

def test_create_job():
    """Test creating a job"""
    response = client.post("/api/jobs", json={
        "name": "Test Job",
        "submitted_by": "Tester"
    })
    assert response.status_code == 200
    assert "job_id" in response.json()
    # Return statement removed - it was causing a warning

def test_full_workflow():
    """Test the complete workflow"""
    # 1. Create job
    create_response = client.post("/api/jobs", json={
        "name": "Workflow Test",
        "submitted_by": "Tester"
    })
    job_id = create_response.json()["job_id"]
    
    # 2. Parse (using fixtures)
    parse_response = client.post(f"/api/jobs/{job_id}/parse")
    assert parse_response.status_code == 200
    
    # 3. Validate
    validate_response = client.post(f"/api/jobs/{job_id}/validate")
    assert validate_response.status_code == 200
    assert "errors" in validate_response.json()
    
    # 4. Render
    render_response = client.post(f"/api/jobs/{job_id}/render")
    assert render_response.status_code == 200
    
    # 5. Check job status
    job_response = client.get(f"/api/jobs/{job_id}")
    assert job_response.status_code == 200
    assert job_response.json()["status"] == "rendered"

def test_list_jobs():
    """Test listing all jobs"""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_get_nonexistent_job():
    """Test 404 for non-existent job"""
    response = client.get("/api/jobs/fake-id-12345")
    assert response.status_code == 404
    assert "Job not found" in response.json()["detail"]

def test_validate_without_parse():
    """Test validation on job without parsed data"""
    # Create job but skip parse
    create_response = client.post("/api/jobs", json={
        "name": "Validation Test",
        "submitted_by": "Tester"
    })
    job_id = create_response.json()["job_id"]
    
    # Validate without parsing first
    validate_response = client.post(f"/api/jobs/{job_id}/validate")
    assert validate_response.status_code == 200
    validation = validate_response.json()
    assert "errors" in validation
    assert "warnings" in validation

def test_job_persistence():
    """Test that jobs persist across requests"""
    # Create a job
    create_response = client.post("/api/jobs", json={
        "name": "Persistence Test",
        "submitted_by": "Tester"
    })
    job_id = create_response.json()["job_id"]
    
    # Get the same job multiple times
    for _ in range(3):
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        assert response.json()["id"] == job_id
        assert response.json()["name"] == "Persistence Test"

def test_file_upload():
    """Test file upload endpoint"""
    # Create job
    create_response = client.post("/api/jobs", json={
        "name": "Upload Test",
        "submitted_by": "Tester"
    })
    job_id = create_response.json()["job_id"]
    
    # Mock file upload
    files = {
        'company_coc': ('coc.pdf', b'%PDF-1.4\nTest COC content', 'application/pdf'),
        'packing_slip': ('packing.pdf', b'%PDF-1.4\nTest packing content', 'application/pdf')
    }
    
    upload_response = client.post(f"/api/jobs/{job_id}/files", files=files)
    assert upload_response.status_code == 200
    assert "successfully" in upload_response.json()["message"]