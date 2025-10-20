# backend/scripts/verify_template.py
from docxtpl import DocxTemplate
from pathlib import Path

def verify_template():
    template_path = Path(__file__).parent.parent / "templates" / "dutch_coc_template.docx"
    
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}")
        return
    
    try:
        doc = DocxTemplate(str(template_path))
        
        context = {
            'supplier_serial_no': 'COC_SV_Del165_20.03.2025',
            'contract_number': '697.12.5011.01',
            'acquirer': 'NETHERLANDS MINISTRY OF DEFENCE\nCOMMIT\nProjects Procurement Division',
            'delivery_address': 'BCD\nCamp New Amsterdam\nDolderseweg 34',
            'partial_delivery_number': '165',
            'final_delivery_number': 'N/A',
            'contract_item': '20000646041',
            'product_description': 'PNR-1000N WPTT',
            'quantity': '100',
            'shipment_no': '6SH264587',
            'undelivered_quantity': '4196 (of 8115)',
            'remarks': 'SW Ver. # 2.2.15.45',
            'serial_count': '100',
            'serials_list': 'NL13721, NL13722, NL13769...'
        }
        
        doc.render(context)
        
        output_path = Path(__file__).parent / "test_output.docx"
        doc.save(str(output_path))
        
        print(f"✓ Template validation successful!")
        print(f"✓ Test output: {output_path}")
        
    except Exception as e:
        print(f"✗ Template validation FAILED: {e}")

if __name__ == "__main__":
    verify_template()