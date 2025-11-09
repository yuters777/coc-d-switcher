from pathlib import Path
from typing import Dict, Any, Optional
from docxtpl import DocxTemplate
import tempfile
import logging

logger = logging.getLogger(__name__)

def render_docx(template_path: Path, data: Dict[str, Any], job_id: str) -> Path:
    """
    Render DOCX from template and conversion data

    Args:
        template_path: Path to the template DOCX file
        data: Dictionary with template variables (extracted_data + manual_data)
        job_id: Job ID for output filename

    Returns:
        Path to the rendered DOCX file
    """
    logger.info(f"Rendering DOCX for job {job_id} with template {template_path}")

    # Create output path in temp directory
    output_dir = Path(tempfile.gettempdir()) / "coc-rendered"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"COC-D_{job_id}.docx"

    try:
        # Load template
        doc = DocxTemplate(template_path)

        # Flatten the data structure for easier template access
        context = prepare_template_context(data)

        logger.info(f"Rendering with context keys: {list(context.keys())}")

        # Render the template
        doc.render(context)

        # Save rendered document
        doc.save(output_path)

        logger.info(f"Successfully rendered document to {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise


def prepare_template_context(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare template context from job data

    Flattens the data structure so template can use {{ contract_number }}
    instead of {{ part_I.contract_number }}
    """
    context = {}

    # Get extracted data (part_I contains most fields)
    extracted = data.get("extracted_data", {})
    part_i = extracted.get("part_I", {})

    # Flatten part_I fields to top level
    if part_i:
        context.update({
            "contract_number": part_i.get("contract_number", ""),
            "shipment_no": part_i.get("shipment_no", ""),
            "supplier_name": part_i.get("supplier_name", ""),
            "supplier_address": part_i.get("supplier_address", ""),
        })

        # Handle items array (get first item if exists)
        items = part_i.get("items", [])
        if items and len(items) > 0:
            item = items[0]
            context.update({
                "product_description": item.get("description", ""),
                "quantity": item.get("quantity", ""),
                "part_number": item.get("part_number", ""),
            })

    # Add manual data fields (these override extracted if present)
    manual = data.get("manual_data", {})
    if manual:
        context.update({
            "partial_delivery_number": manual.get("partial_delivery_number", ""),
            "undelivered_quantity": manual.get("undelivered_quantity", ""),
            "sw_version": manual.get("sw_version", ""),
        })

        # Manual data can also override extracted data
        if manual.get("contract_number"):
            context["contract_number"] = manual["contract_number"]
        if manual.get("shipment_no"):
            context["shipment_no"] = manual["shipment_no"]
        if manual.get("product_description"):
            context["product_description"] = manual["product_description"]
        if manual.get("quantity"):
            context["quantity"] = manual["quantity"]

    # Add metadata
    context.update({
        "job_id": data.get("id", ""),
        "job_name": data.get("name", ""),
        "submitted_by": data.get("submitted_by", ""),
    })

    logger.info(f"Prepared context with {len(context)} variables")
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
