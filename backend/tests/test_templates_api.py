# backend/tests/test_templates_api.py (NEW FILE)
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import tempfile
import shutil
from app.main import app

client = TestClient(app)

# Test fixture: Create a temporary DOCX file for testing
@pytest.fixture
def test_docx_file():
    """Create a temporary test DOCX file"""
    temp_dir = Path(tempfile.mkdtemp())
    test_file = temp_dir / "test_template.docx"
    
    # Create a minimal DOCX (just a ZIP with required structure)
    import zipfile
    with zipfile.ZipFile(test_file, 'w') as docx:
        docx.writestr('[Content_Types].xml', '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
        docx.writestr('_rels/.rels', '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"></Relationships>')
        docx.writestr('word/document.xml', '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>{{contract_number}}</w:t></w:r></w:p></w:body></w:document>')
    
    yield test_file
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture(autouse=True)
def cleanup_templates():
    """Clean up templates directory before AND after each test"""
    # Cleanup BEFORE test
    templates_dir = Path("templates")
    if templates_dir.exists():
        for file in templates_dir.glob("*"):
            if file.name not in [".gitkeep", "metadata.json"]:
                try:
                    file.unlink()
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not delete {file}: {e}")
        metadata_file = templates_dir / "metadata.json"
        if metadata_file.exists():
            try:
                metadata_file.unlink()
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not delete metadata: {e}")
    
    yield  # Run the test
    
    # Cleanup AFTER test
    if templates_dir.exists():
        for file in templates_dir.glob("*"):
            if file.name not in [".gitkeep"]:
                try:
                    file.unlink()
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not delete {file}: {e}")


class TestTemplateAPI:
    """Test suite for Template Management API"""
    
    def test_01_list_templates_empty(self, cleanup_templates):
        """Test 2: List templates when empty"""
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert "templates" in data
        assert isinstance(data["templates"], list)
        print("✅ Test 2: List templates (empty) - PASSED")
    
    def test_02_get_default_template_not_found(self, cleanup_templates):
        """Test 3: Get default template when none exists"""
        response = client.get("/api/templates/default")
        assert response.status_code == 404
        assert response.json()["detail"] == "No templates available"
        print("✅ Test 3: Get default template (404) - PASSED")
    
    def test_03_upload_first_template(self, test_docx_file, cleanup_templates):
        """Test 4: Upload first template"""
        with open(test_docx_file, "rb") as f:
            response = client.post(
                "/api/templates/upload",
                files={"file": ("test_template.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={
                    "name": "Dutch COC v1",
                    "version": "1.0",
                    "set_as_default": "true"
                }
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Template uploaded successfully"
        assert "template" in data
        
        template = data["template"]
        assert template["name"] == "Dutch COC v1"
        assert template["version"] == "1.0"
        assert template["is_default"] == True
        assert "id" in template
        assert "path" in template
        
        # Verify file exists
        assert Path(template["path"]).exists()
        print("✅ Test 4: Upload first template - PASSED")
        
        return template["id"]  # Return for use in other tests
    
    def test_04_list_templates_with_data(self, test_docx_file, cleanup_templates):
        """Test 5: List templates after upload"""
        # First upload a template
        with open(test_docx_file, "rb") as f:
            client.post(
                "/api/templates/upload",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test", "version": "1.0", "set_as_default": "true"}
            )
        
        # Now list templates
        response = client.get("/api/templates")
        assert response.status_code == 200
        data = response.json()
        assert len(data["templates"]) == 1
        assert data["templates"][0]["is_default"] == True
        print("✅ Test 5: List templates (with data) - PASSED")
    
    def test_05_get_default_template_success(self, test_docx_file, cleanup_templates):
        """Test 6: Get default template after upload"""
        # Upload template
        with open(test_docx_file, "rb") as f:
            client.post(
                "/api/templates/upload",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test", "version": "1.0", "set_as_default": "true"}
            )
        
        # Get default
        response = client.get("/api/templates/default")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test"
        assert data["is_default"] == True
        print("✅ Test 6: Get default template (success) - PASSED")
    
    def test_06_upload_second_template(self, test_docx_file, cleanup_templates):
        """Test 7: Upload second template (not default)"""
        # Upload first template
        with open(test_docx_file, "rb") as f:
            client.post(
                "/api/templates/upload",
                files={"file": ("test1.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 1", "version": "1.0", "set_as_default": "true"}
            )
        
        # Upload second template
        with open(test_docx_file, "rb") as f:
            response = client.post(
                "/api/templates/upload",
                files={"file": ("test2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 2", "version": "2.0", "set_as_default": "false"}
            )
        
        assert response.status_code == 200
        
        # Verify first is still default
        default_response = client.get("/api/templates/default")
        assert default_response.json()["name"] == "Template 1"
        print("✅ Test 7: Upload second template - PASSED")
    
    def test_07_set_default_template(self, test_docx_file, cleanup_templates):
        """Test 8: Set second template as default"""
        # Upload two templates
        with open(test_docx_file, "rb") as f:
            client.post(
                "/api/templates/upload",
                files={"file": ("test1.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 1", "version": "1.0", "set_as_default": "true"}
            )
        
        with open(test_docx_file, "rb") as f:
            upload_response = client.post(
                "/api/templates/upload",
                files={"file": ("test2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 2", "version": "2.0", "set_as_default": "false"}
            )
        
        template2_id = upload_response.json()["template"]["id"]
        
        # Set second as default
        response = client.put(f"/api/templates/{template2_id}/set-default")
        assert response.status_code == 200
        
        # Verify it's now default
        default_response = client.get("/api/templates/default")
        assert default_response.json()["name"] == "Template 2"
        print("✅ Test 8: Set default template - PASSED")
    
    def test_08_download_template(self, test_docx_file, cleanup_templates):
        """Test 9: Download template"""
        # Upload template
        with open(test_docx_file, "rb") as f:
            upload_response = client.post(
                "/api/templates/upload",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test", "version": "1.0", "set_as_default": "true"}
            )
        
        template_id = upload_response.json()["template"]["id"]
        
        # Download template
        response = client.get(f"/api/templates/{template_id}/download")
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        print("✅ Test 9: Download template - PASSED")
    
    def test_09_delete_non_default_template(self, test_docx_file, cleanup_templates):
        """Test 10: Delete non-default template"""
        # Upload two templates
        with open(test_docx_file, "rb") as f:
            upload1 = client.post(
                "/api/templates/upload",
                files={"file": ("test1.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 1", "version": "1.0", "set_as_default": "true"}
            )
        
        with open(test_docx_file, "rb") as f:
            upload2 = client.post(
                "/api/templates/upload",
                files={"file": ("test2.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Template 2", "version": "2.0", "set_as_default": "false"}
            )
        
        template2_id = upload2.json()["template"]["id"]
        
        # Delete non-default template
        response = client.delete(f"/api/templates/{template2_id}")
        assert response.status_code == 200
        
        # Verify it's gone
        list_response = client.get("/api/templates")
        assert len(list_response.json()["templates"]) == 1
        print("✅ Test 10: Delete non-default template - PASSED")
    
    def test_10_cannot_delete_last_template(self, test_docx_file, cleanup_templates):
        """Test 11: Cannot delete last remaining template"""
        # Upload one template
        with open(test_docx_file, "rb") as f:
            upload_response = client.post(
                "/api/templates/upload",
                files={"file": ("test.docx", f, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
                data={"name": "Test", "version": "1.0", "set_as_default": "true"}
            )
        
        template_id = upload_response.json()["template"]["id"]
        
        # Try to delete it
        response = client.delete(f"/api/templates/{template_id}")
        assert response.status_code == 400
        assert "Cannot delete template" in response.json()["detail"]
        print("✅ Test 11: Cannot delete last template - PASSED")
    
    def test_11_upload_non_docx_file(self, cleanup_templates):
        """Test 26: Upload non-DOCX file"""
        # Create a fake PDF file
        temp_file = Path(tempfile.mktemp(suffix=".pdf"))
        temp_file.write_bytes(b"fake pdf content")
        
        try:
            with open(temp_file, "rb") as f:
                response = client.post(
                    "/api/templates/upload",
                    files={"file": ("test.pdf", f, "application/pdf")},
                    data={"name": "Test", "version": "1.0", "set_as_default": "true"}
                )
            
            assert response.status_code == 400
            assert response.json()["detail"] == "Only DOCX files allowed"
            print("✅ Test 26: Upload non-DOCX rejected - PASSED")
        finally:
            temp_file.unlink()
    
    def test_12_set_default_nonexistent_template(self, cleanup_templates):
        """Test: Set default for non-existent template"""
        response = client.put("/api/templates/fake-uuid/set-default")
        assert response.status_code == 404
        print("✅ Test: Set default non-existent template - PASSED")
    
    def test_13_delete_nonexistent_template(self, cleanup_templates):
        """Test: Delete non-existent template"""
        response = client.delete("/api/templates/fake-uuid")
        assert response.status_code == 400
        print("✅ Test: Delete non-existent template - PASSED")


# Standalone test runner
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])