# tests/test_extraction.py
import pytest
from pathlib import Path
from app.extract import extract_from_pdfs, normalize_date

def test_extract_from_pdfs_structure():
    """Test that extract_from_pdfs returns the correct structure"""
    result = extract_from_pdfs(None, None)

    assert isinstance(result, dict)
    assert "extracted" in result
    assert "part_I" in result
    assert "part_II" in result
    assert "render_vars" in result
    assert "validation" in result

    assert "from_packing_slip" in result["extracted"]
    assert "from_company_coc" in result["extracted"]

def test_normalize_date():
    """Test date normalization"""
    assert normalize_date("20/Mar/2025") == "20/Mar/2025"
    assert normalize_date("") == ""
    assert normalize_date(None) == ""

def test_render_vars_structure():
    """Test render_vars contains expected keys"""
    result = extract_from_pdfs(None, None)
    render_vars = result["render_vars"]

    assert "docx_template" in render_vars
    assert "output_filename" in render_vars
    assert "date_format" in render_vars

def test_validation_structure():
    """Test validation structure is correct"""
    result = extract_from_pdfs(None, None)
    validation = result["validation"]

    assert "errors" in validation
    assert "warnings" in validation
    assert isinstance(validation["errors"], list)
    assert isinstance(validation["warnings"], list)