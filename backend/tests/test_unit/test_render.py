# tests/test_unit/test_render.py
import pytest
from pathlib import Path
import json
import tempfile
from app.render import render_docx, convert_to_pdf, TEMPLATE_PATH


class TestRenderModule:
    """Test suite for render module"""

    def test_render_docx_creates_file(self):
        """Test that render_docx creates a file at the expected path"""
        conv_json = {
            "part_I": {
                "contract_number": "TEST123",
                "supplier_serial_no": "COC_SV_Del123_20.03.2025.docx"
            },
            "part_II": {}
        }
        job_id = "test-job-123"

        result_path = render_docx(conv_json, job_id)

        assert result_path.exists()
        assert result_path.name == f"coc-{job_id}.docx"
        assert result_path.parent == Path("/tmp")

        # Cleanup
        if result_path.exists():
            result_path.unlink()

    def test_render_docx_contains_data(self):
        """Test that render_docx writes the conversion data to the file"""
        conv_json = {
            "part_I": {
                "contract_number": "ABC456",
                "items": [{"quantity": 10}]
            }
        }
        job_id = "test-job-456"

        result_path = render_docx(conv_json, job_id)

        # Read and verify content
        content = json.loads(result_path.read_text())
        assert content["part_I"]["contract_number"] == "ABC456"
        assert content["part_I"]["items"][0]["quantity"] == 10

        # Cleanup
        if result_path.exists():
            result_path.unlink()

    def test_render_docx_with_empty_data(self):
        """Test render_docx with empty conversion data"""
        conv_json = {}
        job_id = "empty-job"

        result_path = render_docx(conv_json, job_id)

        assert result_path.exists()
        content = json.loads(result_path.read_text())
        assert content == {}

        # Cleanup
        if result_path.exists():
            result_path.unlink()

    def test_render_docx_with_complex_data(self):
        """Test render_docx with complex nested data"""
        conv_json = {
            "part_I": {
                "contract_number": "XYZ789",
                "items": [
                    {"quantity": 5, "description": "Item 1"},
                    {"quantity": 10, "description": "Item 2"}
                ],
                "serials": ["S001", "S002", "S003"]
            },
            "part_II": {
                "qa_manager": "John Doe",
                "signature": "QM.Test"
            },
            "render_vars": {
                "template": "test.docx",
                "date_format": "DD/MM/YYYY"
            }
        }
        job_id = "complex-job"

        result_path = render_docx(conv_json, job_id)

        assert result_path.exists()
        content = json.loads(result_path.read_text())
        assert content["part_I"]["contract_number"] == "XYZ789"
        assert len(content["part_I"]["items"]) == 2
        assert len(content["part_I"]["serials"]) == 3
        assert content["part_II"]["qa_manager"] == "John Doe"

        # Cleanup
        if result_path.exists():
            result_path.unlink()

    def test_convert_to_pdf_creates_file(self):
        """Test that convert_to_pdf creates a PDF file"""
        # Create a temporary docx file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            f.write("Test docx content")
            docx_path = Path(f.name)

        try:
            pdf_path = convert_to_pdf(docx_path)

            assert pdf_path.exists()
            assert pdf_path.suffix == ".pdf"
            assert pdf_path.stem == docx_path.stem

            # Cleanup
            if pdf_path.exists():
                pdf_path.unlink()
        finally:
            if docx_path.exists():
                docx_path.unlink()

    def test_convert_to_pdf_content(self):
        """Test that convert_to_pdf creates file with expected content"""
        # Create a temporary docx file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            f.write("Test docx content")
            docx_path = Path(f.name)

        try:
            pdf_path = convert_to_pdf(docx_path)

            content = pdf_path.read_text()
            assert "PDF version of" in content
            assert docx_path.name in content

            # Cleanup
            if pdf_path.exists():
                pdf_path.unlink()
        finally:
            if docx_path.exists():
                docx_path.unlink()

    def test_convert_to_pdf_preserves_location(self):
        """Test that PDF is created in the same directory as DOCX"""
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = Path(tmpdir) / "test.docx"
            docx_path.write_text("Test content")

            pdf_path = convert_to_pdf(docx_path)

            assert pdf_path.parent == docx_path.parent
            assert pdf_path.name == "test.pdf"

            # Cleanup happens automatically with tmpdir

    def test_template_path_environment_variable(self):
        """Test that TEMPLATE_PATH uses environment variable"""
        import os
        # The default should be from getenv
        assert TEMPLATE_PATH == os.getenv("TEMPLATE_PATH", "templates/COC_SV_Del165_20.03.2025.docx")

    def test_render_docx_different_job_ids(self):
        """Test that different job IDs produce different filenames"""
        conv_json = {"test": "data"}

        path1 = render_docx(conv_json, "job-001")
        path2 = render_docx(conv_json, "job-002")

        assert path1 != path2
        assert path1.name == "coc-job-001.docx"
        assert path2.name == "coc-job-002.docx"

        # Cleanup
        for path in [path1, path2]:
            if path.exists():
                path.unlink()

    def test_render_docx_overwrites_existing(self):
        """Test that render_docx overwrites existing files"""
        conv_json_1 = {"version": 1}
        conv_json_2 = {"version": 2}
        job_id = "overwrite-test"

        # Create first version
        path1 = render_docx(conv_json_1, job_id)
        content1 = json.loads(path1.read_text())
        assert content1["version"] == 1

        # Create second version (should overwrite)
        path2 = render_docx(conv_json_2, job_id)
        assert path1 == path2

        content2 = json.loads(path2.read_text())
        assert content2["version"] == 2

        # Cleanup
        if path2.exists():
            path2.unlink()
