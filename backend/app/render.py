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
    search_paths = [
        Path("templates/COC_SV_Del165_20.03.2025.docx"),
        Path("backend/templates/COC_SV_Del165_20.03.2025.docx"),
        Path("../templates/COC_SV_Del165_20.03.2025.docx"),
        Path(__file__).parent.parent / "templates" / "COC_SV_Del165_20.03.2025.docx",
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

    Flattens the data structure for template variables
    """
    context = {}

    # Get template_vars (prepared by extract.py with all fields)
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

    # Build remarks field from sw_version
    remarks_parts = []
    if context.get("sw_version"):
        remarks_parts.append(f"SW Ver. # {context['sw_version']}")
    context["remarks"] = "\n".join(remarks_parts) if remarks_parts else ""

    # Ensure date is in correct format
    if not context.get("date"):
        context["date"] = datetime.now().strftime("%d.%m.%Y")

    # Ensure final_delivery_number has default
    if not context.get("final_delivery_number"):
        context["final_delivery_number"] = "N/A"

    # Add contract_item if missing
    if not context.get("contract_item"):
        context["contract_item"] = ""

    logger.info(f"Prepared context with {len(context)} variables")
    logger.debug(f"Template context: {list(context.keys())}")
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
