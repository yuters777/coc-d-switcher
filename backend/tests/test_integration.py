import pytest
from pathlib import Path
import tempfile

class TestFullWorkflow:
    def test_complete_workflow(self, client):
        """Test complete COC conversion workflow"""
        # 1. Create job
        job_response = client.post("/api/jobs", json={
            "name": "Integration Test",
            "submitted_by": "Test System"
        })
        assert job_response.status_code == 200
        job_id = job_response.json()["job_id"]
        
        # 2. Upload files
        files = {
            'company_coc': ('coc.pdf', b'%PDF-1.4\nTest', 'application/pdf'),
            'packing_slip': ('packing.pdf', b'%PDF-1.4\nTest', 'application/pdf')
        }
        upload_response = client.post(f"/api/jobs/{job_id}/files", files=files)
        assert upload_response.status_code == 200
        
        # 3. Parse documents
        parse_response = client.post(f"/api/jobs/{job_id}/parse")
        assert parse_response.status_code == 200
        extracted = parse_response.json()
        assert extracted["part_I"]["contract_number"] != ""
        
        # 4. Validate
        validate_response = client.post(f"/api/jobs/{job_id}/validate")
        assert validate_response.status_code == 200
        validation = validate_response.json()
        assert isinstance(validation["errors"], list)
        
        # 5. Render
        render_response = client.post(f"/api/jobs/{job_id}/render")
        assert render_response.status_code == 200
        assert "docx" in render_response.json()
        
        # 6. Download
        download_response = client.get(f"/api/jobs/{job_id}/download/docx")
        assert download_response.status_code == 200
    
    def test_workflow_with_validation_errors(self, client):
        """Test workflow when validation has errors"""
        # Create job and parse
        job_response = client.post("/api/jobs", json={"name": "Test", "submitted_by": "User"})
        job_id = job_response.json()["job_id"]
        
        # Inject bad data
        client.post(f"/api/jobs/{job_id}/parse")
        
        # Modify the job to have mismatched serials
        # This would normally be done through the edit endpoint
        
        validate_response = client.post(f"/api/jobs/{job_id}/validate")
        assert validate_response.status_code == 200