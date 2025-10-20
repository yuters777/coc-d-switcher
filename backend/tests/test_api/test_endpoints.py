import pytest
from fastapi.testclient import TestClient
import json

class TestAPIEndpoints:
    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200
        assert "COC-D Switcher API" in response.json()["message"]
    
    def test_create_job(self, client):
        """Test job creation"""
        job_data = {
            "name": "Test Shipment",
            "submitted_by": "Test User"
        }
        response = client.post("/api/jobs", json=job_data)
        assert response.status_code == 200
        data = response.json()
        assert "job_id" in data
        assert len(data["job_id"]) == 36  # UUID length
    
    def test_get_nonexistent_job(self, client):
        """Test getting job that doesn't exist"""
        response = client.get("/api/jobs/nonexistent-id")
        assert response.status_code == 404
    
    def test_list_jobs(self, client):
        """Test listing all jobs"""
        # Create a job first
        client.post("/api/jobs", json={"name": "Test", "submitted_by": "User"})
        
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_upload_files(self, client):
        """Test file upload endpoint"""
        # Create job first
        job_response = client.post("/api/jobs", json={"name": "Test", "submitted_by": "User"})
        job_id = job_response.json()["job_id"]
        
        # Upload files (mock)
        files = {
            'company_coc': ('coc.pdf', b'PDF content', 'application/pdf'),
            'packing_slip': ('packing.pdf', b'PDF content', 'application/pdf')
        }
        response = client.post(f"/api/jobs/{job_id}/files", files=files)
        assert response.status_code == 200
    
    def test_parse_job(self, client, sample_data):
        """Test parse endpoint"""
        # Create and setup job
        job_response = client.post("/api/jobs", json={"name": "Test", "submitted_by": "User"})
        job_id = job_response.json()["job_id"]
        
        response = client.post(f"/api/jobs/{job_id}/parse")
        assert response.status_code == 200
        assert "part_I" in response.json()
    
    def test_validate_job(self, client):
        """Test validation endpoint"""
        # Create job
        job_response = client.post("/api/jobs", json={"name": "Test", "submitted_by": "User"})
        job_id = job_response.json()["job_id"]
        
        # Parse first (to get data)
        client.post(f"/api/jobs/{job_id}/parse")
        
        # Validate
        response = client.post(f"/api/jobs/{job_id}/validate")
        assert response.status_code == 200
        assert "errors" in response.json()
        assert "warnings" in response.json()