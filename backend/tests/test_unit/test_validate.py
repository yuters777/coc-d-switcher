import pytest
from app.validate import validate_conversion

class TestValidation:
    def test_serial_count_matches_quantity(self):
        """Test validation passes when serial count matches quantity"""
        data = {
            "part_I": {
                "items": [{"quantity": 2}],
                "serials": ["NL001", "NL002"],
                "contract_number": "TEST123"  # Fixed: Added contract number
            }
        }
        result = validate_conversion(data)
        assert len(result["errors"]) == 0
    
    def test_serial_count_mismatch(self):
        """Test validation fails when serial count doesn't match quantity"""
        data = {
            "part_I": {
                "items": [{"quantity": 2}],
                "serials": ["NL001", "NL002", "NL003"],
                "contract_number": "TEST123"
            }
        }
        result = validate_conversion(data)
        errors = result["errors"]
        assert len(errors) > 0
        assert any("SERIAL_COUNT_MISMATCH" in e["code"] for e in errors)
    
    def test_missing_contract_number(self):
        """Test validation fails when contract number is missing"""
        data = {
            "part_I": {
                "contract_number": "",
                "items": [{"quantity": 1}],
                "serials": ["NL001"]
            }
        }
        result = validate_conversion(data)
        errors = result["errors"]
        assert any("MISSING_CONTRACT" in e["code"] for e in errors)
    
    def test_empty_data(self):
        """Test validation handles empty data gracefully"""
        result = validate_conversion({})
        assert "errors" in result
        assert "warnings" in result
    
    def test_missing_serials(self):
        """Test validation when serials are missing"""
        data = {
            "part_I": {
                "items": [{"quantity": 5}],
                "serials": [],
                "contract_number": "TEST123"
            }
        }
        result = validate_conversion(data)
        errors = result["errors"]
        assert len(errors) > 0
        assert any("SERIAL_COUNT_MISMATCH" in e["code"] for e in errors)
    
    def test_zero_quantity_with_serials(self):
        """Test validation when quantity is 0 but serials exist"""
        data = {
            "part_I": {
                "items": [{"quantity": 0}],
                "serials": ["NL001", "NL002"],
                "contract_number": "TEST123"
            }
        }
        result = validate_conversion(data)
        errors = result["errors"]
        assert len(errors) > 0
        assert any("SERIAL_COUNT_MISMATCH" in e["code"] for e in errors)
    
    def test_multiple_items_validation(self):
        """Test validation with multiple items (takes first item's quantity)"""
        data = {
            "part_I": {
                "items": [
                    {"quantity": 3},
                    {"quantity": 5}
                ],
                "serials": ["NL001", "NL002", "NL003"],
                "contract_number": "TEST123"
            }
        }
        result = validate_conversion(data)
        # Should validate against first item's quantity (3)
        assert len(result["errors"]) == 0
    
    def test_no_items_array(self):
        """Test validation when items array is missing"""
        data = {
            "part_I": {
                "serials": ["NL001", "NL002"],
                "contract_number": "TEST123"
            }
        }
        result = validate_conversion(data)
        # Should handle gracefully
        assert "errors" in result
        assert "warnings" in result
    
    def test_malformed_data_structure(self):
        """Test validation with malformed data"""
        data = {
            "part_I": None
        }
        result = validate_conversion(data)
        assert "errors" in result
        assert "warnings" in result
        
    def test_validation_with_all_fields_correct(self):
        """Test validation passes with complete valid data"""
        data = {
            "part_I": {
                "contract_number": "697.12.5011.01",
                "items": [{"quantity": 100}],
                "serials": ["NL" + str(i).zfill(5) for i in range(1, 101)],  # 100 serials
                "applicable_to": "6SH264587",
                "remarks": "Test remarks"
            }
        }
        result = validate_conversion(data)
        assert len(result["errors"]) == 0
        assert isinstance(result["warnings"], list)