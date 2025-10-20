"""Test PDF extraction with real files"""
from app.extract import extract_from_pdfs
from pathlib import Path
import json
import sys

def test_extraction():
    """Test extraction with actual PDF files"""
    
    # Check if files exist
    coc_path = "test_coc.pdf"
    packing_path = "test_packing.pdf"
    
    if not Path(coc_path).exists():
        print(f"ERROR: {coc_path} not found")
        print("Place your test PDFs in the backend directory and name them:")
        print("  - test_coc.pdf (Company COC)")
        print("  - test_packing.pdf (Packing Slip)")
        sys.exit(1)
    
    if not Path(packing_path).exists():
        print(f"WARNING: {packing_path} not found, continuing with COC only")
        packing_path = None
    
    print("=" * 70)
    print("PDF EXTRACTION TEST")
    print("=" * 70)
    
    # Extract data
    result = extract_from_pdfs(coc_path, packing_path)
    
    # Section 1: Raw extracted data
    print("\n1. RAW EXTRACTED DATA")
    print("-" * 70)
    
    print("\n  From Company COC:")
    coc_data = result["extracted_raw"]["from_coc"]
    for key, value in coc_data.items():
        if key == "serials":
            print(f"    {key}: {len(value)} serials found")
        elif isinstance(value, str) and len(value) > 50:
            print(f"    {key}: {value[:50]}...")
        else:
            print(f"    {key}: {value}")
    
    if packing_path:
        print("\n  From Packing Slip:")
        packing_data = result["extracted_raw"]["from_packing_slip"]
        for key, value in packing_data.items():
            if isinstance(value, str) and len(value) > 50:
                print(f"    {key}: {value[:50]}...")
            else:
                print(f"    {key}: {value}")
    
    # Section 2: Template variables (ready for rendering)
    print("\n\n2. TEMPLATE VARIABLES (13 total)")
    print("-" * 70)
    
    template_vars = result["template_vars"]
    
    # Group by type
    calculated = ["supplier_serial_no", "partial_delivery_number", "final_delivery_number"]
    from_coc = ["contract_number", "contract_item", "product_description", 
                "quantity", "shipment_no", "date", "acquirer"]
    from_packing = ["delivery_address"]
    manual = ["undelivered_quantity", "remarks"]
    
    print("\n  Calculated:")
    for var in calculated:
        value = template_vars.get(var, "")
        print(f"    {var}: {value}")
    
    print("\n  From COC:")
    for var in from_coc:
        value = template_vars.get(var, "")
        if isinstance(value, str) and len(value) > 60:
            print(f"    {var}: {value[:60]}...")
        else:
            print(f"    {var}: {value}")
    
    print("\n  From Packing Slip:")
    for var in from_packing:
        value = template_vars.get(var, "")
        if isinstance(value, str) and len(value) > 60:
            print(f"    {var}: {value[:60]}...")
        else:
            print(f"    {var}: {value}")
    
    print("\n  Manual Input Required:")
    for var in manual:
        value = template_vars.get(var, "")
        status = "EMPTY - needs user input" if not value else value
        print(f"    {var}: {status}")
    
    # Section 3: Validation results
    print("\n\n3. VALIDATION RESULTS")
    print("-" * 70)
    
    validation = result["validation"]
    
    print(f"\n  Errors: {len(validation['errors'])}")
    if validation['errors']:
        for error in validation['errors']:
            print(f"    ❌ {error['code']}")
            print(f"       {error['message']}")
            print(f"       Location: {error['where']}")
    else:
        print("    ✓ No errors")
    
    print(f"\n  Warnings: {len(validation['warnings'])}")
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"    ⚠ {warning['code']}")
            print(f"       {warning['message']}")
            print(f"       Location: {warning['where']}")
    else:
        print("    ✓ No warnings")
    
    # Section 4: Summary
    print("\n\n4. EXTRACTION SUMMARY")
    print("-" * 70)
    
    print(f"  Contract Number: {template_vars.get('contract_number', 'MISSING')}")
    print(f"  Shipment Number: {template_vars.get('shipment_no', 'MISSING')}")
    print(f"  Product: {template_vars.get('product_description', 'MISSING')}")
    print(f"  Quantity: {template_vars.get('quantity', 'MISSING')}")
    print(f"  Supplier Serial No: {template_vars.get('supplier_serial_no', 'MISSING')}")
    
    serials_count = len(coc_data.get('serials', []))
    expected_qty = template_vars.get('quantity', 0)
    serial_match = "✓" if serials_count == expected_qty else "✗"
    print(f"  Serials: {serials_count} {serial_match} (expected: {expected_qty})")
    
    # Section 5: Ready for rendering check
    print("\n\n5. READY FOR RENDERING?")
    print("-" * 70)
    
    blocking_errors = [e for e in validation['errors'] if e['code'].startswith('MISSING_')]
    manual_warnings = [w for w in validation['warnings'] if 'REQUIRED' in w['code']]
    
    if blocking_errors:
        print("  ✗ NO - Missing required fields")
        for error in blocking_errors:
            print(f"    - {error['where']}")
    elif manual_warnings:
        print("  ⚠ PARTIAL - Waiting for manual input:")
        for warning in manual_warnings:
            print(f"    - {warning['where']}")
    else:
        print("  ✓ YES - All data ready")
    
    print("\n" + "=" * 70)
    
    # Save full output to JSON for inspection
    output_file = "extraction_result.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nFull extraction result saved to: {output_file}")
    
    return result

if __name__ == "__main__":
    test_extraction()