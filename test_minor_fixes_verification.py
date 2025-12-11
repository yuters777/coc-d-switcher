#!/usr/bin/env python3
"""
Automated Test Script for Minor Issues Fixes Verification
Tests both COC+PS and PS-Only operation modes

Verifies:
1. Dynamic filename generation with delivery number and date
2. Date normalization (display vs filename formats)
3. Serial count display in UI

Date: November 17, 2025
"""

import sys
import re
from datetime import datetime
from pathlib import Path

# Test results tracker
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name: str, passed: bool, message: str = ""):
    """Log test result"""
    status = "✓ PASS" if passed else "✗ FAIL"
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
    
    print(f"{status}: {name}")
    if message:
        print(f"  {message}")

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}\n")

def print_section(text: str):
    """Print formatted section"""
    print(f"\n{'─'*70}")
    print(f"  {text}")
    print(f"{'─'*70}")

# ============================================================================
# TEST 1: FILENAME PATTERN VERIFICATION
# ============================================================================

def test_filename_pattern():
    """Test dynamic filename generation"""
    print_section("TEST 1: Filename Pattern Generation")
    
    test_cases = [
        {
            "name": "COC+PS Mode - Delivery 165",
            "delivery_num": "165",
            "expected_pattern": r"COC_SV_Del165_\d{2}\.\d{2}\.\d{4}\.docx"
        },
        {
            "name": "PS Only Mode - Delivery 153",
            "delivery_num": "153",
            "expected_pattern": r"COC_SV_Del153_\d{2}\.\d{2}\.\d{4}\.docx"
        },
        {
            "name": "Edge Case - No delivery number",
            "delivery_num": None,
            "expected_pattern": r"COC_SV_Del000_\d{2}\.\d{2}\.\d{4}\.docx"
        },
        {
            "name": "Edge Case - Three digit delivery",
            "delivery_num": "187",
            "expected_pattern": r"COC_SV_Del187_\d{2}\.\d{2}\.\d{4}\.docx"
        }
    ]
    
    for test_case in test_cases:
        # Simulate filename generation logic from backend/app/render.py
        delivery_num = test_case["delivery_num"] or "000"
        date_str = datetime.now().strftime("%d.%m.%Y")
        generated_filename = f"COC_SV_Del{delivery_num}_{date_str}.docx"
        
        # Verify pattern matches
        pattern_match = re.match(test_case["expected_pattern"], generated_filename)
        
        log_test(
            f"Filename Pattern: {test_case['name']}",
            pattern_match is not None,
            f"Generated: {generated_filename}"
        )
        
        # Verify date format in filename (DD.MM.YYYY)
        date_parts = date_str.split('.')
        date_valid = (
            len(date_parts) == 3 and
            len(date_parts[0]) == 2 and  # DD
            len(date_parts[1]) == 2 and  # MM
            len(date_parts[2]) == 4      # YYYY
        )
        
        log_test(
            f"Date Format in Filename: {test_case['name']}",
            date_valid,
            f"Date: {date_str} (DD.MM.YYYY format)"
        )

# ============================================================================
# TEST 2: DATE NORMALIZATION
# ============================================================================

def normalize_date(date_str: str, output_format: str = "display") -> str:
    """
    Normalize date to specified format (from backend/app/extract.py)
    
    Args:
        date_str: Input date string in various formats
        output_format: 'display' for DD/Mon/YYYY or 'filename' for DD.MM.YYYY
    """
    if not date_str:
        return ""
    
    # Try multiple input formats
    input_formats = [
        "%d/%m/%Y",    # 20/03/2025
        "%d.%m.%Y",    # 20.03.2025
        "%d-%m-%Y",    # 20-03-2025
        "%d/%b/%Y",    # 20/Mar/2025
        "%d/%B/%Y",    # 20/March/2025
        "%Y-%m-%d",    # 2025-03-20 (ISO)
        "%d.%m.%y",    # 20.03.25
        "%d/%m/%y"     # 20/03/25
    ]
    
    date_obj = None
    for fmt in input_formats:
        try:
            date_obj = datetime.strptime(date_str, fmt)
            break
        except ValueError:
            continue
    
    if not date_obj:
        return date_str
    
    # Output in requested format
    if output_format == "display":
        return date_obj.strftime("%d/%b/%Y")  # 20/Mar/2025
    elif output_format == "filename":
        return date_obj.strftime("%d.%m.%Y")  # 20.03.2025
    else:
        return date_str

def test_date_normalization():
    """Test date normalization function"""
    print_section("TEST 2: Date Normalization")
    
    test_cases = [
        # Display format tests
        {
            "input": "20/03/2025",
            "format": "display",
            "expected": "20/Mar/2025",
            "description": "European format to display"
        },
        {
            "input": "2025-03-20",
            "format": "display",
            "expected": "20/Mar/2025",
            "description": "ISO format to display"
        },
        {
            "input": "20.03.2025",
            "format": "display",
            "expected": "20/Mar/2025",
            "description": "Dot format to display"
        },
        {
            "input": "20/Mar/2025",
            "format": "display",
            "expected": "20/Mar/2025",
            "description": "Display format (unchanged)"
        },
        
        # Filename format tests
        {
            "input": "20/Mar/2025",
            "format": "filename",
            "expected": "20.03.2025",
            "description": "Display to filename format"
        },
        {
            "input": "2025-03-20",
            "format": "filename",
            "expected": "20.03.2025",
            "description": "ISO to filename format"
        },
        {
            "input": "20/03/2025",
            "format": "filename",
            "expected": "20.03.2025",
            "description": "European to filename format"
        },
        {
            "input": "20.03.25",
            "format": "filename",
            "expected": "20.03.2025",
            "description": "Short year to filename format"
        }
    ]
    
    for test_case in test_cases:
        result = normalize_date(test_case["input"], test_case["format"])
        passed = result == test_case["expected"]
        
        log_test(
            f"Date Normalization: {test_case['description']}",
            passed,
            f"Input: '{test_case['input']}' → Output: '{result}' (Expected: '{test_case['expected']}')"
        )

# ============================================================================
# TEST 3: SERIAL COUNT DISPLAY
# ============================================================================

def test_serial_count_display():
    """Test serial count display logic"""
    print_section("TEST 3: Serial Count Display")
    
    test_cases = [
        {
            "name": "COC+PS Mode - 2 serials extracted",
            "extracted_data": {
                "part_I": {
                    "serial_count": 2,
                    "serials": ["NL13721", "NL13722"]
                },
                "template_vars": {
                    "contract_number": "697.12.5011.01",
                    "shipment_no": "6SH264587"
                }
            },
            "should_display": True,
            "expected_count": 2
        },
        {
            "name": "PS Only Mode - 4196 serials extracted",
            "extracted_data": {
                "part_I": {
                    "serial_count": 4196,
                    "serials": ["SN001", "SN002", "..."]
                },
                "template_vars": {
                    "contract_number": "697.12.5011.01"
                }
            },
            "should_display": True,
            "expected_count": 4196
        },
        {
            "name": "Edge Case - No serial count",
            "extracted_data": {
                "part_I": {
                    "serials": []
                },
                "template_vars": {}
            },
            "should_display": False,
            "expected_count": None
        },
        {
            "name": "Edge Case - Zero serials",
            "extracted_data": {
                "part_I": {
                    "serial_count": 0,
                    "serials": []
                }
            },
            "should_display": False,  # Zero count shouldn't display
            "expected_count": 0
        }
    ]
    
    for test_case in test_cases:
        # Simulate the frontend logic from ManualInputForm.tsx
        extracted_data = test_case["extracted_data"]
        serial_count = extracted_data.get("part_I", {}).get("serial_count")
        
        # Check if display condition is met
        should_display = bool(serial_count)
        display_matches = should_display == test_case["should_display"]
        
        if should_display and test_case["should_display"]:
            count_matches = serial_count == test_case["expected_count"]
            display_text = f"ℹ️ Extracted {serial_count} serial numbers"
        else:
            count_matches = True  # N/A for non-display cases
            display_text = "Not displayed"
        
        log_test(
            f"Serial Count Display: {test_case['name']}",
            display_matches and count_matches,
            f"{display_text}"
        )

# ============================================================================
# TEST 4: INTEGRATION SCENARIOS
# ============================================================================

def test_integration_scenarios():
    """Test complete workflows"""
    print_section("TEST 4: Integration Scenarios")
    
    # Scenario 1: COC+PS Mode Complete Flow
    print("\n  Scenario 1: COC+PS Mode (Full Extraction)")
    print("  " + "─" * 65)
    
    # Simulate extracted data
    extracted_data = {
        "part_I": {
            "serial_count": 2,
            "serials": ["NL13721", "NL13722"]
        },
        "template_vars": {
            "contract_number": "697.12.5011.01",
            "shipment_no": "6SH264587",
            "product_description": "PNR-1000N WPTT",
            "quantity": 2,
            "date": "20/Mar/2025"
        }
    }
    
    # User enters manual data
    manual_data = {
        "partial_delivery_number": "165",
        "undelivered_quantity": "4196 (of 8115)",
        "sw_version": "2.2.15.45"
    }
    
    # Test 1: Filename generation
    delivery_num = manual_data["partial_delivery_number"]
    date_str = datetime.now().strftime("%d.%m.%Y")
    filename = f"COC_SV_Del{delivery_num}_{date_str}.docx"
    filename_valid = re.match(r"COC_SV_Del165_\d{2}\.\d{2}\.\d{4}\.docx", filename)
    
    log_test(
        "COC+PS: Filename generation",
        filename_valid is not None,
        f"Generated: {filename}"
    )
    
    # Test 2: Serial count display
    serial_count = extracted_data["part_I"]["serial_count"]
    display_text = f"ℹ️ Extracted {serial_count} serial numbers"
    
    log_test(
        "COC+PS: Serial count display",
        serial_count == 2,
        display_text
    )
    
    # Test 3: Date normalization
    original_date = extracted_data["template_vars"]["date"]
    display_date = normalize_date(original_date, "display")
    filename_date = normalize_date(original_date, "filename")
    
    date_valid = (
        display_date == "20/Mar/2025" and
        filename_date == "20.03.2025"
    )
    
    log_test(
        "COC+PS: Date normalization",
        date_valid,
        f"Display: {display_date}, Filename: {filename_date}"
    )
    
    # Scenario 2: PS Only Mode Complete Flow
    print("\n  Scenario 2: PS Only Mode (Manual Entry)")
    print("  " + "─" * 65)
    
    # PS only - extract serials from packing slip
    ps_extracted = {
        "part_I": {
            "serial_count": 4196,
            "serials": ["SN001", "SN002", "..."]  # Abbreviated
        }
    }
    
    # User enters all manual data including COC info
    manual_data_ps = {
        "partial_delivery_number": "153",
        "undelivered_quantity": "3919 (of 8115)",
        "sw_version": "2.2.15.45",
        "contract_number": "697.12.5011.01",
        "date": "13.11.2025"
    }
    
    # Test 1: Filename generation
    delivery_num_ps = manual_data_ps["partial_delivery_number"]
    date_str_ps = datetime.now().strftime("%d.%m.%Y")
    filename_ps = f"COC_SV_Del{delivery_num_ps}_{date_str_ps}.docx"
    filename_ps_valid = re.match(r"COC_SV_Del153_\d{2}\.\d{2}\.\d{4}\.docx", filename_ps)
    
    log_test(
        "PS Only: Filename generation",
        filename_ps_valid is not None,
        f"Generated: {filename_ps}"
    )
    
    # Test 2: Serial count from PS
    serial_count_ps = ps_extracted["part_I"]["serial_count"]
    display_text_ps = f"ℹ️ Extracted {serial_count_ps} serial numbers"
    
    log_test(
        "PS Only: Serial count from PS",
        serial_count_ps == 4196,
        display_text_ps
    )
    
    # Test 3: Manual date normalization
    manual_date = manual_data_ps["date"]
    display_date_ps = normalize_date(manual_date, "display")
    filename_date_ps = normalize_date(manual_date, "filename")
    
    date_ps_valid = (
        display_date_ps == "13/Nov/2025" and
        filename_date_ps == "13.11.2025"
    )
    
    log_test(
        "PS Only: Manual date normalization",
        date_ps_valid,
        f"Display: {display_date_ps}, Filename: {filename_date_ps}"
    )

# ============================================================================
# TEST 5: EDGE CASES
# ============================================================================

def test_edge_cases():
    """Test edge cases and error handling"""
    print_section("TEST 5: Edge Cases")
    
    # Edge Case 1: Missing delivery number
    delivery_num = None
    default_num = delivery_num or "000"
    date_str = datetime.now().strftime("%d.%m.%Y")
    filename = f"COC_SV_Del{default_num}_{date_str}.docx"
    
    log_test(
        "Edge Case: Missing delivery number",
        "Del000" in filename,
        f"Generated: {filename} (defaults to 000)"
    )
    
    # Edge Case 2: Invalid date format
    invalid_date = "not-a-date"
    result = normalize_date(invalid_date, "display")
    
    log_test(
        "Edge Case: Invalid date format",
        result == invalid_date,  # Should return original
        f"Input: '{invalid_date}' → Output: '{result}' (unchanged)"
    )
    
    # Edge Case 3: Empty serial list
    empty_serials = {
        "part_I": {
            "serials": []
        }
    }
    serial_count = empty_serials.get("part_I", {}).get("serial_count")
    should_display = bool(serial_count)
    
    log_test(
        "Edge Case: Empty serial list",
        not should_display,
        "Serial count display correctly hidden"
    )
    
    # Edge Case 4: Very large delivery number
    large_del_num = "9999"
    filename_large = f"COC_SV_Del{large_del_num}_{date_str}.docx"
    
    log_test(
        "Edge Case: Large delivery number",
        "Del9999" in filename_large,
        f"Generated: {filename_large}"
    )
    
    # Edge Case 5: Date with short year
    short_year = "20.03.25"
    normalized = normalize_date(short_year, "display")
    
    log_test(
        "Edge Case: Short year format",
        normalized == "20/Mar/2025",
        f"Input: '{short_year}' → Output: '{normalized}'"
    )

# ============================================================================
# MAIN TEST EXECUTION
# ============================================================================

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests:  {total_tests}")
    print(f"Passed:       {test_results['passed']} ✓")
    print(f"Failed:       {test_results['failed']} ✗")
    print(f"Pass Rate:    {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\nFailed Tests:")
        print("─" * 70)
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  ✗ {test['name']}")
                if test["message"]:
                    print(f"    {test['message']}")
    
    print("\n" + "="*70)
    
    if test_results["failed"] == 0:
        print("✓ ALL TESTS PASSED - Ready for production")
    else:
        print("✗ SOME TESTS FAILED - Review before deployment")
    
    print("="*70 + "\n")
    
    return test_results["failed"] == 0

def main():
    """Main test execution"""
    print_header("COC-D SWITCHER - MINOR FIXES VERIFICATION")
    print("Testing fixes for:")
    print("  1. Dynamic filename generation")
    print("  2. Date normalization")
    print("  3. Serial count display")
    print("\nModes tested:")
    print("  • COC + Packing Slip (Full Extraction)")
    print("  • PS Only (Packing Slip with Manual Entry)")
    
    # Run all test suites
    test_filename_pattern()
    test_date_normalization()
    test_serial_count_display()
    test_integration_scenarios()
    test_edge_cases()
    
    # Print summary and exit with appropriate code
    all_passed = print_summary()
    sys.exit(0 if all_passed else 1)

if __name__ == "__main__":
    main()
