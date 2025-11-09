#!/usr/bin/env python3
"""
Test the template with docxtpl to see what variables it finds.
"""

from pathlib import Path
from docxtpl import DocxTemplate

def test_template(template_path: Path):
    """Test what variables docxtpl can find in the template."""
    print(f"Loading template: {template_path}")

    try:
        doc = DocxTemplate(template_path)

        # Get the template's XML
        print("\n" + "="*60)
        print("Testing with sample data...")
        print("="*60)

        # Create test context with all expected variables
        test_context = {
            'supplier_serial_no': 'TEST-12345',
            'contract_number': '454545-TEST',
            'acquirer': 'Test Acquirer Name',
            'delivery_address': 'Test Delivery Address',
            'partial_delivery_number': '777577-TEST',
            'final_delivery_number': 'N/A',
            'contract_item': 'TEST-ITEM',
            'product_description': 'TEST PRODUCT',
            'quantity': '100',
            'shipment_no': '6SH264587-TEST',
            'undelivered_quantity': '1000(5000)-TEST',
            'remarks': 'SW Ver. # 27.27-TEST',
            'date': '09/Nov/2025',
            'job_id': 'test-job-id',
            'job_name': 'Test Job',
            'submitted_by': 'Test User'
        }

        print("\nTest context:")
        for key, value in test_context.items():
            print(f"  {key}: {value}")

        # Try to render
        output_path = Path("templates/TEST_OUTPUT.docx")
        print(f"\nRendering to: {output_path}")

        doc.render(test_context)
        doc.save(output_path)

        print("\n" + "="*60)
        print("SUCCESS! Template rendered.")
        print("="*60)
        print(f"\nOpen {output_path} and check if variables are filled.")
        print("\nIf variables are still empty, the template may have:")
        print("  1. Variables in text boxes (docxtpl doesn't support these)")
        print("  2. Variables with extra spaces: {{ variable }} vs {{variable}}")
        print("  3. Variables using different names than expected")

    except Exception as e:
        print(f"\nERROR rendering template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    template_path = Path("templates/COC_SV_Del165_20.03.2025.docx")

    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}")
        exit(1)

    test_template(template_path)
