# tests/test_extraction.py
import pytest
from pathlib import Path
from app.extract import (
    extract_from_company_coc, 
    extract_from_packing_slip,
    map_to_template_vars,
    normalize_date_to_ddmmyyyy
)

def test_date_normalization():
    """Test date format conversion"""
    assert normalize_date_to_ddmmyyyy("20/Mar/2025") == "20.03.2025"
    assert normalize_date_to_ddmmyyyy("20-03-2025") == "20.03.2025"
    assert normalize_date_to_ddmmyyyy("") == ""

def test_supplier_serial_calculation():
    """Test supplier serial number generation"""
    coc_data = {
        "shipment_no": "6SH264587",
        "date": "20/Mar/2025"
    }
    packing_data = {}
    
    result = map_to_template_vars(coc_data, packing_data)
    
    assert result["supplier_serial_no"] == "COC_SV_Del587_20.03.2025.docx"

def test_template_vars_mapping():
    """Test complete variable mapping"""
    coc_data = {
        "order": "697.12.5011.01",
        "customer_part_no": "20000646041",
        "product_name": "PNR-1000N WPTT",
        "quantity": 100,
        "shipment_no": "6SH264587",
        "date": "20/Mar/2025",
        "acquirer": "NETHERLANDS MINISTRY OF DEFENCE",
        "serials": ["NL13721", "NL13722"]
    }
    
    packing_data = {
        "delivery_address": "BCD\nCamp New Amsterdam"
    }
    
    vars = map_to_template_vars(coc_data, packing_data)
    
    assert vars["contract_number"] == "697.12.5011.01"
    assert vars["contract_item"] == "20000646041"
    assert vars["quantity"] == 100
    assert vars["final_delivery_number"] == "N/A"
    assert "PNR-1000N" in vars["product_description"]

def test_validation_missing_fields():
    """Test validation catches missing required fields"""
    from app.extract import validate_extracted_data
    
    incomplete_vars = {
        "supplier_serial_no": "COC_SV_Del587_20.03.2025.docx",
        "contract_number": "",  # Missing
        "quantity": 0
    }
    
    validation = validate_extracted_data(incomplete_vars)
    
    assert len(validation["errors"]) > 0
    error_codes = [e["code"] for e in validation["errors"]]
    assert "MISSING_CONTRACT_NUMBER" in error_codes