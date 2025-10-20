import pytest
import tempfile
from pathlib import Path
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock the problematic import
import unittest.mock as mock
sys.modules['pdfplumber'] = mock.MagicMock()

from fastapi.testclient import TestClient

@pytest.fixture
def client():
    """Create test client"""
    from app.main import app
    return TestClient(app)

@pytest.fixture
def sample_data():
    """Sample conversion data"""
    return {
        "part_I": {
            "supplier_serial_no": "COC_SV_Del165_20.03.2025.docx",
            "contract_number": "697.12.5011.01",
            "applicable_to": "6SH264587",
            "items": [{
                "contract_item": "1",
                "product_description_or_part": "20580903700; PNR-1000N WPTT",
                "quantity": 2,
                "shipment_document": "Packing Slip 6SH264587"
            }],
            "serials": ["NL13721", "NL13722"],
            "remarks": "SW Ver. # 2.2.15.45",
            "date": "20/Mar/2025"
        },
        "part_II": {
            "supplier_coc_serial_no": "COC_SV_Del165_20.03.2025.docx",
            "contract_number": "697.12.5011.01"
        },
        "validation": {"errors": [], "warnings": []}
    }