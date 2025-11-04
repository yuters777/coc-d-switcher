# tests/test_unit/test_templates.py
import pytest
from pathlib import Path
import json
import tempfile
import shutil
from app.templates import (
    load_metadata,
    save_metadata,
    list_templates,
    get_template,
    get_default_template,
    add_template,
    set_default_template,
    delete_template,
    TEMPLATES_DIR,
    TEMPLATE_METADATA_FILE
)


@pytest.fixture
def temp_templates_dir(monkeypatch):
    """Create a temporary templates directory for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        templates_dir = tmpdir_path / "templates"
        templates_dir.mkdir(exist_ok=True)

        # Monkey patch the TEMPLATES_DIR and TEMPLATE_METADATA_FILE
        monkeypatch.setattr("app.templates.TEMPLATES_DIR", templates_dir)
        monkeypatch.setattr("app.templates.TEMPLATE_METADATA_FILE", templates_dir / "metadata.json")

        yield templates_dir


@pytest.fixture
def sample_template_file():
    """Create a temporary sample template file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
        f.write("Sample template content")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestTemplatesModule:
    """Test suite for templates module"""

    def test_load_metadata_empty(self, temp_templates_dir):
        """Test loading metadata when file doesn't exist"""
        result = load_metadata()
        assert result == {"templates": []}

    def test_save_and_load_metadata(self, temp_templates_dir):
        """Test saving and loading metadata"""
        test_data = {
            "templates": [
                {"id": "test-1", "name": "Template 1"}
            ]
        }
        save_metadata(test_data)

        loaded = load_metadata()
        assert loaded == test_data

    def test_list_templates_empty(self, temp_templates_dir):
        """Test listing templates when none exist"""
        templates = list_templates()
        assert templates == []

    def test_list_templates_with_data(self, temp_templates_dir):
        """Test listing templates with existing data"""
        test_data = {
            "templates": [
                {"id": "1", "name": "Template 1"},
                {"id": "2", "name": "Template 2"}
            ]
        }
        save_metadata(test_data)

        templates = list_templates()
        assert len(templates) == 2
        assert templates[0]["name"] == "Template 1"

    def test_get_template_found(self, temp_templates_dir):
        """Test getting a template by ID"""
        test_data = {
            "templates": [
                {"id": "test-1", "name": "Template 1"},
                {"id": "test-2", "name": "Template 2"}
            ]
        }
        save_metadata(test_data)

        template = get_template("test-1")
        assert template is not None
        assert template["name"] == "Template 1"

    def test_get_template_not_found(self, temp_templates_dir):
        """Test getting a non-existent template"""
        template = get_template("non-existent")
        assert template is None

    def test_get_default_template_when_marked(self, temp_templates_dir):
        """Test getting default template when one is marked as default"""
        test_data = {
            "templates": [
                {"id": "1", "name": "Template 1", "is_default": False},
                {"id": "2", "name": "Template 2", "is_default": True}
            ]
        }
        save_metadata(test_data)

        default = get_default_template()
        assert default is not None
        assert default["id"] == "2"

    def test_get_default_template_returns_first(self, temp_templates_dir):
        """Test that first template is returned when no default is set"""
        test_data = {
            "templates": [
                {"id": "1", "name": "Template 1"},
                {"id": "2", "name": "Template 2"}
            ]
        }
        save_metadata(test_data)

        default = get_default_template()
        assert default is not None
        assert default["id"] == "1"

    def test_get_default_template_none(self, temp_templates_dir):
        """Test getting default template when none exist"""
        default = get_default_template()
        assert default is None

    def test_add_first_template(self, temp_templates_dir, sample_template_file):
        """Test adding the first template (should be default automatically)"""
        result = add_template(
            sample_template_file,
            "My Template",
            "1.0"
        )

        assert result["name"] == "My Template"
        assert result["version"] == "1.0"
        assert result["is_default"] is True
        assert "id" in result
        assert "uploaded_at" in result

        # Verify file was copied
        dest_file = Path(result["path"])
        assert dest_file.exists()

    def test_add_template_with_explicit_default(self, temp_templates_dir, sample_template_file):
        """Test adding a template and explicitly setting it as default"""
        # Add first template
        first = add_template(sample_template_file, "Template 1", "1.0")

        # Add second template as default
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            f.write("Second template")
            second_file = Path(f.name)

        try:
            second = add_template(second_file, "Template 2", "2.0", set_as_default=True)

            assert second["is_default"] is True

            # Verify first is no longer default
            templates = list_templates()
            first_template = next(t for t in templates if t["id"] == first["id"])
            assert first_template["is_default"] is False
        finally:
            if second_file.exists():
                second_file.unlink()

    def test_add_multiple_templates(self, temp_templates_dir, sample_template_file):
        """Test adding multiple templates"""
        result1 = add_template(sample_template_file, "Template 1", "1.0")
        result2 = add_template(sample_template_file, "Template 2", "2.0")

        templates = list_templates()
        assert len(templates) == 2
        assert result1["is_default"] is True
        assert result2["is_default"] is False

    def test_set_default_template_success(self, temp_templates_dir, sample_template_file):
        """Test setting a template as default"""
        template1 = add_template(sample_template_file, "Template 1", "1.0")
        template2 = add_template(sample_template_file, "Template 2", "2.0")

        # Set second template as default
        result = set_default_template(template2["id"])
        assert result is True

        # Verify changes
        templates = list_templates()
        t1 = next(t for t in templates if t["id"] == template1["id"])
        t2 = next(t for t in templates if t["id"] == template2["id"])

        assert t1["is_default"] is False
        assert t2["is_default"] is True

    def test_set_default_template_not_found(self, temp_templates_dir):
        """Test setting a non-existent template as default"""
        result = set_default_template("non-existent-id")
        assert result is False

    def test_delete_template_success(self, temp_templates_dir, sample_template_file):
        """Test deleting a template"""
        template1 = add_template(sample_template_file, "Template 1", "1.0")
        template2 = add_template(sample_template_file, "Template 2", "2.0")

        # Delete second template
        result = delete_template(template2["id"])
        assert result is True

        # Verify deletion
        templates = list_templates()
        assert len(templates) == 1
        assert templates[0]["id"] == template1["id"]

    def test_delete_template_not_found(self, temp_templates_dir):
        """Test deleting a non-existent template"""
        result = delete_template("non-existent-id")
        assert result is False

    def test_delete_last_template_fails(self, temp_templates_dir, sample_template_file):
        """Test that deleting the last template is prevented"""
        template = add_template(sample_template_file, "Last Template", "1.0")

        result = delete_template(template["id"])
        assert result is False

        # Verify template still exists
        templates = list_templates()
        assert len(templates) == 1

    def test_delete_default_template_reassigns(self, temp_templates_dir, sample_template_file):
        """Test that deleting default template reassigns default to first remaining"""
        template1 = add_template(sample_template_file, "Template 1", "1.0")
        template2 = add_template(sample_template_file, "Template 2", "2.0")
        template3 = add_template(sample_template_file, "Template 3", "3.0")

        # Template 1 is default, delete it
        result = delete_template(template1["id"])
        assert result is True

        # Verify template 2 is now default
        templates = list_templates()
        assert len(templates) == 2
        assert templates[0]["is_default"] is True

    def test_delete_template_removes_file(self, temp_templates_dir, sample_template_file):
        """Test that deleting a template removes the physical file"""
        template1 = add_template(sample_template_file, "Template 1", "1.0")
        template2 = add_template(sample_template_file, "Template 2", "2.0")

        file_path = Path(template2["path"])
        assert file_path.exists()

        delete_template(template2["id"])
        assert not file_path.exists()

    def test_add_template_copies_file(self, temp_templates_dir, sample_template_file):
        """Test that adding a template copies the file"""
        original_content = sample_template_file.read_text()

        result = add_template(sample_template_file, "Test Template", "1.0")

        # Verify file was copied with new name
        copied_file = Path(result["path"])
        assert copied_file.exists()
        assert copied_file != sample_template_file
        assert copied_file.read_text() == original_content

    def test_metadata_persistence(self, temp_templates_dir, sample_template_file):
        """Test that metadata persists across function calls"""
        # Add a template
        add_template(sample_template_file, "Template 1", "1.0")

        # Reload metadata
        metadata = load_metadata()
        assert len(metadata["templates"]) == 1

        # Add another template
        add_template(sample_template_file, "Template 2", "2.0")

        # Verify both are present
        metadata = load_metadata()
        assert len(metadata["templates"]) == 2
