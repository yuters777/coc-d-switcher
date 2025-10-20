import pytest
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

def test_validate_function():
    """Test validation without importing main app"""
    from app.validate import validate_conversion
    
    test_data = {
        "part_I": {
            "items": [{"quantity": 2}],
            "serials": ["NL001", "NL002"],
            "contract_number": "123"
        }
    }
    
    result = validate_conversion(test_data)
    assert "errors" in result
    assert "warnings" in result
    assert len(result["errors"]) == 0  # Should pass

def test_config_loading():
    """Test config can be loaded"""
    from app.config import load_config
    config = load_config()
    assert "supplier_block" in config
    assert "delivery_id" in config

def test_validation_error():
    """Test validation catches serial mismatch"""
    from app.validate import validate_conversion
    
    test_data = {
        "part_I": {
            "items": [{"quantity": 2}],
            "serials": ["NL001", "NL002", "NL003"],  # 3 serials but quantity is 2
            "contract_number": "123"
        }
    }
    
    result = validate_conversion(test_data)
    assert len(result["errors"]) > 0
    assert any("SERIAL_COUNT_MISMATCH" in e["code"] for e in result["errors"])