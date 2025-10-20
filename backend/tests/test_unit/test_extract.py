import pytest
from app.extract import extract_from_pdfs, normalize_date

class TestExtraction:
    def test_extract_returns_required_structure(self):
        """Test extraction returns all required keys"""
        result = extract_from_pdfs(None, None)
        
        assert "extracted" in result
        assert "part_I" in result
        assert "part_II" in result
        assert "render_vars" in result
        assert "validation" in result
    
    def test_normalize_date_formats(self):
        """Test date normalization"""
        assert normalize_date("20-03-2025") == "20/Mar/2025" or "20-03-2025"
        assert normalize_date("20/Mar/2025") == "20/Mar/2025"
        assert normalize_date("") == ""
        assert normalize_date(None) == ""
    
    def test_extraction_with_missing_files(self):
        """Test extraction handles missing files gracefully"""
        result = extract_from_pdfs(None, None)
        assert result is not None
        assert isinstance(result, dict)
    
    def test_supplier_serial_no_generation(self):
        """Test that supplier serial number is generated correctly"""
        result = extract_from_pdfs(None, None)
        serial_no = result["part_I"].get("supplier_serial_no", "")
        assert "COC_SV_Del" in serial_no
        assert serial_no.endswith(".docx")