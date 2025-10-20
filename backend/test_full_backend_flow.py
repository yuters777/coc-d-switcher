# test_full_backend_flow.py
from app.extract import extract_from_pdfs
from app.render import render_docx

print("=== FULL BACKEND FLOW TEST ===\n")

# Step 1: Extract from PDFs
print("1. Extracting from PDFs...")
result = extract_from_pdfs("test_coc.pdf", "test_packing.pdf")

print(f"   Extracted {len(result['extracted_raw']['from_coc'])} COC fields")
print(f"   Extracted {len(result['extracted_raw']['from_packing_slip'])} Packing Slip fields")

# Step 2: Show template vars
print("\n2. Template variables ready:")
template_vars = result['template_vars']
for key, value in template_vars.items():
    if isinstance(value, str) and len(value) > 50:
        print(f"   {key}: {value[:50]}...")
    else:
        print(f"   {key}: {value}")

# Step 3: Simulate manual input
print("\n3. Adding manual input...")
template_vars['partial_delivery_number'] = "165"
template_vars['undelivered_quantity'] = "4196 (of 8115)"
template_vars['remarks'] = f"{template_vars['product_description']}'s SW Ver. # 2.2.15.45"

# Step 4: Render
print("\n4. Rendering DOCX...")
output_path = render_docx(template_vars, "test_job")
print(f"   ✓ Rendered: {output_path}")
print(f"   ✓ File exists: {output_path.exists()}")
print(f"   ✓ File size: {output_path.stat().st_size} bytes")

print("\n=== TEST COMPLETE ===")