from pathlib import Path
from typing import Dict, Any, Optional
from docxtpl import DocxTemplate
import tempfile
import logging
from datetime import datetime

logger = logging.getLogger("uvicorn")

def render_docx(conv_json: Dict[str, Any], job_id: str) -> Path:
    """
    Render DOCX from template and conversion data

    Args:
        conv_json: Conversion data including template_vars, manual_data, extracted_data
        job_id: Job ID for output filename

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

    logger.info(f"Rendering DOCX for job {job_id} with filename {filename}")

    # Use cross-platform temporary directory
    output_dir = Path(tempfile.gettempdir()) / "coc-rendered"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / filename

    # Find template file
    template_path = find_template()
    if not template_path or not template_path.exists():
        raise FileNotFoundError(f"Template file not found. Searched in common locations.")

    try:
        # Load template
        doc = DocxTemplate(template_path)

        # Prepare context from conversion data
        context = prepare_template_context(conv_json)

        logger.info(f"Rendering with context keys: {list(context.keys())}")
        logger.debug(f"Context data: {context}")

        # Render the template
        doc.render(context)

        # Save rendered document
        doc.save(output_path)

        logger.info(f"Successfully rendered document to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error rendering template: {e}", exc_info=True)
        raise


def find_template() -> Optional[Path]:
    """Find template file in common locations"""
    # Use the template from metadata (without _fixed suffix)
    template_name = "d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template.docx"

    search_paths = [
        Path(f"templates/{template_name}"),
        Path(f"backend/templates/{template_name}"),
        Path(f"../templates/{template_name}"),
        Path(__file__).parent.parent / "templates" / template_name,
    ]

    for path in search_paths:
        if path.exists():
            logger.info(f"Found template at: {path}")
            return path

    logger.error(f"Template not found. Searched: {[str(p) for p in search_paths]}")
    return None


def prepare_template_context(conv_json: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare template context from conversion data

    Template expects these flat variables (confirmed by extract_template_vars.py):
    - contract_number, shipment_no, contract_item, product_description, quantity
    - supplier_serial_no, delivery_address, acquirer, date
    - partial_delivery_number, final_delivery_number, undelivered_quantity, remarks
    """
    context = {}

    # Get template_vars (prepared by extract.py with all fields INCLUDING serial numbers)
    template_vars = conv_json.get("template_vars", {})
    if template_vars:
        context.update(template_vars)

    # Get manual data and override/add fields
    manual_data = conv_json.get("manual_data", {})
    if manual_data:
        context.update({
            "partial_delivery_number": manual_data.get("partial_delivery_number", ""),
            "undelivered_quantity": manual_data.get("undelivered_quantity", ""),
            "sw_version": manual_data.get("sw_version", ""),
            "contract_item": manual_data.get("contract_item", ""),  # Can be manually set
        })

    # Get extracted data for fallback
    extracted_data = conv_json.get("extracted_data", {})
    if extracted_data:
        part_i = extracted_data.get("part_I", {})
        if part_i:
            # Fill in any missing fields from part_I
            if not context.get("contract_number"):
                context["contract_number"] = part_i.get("contract_number", "")
            if not context.get("shipment_no"):
                context["shipment_no"] = part_i.get("shipment_no", "")
            if not context.get("product_description"):
                context["product_description"] = part_i.get("product_description", "")
            if not context.get("quantity"):
                context["quantity"] = str(part_i.get("quantity", ""))
            # Ensure serial numbers are present
            if not context.get("serials"):
                context["serials"] = part_i.get("serials", [])
                context["serial_count"] = len(context["serials"])

    # Build remarks field from sw_version
    remarks_parts = []
    if context.get("sw_version"):
        remarks_parts.append(f"SW Ver. # {context['sw_version']}")
    context["remarks"] = "\n".join(remarks_parts) if remarks_parts else ""

    # Ensure all expected template variables have defaults
    context.setdefault("contract_number", "")
    context.setdefault("shipment_no", "")
    context.setdefault("contract_item", "")  # Template expects this
    context.setdefault("product_description", "")
    context.setdefault("quantity", "")
    context.setdefault("supplier_serial_no", "")
    context.setdefault("delivery_address", "")
    context.setdefault("acquirer", "")
    context.setdefault("date", datetime.now().strftime("%d.%m.%Y"))
    context.setdefault("partial_delivery_number", "")
    context.setdefault("final_delivery_number", "")
    context.setdefault("undelivered_quantity", "")
    context.setdefault("serials", [])
    context.setdefault("serial_count", 0)

    # Log what we're providing to template
    logger.info(f"Template context prepared with {len(context)} variables")
    logger.info(f"  - contract_number: {context.get('contract_number', 'MISSING')}")
    logger.info(f"  - shipment_no: {context.get('shipment_no', 'MISSING')}")
    logger.info(f"  - contract_item: {context.get('contract_item', 'EMPTY')}")
    logger.info(f"  - product_description: {context.get('product_description', 'MISSING')[:50]}...")
    logger.info(f"  - quantity: {context.get('quantity', 'MISSING')}")
    logger.info(f"  - serial numbers: {len(context.get('serials', []))} items")
    logger.info(f"  - date: {context.get('date', 'MISSING')}")

    return context


def convert_to_pdf(docx_path: Path) -> Path:
    """
    Convert DOCX to PDF using LibreOffice headless

    Note: Requires LibreOffice to be installed on the system
    For now, this is a placeholder
    """
    pdf_path = docx_path.with_suffix(".pdf")

    # TODO: Implement actual conversion using LibreOffice
    # Command: libreoffice --headless --convert-to pdf --outdir <dir> <file>
    # For now, create placeholder
    logger.warning("PDF conversion not yet implemented - creating placeholder")
    pdf_path.write_text(f"PDF version of {docx_path.name}\nPDF conversion requires LibreOffice installation.")

    return pdf_path
