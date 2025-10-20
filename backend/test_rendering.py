# tests/test_rendering.py
import pytest
from pathlib import Path
from app.render import prepare_context, render_docx

def test_context_preparation():
    """Test rendering context has all variables"""
    template_vars = {
        "supplier_serial_no": "COC_SV_Del587_20.03.2025.docx",
        "contract_number": "697.12.5011.01",
        "quantity": 100
    }
    
    context = prepare_context(template_vars)
    
    # Check all 13 required variables exist
    required = [
        "supplier_serial_no", "contract_number", "acquirer",
        "delivery_address", "partial_delivery_number", 
        "final_delivery_number", "contract_item",
        "product_description", "quantity", "shipment_no",
        "undelivered_quantity", "remarks", "date"
    ]
    
    for var in required:
        assert var in context

def test_final_delivery_default():
    """Test final_delivery_number defaults to N/A"""
    context = prepare_context({})
    assert context["final_delivery_number"] == "N/A"