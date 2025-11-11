#!/usr/bin/env python3
"""
Test script to verify PDF extraction functionality
"""
import sys
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.extract import extract_from_pdfs, extract_company_coc, extract_packing_slip
import json


def test_extraction(coc_path: str = None, ps_path: str = None):
    """Test the extraction with provided PDF files"""

    print("=" * 80)
    print("PDF EXTRACTION TEST")
    print("=" * 80)

    # Test individual extraction functions
    if coc_path and Path(coc_path).exists():
        print(f"\n📄 Testing Company COC: {coc_path}")
        print("-" * 80)
        coc_data = extract_company_coc(coc_path)
        print(json.dumps(coc_data, indent=2))
    else:
        print(f"\n⚠️  Company COC not found: {coc_path}")

    if ps_path and Path(ps_path).exists():
        print(f"\n📄 Testing Packing Slip: {ps_path}")
        print("-" * 80)
        ps_data = extract_packing_slip(ps_path)
        print(json.dumps(ps_data, indent=2))
    else:
        print(f"\n⚠️  Packing Slip not found: {ps_path}")

    # Test combined extraction
    if (coc_path and Path(coc_path).exists()) or (ps_path and Path(ps_path).exists()):
        print(f"\n📊 Testing Combined Extraction")
        print("-" * 80)
        result = extract_from_pdfs(coc_path, ps_path)

        print("\n✅ Extracted Data (from_company_coc):")
        print(json.dumps(result['extracted']['from_company_coc'], indent=2))

        print("\n✅ Extracted Data (from_packing_slip):")
        print(json.dumps(result['extracted']['from_packing_slip'], indent=2))

        print("\n✅ Merged Part I Data:")
        print(json.dumps(result['part_I'], indent=2))

        # Verify expected data
        print("\n" + "=" * 80)
        print("VERIFICATION")
        print("=" * 80)

        part_i = result['part_I']
        checks = [
            ("Contract Number", part_i.get('contract_number')),
            ("Shipment Number", part_i.get('shipment_no')),
            ("Product Description", part_i.get('product_description')),
            ("Quantity", part_i.get('quantity')),
            ("Serial Count", part_i.get('serial_count')),
        ]

        for field, value in checks:
            status = "✅" if value else "❌"
            print(f"{status} {field}: {value}")

        if part_i.get('serials'):
            print(f"\n📋 Serial Numbers (first 10):")
            for serial in part_i['serials'][:10]:
                print(f"   - {serial}")
            if len(part_i['serials']) > 10:
                print(f"   ... and {len(part_i['serials']) - 10} more")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    # Default test files (adjust paths as needed)
    coc_file = "test_files/COC_6SH264587.pdf"
    ps_file = "test_files/PackingSlip.pdf"

    # Check command line arguments
    if len(sys.argv) > 1:
        coc_file = sys.argv[1]
    if len(sys.argv) > 2:
        ps_file = sys.argv[2]

    print(f"\nUsage: python test_extraction.py [coc_pdf_path] [packing_slip_pdf_path]")
    print(f"\nTesting with:")
    print(f"  COC: {coc_file}")
    print(f"  PS:  {ps_file}")

    test_extraction(coc_file, ps_file)
