from pathlib import Path
from typing import Dict, Any
import json
import os
import tempfile
from datetime import datetime

TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "templates/COC_SV_Del165_20.03.2025.docx")

def prepare_context(template_vars: Dict[str, Any]) -> Dict[str, Any]:
    """Prepare rendering context with all required variables"""
    context = {
        "supplier_serial_no": template_vars.get("supplier_serial_no", ""),
        "contract_number": template_vars.get("contract_number", ""),
        "acquirer": template_vars.get("acquirer", ""),
        "delivery_address": template_vars.get("delivery_address", ""),
        "partial_delivery_number": template_vars.get("partial_delivery_number", ""),
        "final_delivery_number": template_vars.get("final_delivery_number", "N/A"),
        "contract_item": template_vars.get("contract_item", ""),
        "product_description": template_vars.get("product_description", ""),
        "quantity": template_vars.get("quantity", ""),
        "shipment_no": template_vars.get("shipment_no", ""),
        "undelivered_quantity": template_vars.get("undelivered_quantity", ""),
        "remarks": template_vars.get("remarks", ""),
        "date": template_vars.get("date", datetime.now().strftime("%d.%m.%Y"))
    }
    return context

def render_docx(conv_json: Dict[str, Any], job_id: str) -> Path:
    """Render DOCX from conversion data

    Args:
        conv_json: Conversion data including template_vars and manual_data
        job_id: Job identifier

    Returns:
        Path to rendered DOCX file with pattern: COC_SV_Del{DeliveryID}_{DD.MM.YYYY}.docx
    """
    # Extract delivery number from manual data or template vars
    delivery_num = "000"
    if "manual_data" in conv_json:
        delivery_num = conv_json["manual_data"].get("partial_delivery_number", "000")
    elif "template_vars" in conv_json:
        delivery_num = conv_json["template_vars"].get("partial_delivery_number", "000")
    elif "partial_delivery_number" in conv_json:
        delivery_num = conv_json.get("partial_delivery_number", "000")

    # Generate filename with current date in DD.MM.YYYY format
    date_str = datetime.now().strftime("%d.%m.%Y")
    filename = f"COC_SV_Del{delivery_num}_{date_str}.docx"

    # Use cross-platform temporary directory
    temp_dir = Path(tempfile.gettempdir())
    out_path = temp_dir / filename

    # In production, use docxtpl with actual template
    # For now, create placeholder
    with open(out_path, 'w') as f:
        json.dump(conv_json, f, indent=2)

    return out_path

def convert_to_pdf(docx_path: Path) -> Path:
    """Convert DOCX to PDF"""
    pdf_path = docx_path.with_suffix(".pdf")

    # In production, use LibreOffice headless conversion
    # For now, create placeholder
    pdf_path.write_text(f"PDF version of {docx_path.name}")

    return pdf_path
