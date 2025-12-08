"""
COC-D Document Rendering Module

This module handles the rendering of Certificate of Conformity documents
by flattening nested data structures to match template variables.
"""

import logging
import os
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from docxtpl import DocxTemplate

logger = logging.getLogger(__name__)

TEMPLATE_PATH = os.getenv("TEMPLATE_PATH", "templates/COC_SV_Del165_20.03.2025.docx")

# Default values for static/reference fields
DEFAULT_ACQUIRER = """NETHERLANDS MINISTRY OF DEFENCE
COMMIT
Projects Procurement Division
Herculeslaan 1, 3584 AB Utrecht MPC 55 A
The Netherlands"""

DEFAULT_SUPPLIER = {
    "name": "Elbit Systems C4I and Cyber Ltd",
    "address": "2 Hamachshev, Netanya\nIsrael",
    "contact": "Ido Shilo",
    "email": "Ido.Shilo@elbitsystems.com"
}

DEFAULT_GQAR = {
    "name": "R. Kompier",
    "phone": "+31620415178",
    "email": "R.Kompier@mindef.nl"
}

DEFAULT_CONTRACT_MODIFICATION = """AMENDEMENT 15-12-2020 VOSS additional order
C4I solution and deliveries 11-12-2020
10-01-2022 Amendment to the Agreement TCP
187, TCP 192, TCP 193 DMO signed
Approved TCP's list"""

DEFAULT_APPROVED_DEVIATIONS = """See remarks in Box 14.
ELB_VOS_POR001
ELB_VOS_CE0003
ELB_VOS_SEC001
ELB_VOS_CE0004"""


def normalize_date_to_ddmmyyyy(date_str: str) -> str:
    """
    Normalize date string to DD.MM.YYYY format.

    Handles various input formats:
    - DD/MMM/YYYY (e.g., "04/Nov/2025")
    - DD-MM-YYYY
    - YYYY-MM-DD
    - DD.MM.YYYY (already normalized)

    Args:
        date_str: Input date string

    Returns:
        Date in DD.MM.YYYY format or empty string if invalid
    """
    if not date_str:
        return ""

    date_str = date_str.strip()

    # Already in correct format
    if re.match(r'^\d{2}\.\d{2}\.\d{4}$', date_str):
        return date_str

    # Month name mapping
    month_map = {
        'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04',
        'may': '05', 'jun': '06', 'jul': '07', 'aug': '08',
        'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'
    }

    # Try DD/MMM/YYYY format (e.g., "04/Nov/2025")
    match = re.match(r'^(\d{1,2})[/\-](\w{3})[/\-](\d{4})$', date_str, re.IGNORECASE)
    if match:
        day = match.group(1).zfill(2)
        month = month_map.get(match.group(2).lower()[:3], '01')
        year = match.group(3)
        return f"{day}.{month}.{year}"

    # Try DD-MM-YYYY or DD/MM/YYYY format
    match = re.match(r'^(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})$', date_str)
    if match:
        day = match.group(1).zfill(2)
        month = match.group(2).zfill(2)
        year = match.group(3)
        return f"{day}.{month}.{year}"

    # Try YYYY-MM-DD format
    match = re.match(r'^(\d{4})[/\-](\d{1,2})[/\-](\d{1,2})$', date_str)
    if match:
        year = match.group(1)
        month = match.group(2).zfill(2)
        day = match.group(3).zfill(2)
        return f"{day}.{month}.{year}"

    logger.warning(f"Could not normalize date: {date_str}")
    return date_str


def calculate_supplier_serial_no(partial_delivery_number: str, date_str: str) -> str:
    """
    Calculate the Supplier Serial Number for the COC document.

    Format: COC_SV_Del{XXX}_{DD.MM.YYYY}
    Where XXX is the partial delivery number (from manual input).

    Args:
        partial_delivery_number: Partial delivery number (e.g., "165")
        date_str: Date string to be normalized

    Returns:
        Formatted supplier serial number (e.g., "COC_SV_Del165_20.03.2025")
    """
    # Use partial delivery number directly (pad with zeros if needed)
    del_number = str(partial_delivery_number).strip() if partial_delivery_number else "000"

    # Normalize the date
    normalized_date = normalize_date_to_ddmmyyyy(date_str)

    if not normalized_date:
        normalized_date = datetime.now().strftime("%d.%m.%Y")

    return f"COC_SV_Del{del_number}_{normalized_date}"


def format_delivery_address(address_data: Optional[Dict[str, Any]]) -> str:
    """
    Format delivery address data as multi-line string.

    Args:
        address_data: Dictionary with 'Name' and 'AddressLines' keys,
                     or a string directly

    Returns:
        Multi-line formatted address string
    """
    if not address_data:
        return ""

    if isinstance(address_data, str):
        return address_data

    lines = []

    # Add organization name
    if address_data.get("Name"):
        lines.append(str(address_data["Name"]))

    # Add address lines
    address_lines = address_data.get("AddressLines", [])
    if isinstance(address_lines, list):
        lines.extend([str(line) for line in address_lines if line])
    elif isinstance(address_lines, str):
        lines.append(address_lines)

    return "\n".join(lines)


def format_acquirer_data(acquirer_data: Optional[Dict[str, Any]]) -> str:
    """
    Format acquirer data as multi-line string.
    Falls back to Netherlands Ministry of Defence if not provided.

    Args:
        acquirer_data: Dictionary with acquirer details or string

    Returns:
        Multi-line formatted acquirer string
    """
    if not acquirer_data:
        return DEFAULT_ACQUIRER

    if isinstance(acquirer_data, str):
        return acquirer_data if acquirer_data.strip() else DEFAULT_ACQUIRER

    lines = []

    # Add organization name
    name = acquirer_data.get("Name", "")
    if name:
        lines.append(str(name))

    # Add address lines
    address_lines = acquirer_data.get("AddressLines", [])
    if isinstance(address_lines, list):
        lines.extend([str(line) for line in address_lines if line])
    elif isinstance(address_lines, str):
        lines.append(address_lines)

    return "\n".join(lines) if lines else DEFAULT_ACQUIRER


def format_applicable_to(partial_delivery: str, final_delivery: str = "N/A") -> str:
    """
    Format the 'Applicable To' field with delivery numbers.

    Args:
        partial_delivery: Partial delivery number
        final_delivery: Final delivery number (defaults to N/A)

    Returns:
        Formatted applicable to string
    """
    return f"Partial Delivery Number: {partial_delivery}\n\nFinal Delivery Number: {final_delivery}"


def extract_delivery_number(shipment_no: str) -> str:
    """
    Extract delivery number from shipment number.

    Args:
        shipment_no: Full shipment number (e.g., "6SH264587")

    Returns:
        Delivery number portion (e.g., "240")
    """
    # Extract digits
    digits = re.sub(r'[^0-9]', '', str(shipment_no))
    # Return last 3 digits as delivery number
    return digits[-3:] if len(digits) >= 3 else digits


def parse_product_description(raw_description: str) -> dict:
    """
    Parse concatenated product description into components.

    Input format: "20580903700; PNR-1000N WPTT; Customer Item 20000646041"

    Returns dict with:
    - catalog_number: "20580903700"
    - product_name: "PNR-1000N WPTT"
    - customer_item: "20000646041"
    - formatted_description: "20580903700 - PNR-1000N WPTT"

    Args:
        raw_description: Concatenated product description string

    Returns:
        Dictionary with parsed components
    """
    result = {
        "catalog_number": "",
        "product_name": "",
        "customer_item": "",
        "formatted_description": raw_description  # Default to original
    }

    if not raw_description:
        return result

    # Split by semicolon
    parts = [p.strip() for p in str(raw_description).split(';')]

    if len(parts) >= 1:
        result["catalog_number"] = parts[0].strip()

    if len(parts) >= 2:
        result["product_name"] = parts[1].strip()
        # Format as "catalog - product_name"
        result["formatted_description"] = f"{result['catalog_number']} - {result['product_name']}"

    if len(parts) >= 3:
        # Extract customer item number from "Customer Item 20000646041"
        customer_part = parts[2].strip()
        # Remove "Customer Item" prefix if present
        customer_item_match = re.search(r'(?:Customer\s*Item\s*)?(\d+)', customer_part, re.IGNORECASE)
        if customer_item_match:
            result["customer_item"] = customer_item_match.group(1)
        else:
            result["customer_item"] = customer_part

    return result


def format_shipment_document(shipment_doc: str, packing_slip: str = "") -> str:
    """
    Format shipment document field, ensuring 'Delivery by DSV' is included.

    Args:
        shipment_doc: Original shipment document text
        packing_slip: Packing slip number

    Returns:
        Formatted shipment document with DSV delivery note
    """
    parts = []

    if packing_slip:
        parts.append(f"Packing Slip: {packing_slip}")
    elif shipment_doc:
        parts.append(str(shipment_doc))

    # Always add DSV delivery note
    if "Delivery by DSV" not in str(shipment_doc):
        parts.append("Delivery by DSV")

    return "\n".join(parts)


def flatten_data_for_template(job_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Flatten nested PI/PII data structure to match template variables.

    The template expects flat variables like:
    - supplier_serial_no
    - contract_number
    - acquirer
    - delivery_address
    etc.

    But the backend sends nested structure with PI and PII keys.

    Args:
        job_data: Nested dictionary with PI/PII structure

    Returns:
        Flat dictionary matching template variable names
    """
    # Handle case where data might already be flat or in different structure
    pi_data = job_data.get("PI", job_data.get("part_I", {}))
    pii_data = job_data.get("PII", job_data.get("part_II", {}))

    # Also check for template_vars key (from extraction)
    template_vars = job_data.get("template_vars", {})

    # Get manual_data (contains partial_delivery_number from user input)
    manual_data = job_data.get("manual_data", {})

    # Extract item data (use first item if available)
    items = pi_data.get("Items", pi_data.get("items", []))
    first_item = items[0] if items else {}

    # Get key values
    shipment_no = (
        pi_data.get("ShipmentNumber") or
        pi_data.get("shipment_no") or
        template_vars.get("shipment_no") or
        first_item.get("ShipmentDocument") or
        ""
    )

    # Extract packing slip number from shipment data
    packing_slip = (
        first_item.get("PackingSlip") or
        first_item.get("ShipmentDocument") or
        pi_data.get("PackingSlip") or
        ""
    )

    date_str = (
        pi_data.get("Date") or
        pi_data.get("date") or
        template_vars.get("date") or
        datetime.now().strftime("%d/%b/%Y")
    )

    contract_number = (
        pi_data.get("ContractNumber") or
        pi_data.get("contract_number") or
        pi_data.get("order") or
        template_vars.get("contract_number") or
        ""
    )

    # Extract partial delivery number (prioritize manual_data from user input)
    partial_delivery = (
        manual_data.get("partial_delivery_number") or
        template_vars.get("partial_delivery_number") or
        pi_data.get("PartialDeliveryNumber") or
        pi_data.get("partial_delivery_number") or
        extract_delivery_number(shipment_no)
    )

    # Extract raw product description for parsing
    raw_product_description = (
        first_item.get("ProductDescriptionOrPart") or
        first_item.get("product_description_or_part") or
        first_item.get("product_description") or
        pi_data.get("product_name") or
        template_vars.get("product_description") or
        ""
    )

    # Parse the product description to extract components
    # Input: "20580903700; PNR-1000N WPTT; Customer Item 20000646041"
    # Output: catalog_number, product_name, customer_item, formatted_description
    parsed_product = parse_product_description(raw_product_description)

    # Field 9 (contract_item): Use customer_item from parsed description, or fallback to other sources
    contract_item = (
        parsed_product.get("customer_item") or
        first_item.get("ContractItem") or
        first_item.get("contract_item") or
        pi_data.get("customer_part_no") or
        template_vars.get("contract_item") or
        ""
    )

    # Field 10 (product_description): Use formatted "catalog - product_name" format
    product_description = parsed_product.get("formatted_description") or raw_product_description

    quantity = (
        first_item.get("Quantity") or
        first_item.get("quantity") or
        pi_data.get("quantity") or
        template_vars.get("quantity") or
        ""
    )

    # Get shipment document with DSV
    shipment_doc_raw = (
        first_item.get("ShipmentDocument") or
        first_item.get("shipment_document") or
        packing_slip or
        shipment_no
    )

    # Undelivered quantity (prioritize manual_data from user input)
    undelivered_qty = (
        manual_data.get("undelivered_quantity") or
        template_vars.get("undelivered_quantity") or
        first_item.get("UndeliveredQuantity") or
        first_item.get("undelivered_quantity") or
        pi_data.get("undelivered_quantity") or
        ""
    )

    # Remarks (prioritize manual_data from user input)
    remarks = (
        manual_data.get("remarks") or
        template_vars.get("remarks") or
        pi_data.get("Remarks") or
        pi_data.get("remarks") or
        ""
    )

    # GQAR data from Part II
    gqar_data = pii_data.get("GQAR", pii_data.get("gqar", {}))

    # Supplier data
    supplier_data = pi_data.get("Supplier", pi_data.get("supplier", {}))

    # Build flat data dictionary
    flat_data = {
        # Page 1 - Core fields
        # supplier_serial_no uses partial_delivery_number (from manual input) + date
        "supplier_serial_no": calculate_supplier_serial_no(partial_delivery, date_str),
        "contract_number": str(contract_number),
        "contract_modification": (
            pi_data.get("ContractModification") or
            template_vars.get("contract_modification") or
            DEFAULT_CONTRACT_MODIFICATION
        ),

        # Supplier info
        "supplier_name": (
            supplier_data.get("Name") or
            supplier_data.get("name") or
            template_vars.get("supplier_name") or
            DEFAULT_SUPPLIER["name"]
        ),
        "supplier_address": (
            supplier_data.get("Address") or
            supplier_data.get("address") or
            template_vars.get("supplier_address") or
            DEFAULT_SUPPLIER["address"]
        ),
        "supplier_contact": (
            supplier_data.get("Contact") or
            supplier_data.get("contact") or
            template_vars.get("supplier_contact") or
            DEFAULT_SUPPLIER["contact"]
        ),
        "supplier_email": (
            supplier_data.get("Email") or
            supplier_data.get("email") or
            template_vars.get("supplier_email") or
            DEFAULT_SUPPLIER["email"]
        ),

        # Acquirer and delivery
        "acquirer": format_acquirer_data(
            pi_data.get("Acquirer") or
            pi_data.get("acquirer") or
            template_vars.get("acquirer")
        ),
        "delivery_address": format_delivery_address(
            pi_data.get("DeliveryAddress") or
            pi_data.get("delivery_address") or
            template_vars.get("delivery_address")
        ),

        # Approved deviations
        "approved_deviations": (
            pi_data.get("ApprovedDeviations") or
            template_vars.get("approved_deviations") or
            DEFAULT_APPROVED_DEVIATIONS
        ),

        # Applicable to
        "applicable_to": format_applicable_to(
            str(partial_delivery),
            pi_data.get("FinalDeliveryNumber") or
            template_vars.get("final_delivery_number") or
            "N/A"
        ),
        "partial_delivery_number": str(partial_delivery),
        "final_delivery_number": (
            pi_data.get("FinalDeliveryNumber") or
            template_vars.get("final_delivery_number") or
            "N/A"
        ),

        # Item data (Fields 9-13)
        "contract_item": str(contract_item),
        "product_description": str(product_description),
        "quantity": str(quantity),
        "shipment_no": format_shipment_document(shipment_doc_raw, packing_slip),
        "undelivered_quantity": str(undelivered_qty),

        # Remarks
        "remarks": str(remarks),

        # Date
        "date": normalize_date_to_ddmmyyyy(date_str),

        # Page 2 - GQAR fields
        "gqar_name": (
            gqar_data.get("Name") or
            gqar_data.get("name") or
            template_vars.get("gqar_name") or
            DEFAULT_GQAR["name"]
        ),
        "gqar_phone": (
            gqar_data.get("Phone") or
            gqar_data.get("phone") or
            gqar_data.get("PhoneNumber") or
            template_vars.get("gqar_phone") or
            DEFAULT_GQAR["phone"]
        ),
        "gqar_email": (
            gqar_data.get("Email") or
            gqar_data.get("email") or
            template_vars.get("gqar_email") or
            DEFAULT_GQAR["email"]
        ),
        "gqar_date": normalize_date_to_ddmmyyyy(date_str),

        # Additional serial fields (if present)
        "serial_count": (
            pi_data.get("SerialCount") or
            template_vars.get("serial_count") or
            str(quantity)
        ),
        "serials_list": (
            pi_data.get("SerialsList") or
            template_vars.get("serials_list") or
            ""
        ),
    }

    logger.debug(f"Flattened data keys: {list(flat_data.keys())}")

    return flat_data


def prepare_context(template_vars: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare rendering context with all required variables and defaults.

    This function ensures all template variables have values,
    using defaults where necessary.

    Args:
        template_vars: Dictionary of template variables (may be incomplete)

    Returns:
        Complete context dictionary with all required variables
    """
    # If we receive nested data, flatten it first
    if "PI" in template_vars or "PII" in template_vars:
        template_vars = flatten_data_for_template(template_vars)

    # Current date as fallback
    current_date = datetime.now().strftime("%d.%m.%Y")

    # Build context with defaults
    context = {
        # Page 1 fields
        "supplier_serial_no": template_vars.get("supplier_serial_no", ""),
        "contract_number": template_vars.get("contract_number", ""),
        "contract_modification": template_vars.get("contract_modification", DEFAULT_CONTRACT_MODIFICATION),

        # Supplier
        "supplier_name": template_vars.get("supplier_name", DEFAULT_SUPPLIER["name"]),
        "supplier_address": template_vars.get("supplier_address", DEFAULT_SUPPLIER["address"]),
        "supplier_contact": template_vars.get("supplier_contact", DEFAULT_SUPPLIER["contact"]),
        "supplier_email": template_vars.get("supplier_email", DEFAULT_SUPPLIER["email"]),

        # Acquirer and delivery
        "acquirer": template_vars.get("acquirer", DEFAULT_ACQUIRER),
        "delivery_address": template_vars.get("delivery_address", ""),
        "approved_deviations": template_vars.get("approved_deviations", DEFAULT_APPROVED_DEVIATIONS),

        # Applicable to
        "applicable_to": template_vars.get("applicable_to", ""),
        "partial_delivery_number": template_vars.get("partial_delivery_number", ""),
        "final_delivery_number": template_vars.get("final_delivery_number", "N/A"),

        # Item data
        "contract_item": template_vars.get("contract_item", ""),
        "product_description": template_vars.get("product_description", ""),
        "quantity": template_vars.get("quantity", ""),
        "shipment_no": template_vars.get("shipment_no", ""),
        "undelivered_quantity": template_vars.get("undelivered_quantity", ""),

        # Remarks
        "remarks": template_vars.get("remarks", ""),

        # Date
        "date": template_vars.get("date", current_date),

        # Page 2 - GQAR
        "gqar_name": template_vars.get("gqar_name", DEFAULT_GQAR["name"]),
        "gqar_phone": template_vars.get("gqar_phone", DEFAULT_GQAR["phone"]),
        "gqar_email": template_vars.get("gqar_email", DEFAULT_GQAR["email"]),
        "gqar_date": template_vars.get("gqar_date", template_vars.get("date", current_date)),

        # Serials
        "serial_count": template_vars.get("serial_count", ""),
        "serials_list": template_vars.get("serials_list", ""),
    }

    # Generate applicable_to if not provided
    if not context["applicable_to"] and context["partial_delivery_number"]:
        context["applicable_to"] = format_applicable_to(
            context["partial_delivery_number"],
            context["final_delivery_number"]
        )

    return context


def render_docx(conv_json: Dict[str, Any], job_id: str, template_path: Optional[str] = None) -> Path:
    """
    Render DOCX from conversion data using docxtpl.

    This function:
    1. Flattens nested PI/PII data to match template variables
    2. Prepares context with defaults
    3. Renders the template with docxtpl

    Args:
        conv_json: Conversion data (nested or flat format)
        job_id: Unique job identifier
        template_path: Optional path to template file

    Returns:
        Path to the rendered DOCX file
    """
    # Determine template path
    if template_path is None:
        # Check for template in templates directory
        backend_dir = Path(__file__).parent.parent
        template_candidates = [
            # New template with proper {{ placeholders }} for GQAR section
            backend_dir / "templates" / "dutch_coc_template.docx",
            # Fallback templates
            backend_dir / "templates" / "d0d00cd7-54a4-4925-a5bd-6965624e82b8_temp_dutch_coc_template.docx",
            backend_dir / "templates" / "COC_SV_Del165_20.03.2025.docx",
            Path(TEMPLATE_PATH),
        ]

        template_file = None
        for candidate in template_candidates:
            if candidate.exists():
                template_file = candidate
                break

        if template_file is None:
            logger.error(f"No template file found. Checked: {template_candidates}")
            # Fall back to placeholder for development
            out_path = Path(tempfile.gettempdir()) / f"coc-{job_id}.docx"
            import json
            with open(out_path, 'w') as f:
                json.dump(conv_json, f, indent=2)
            return out_path
    else:
        template_file = Path(template_path)

    # Flatten data if needed
    if "PI" in conv_json or "PII" in conv_json or "part_I" in conv_json:
        flat_data = flatten_data_for_template(conv_json)
    else:
        flat_data = conv_json

    # Prepare context with defaults
    context = prepare_context(flat_data)

    # Get supplier_serial_no for filename (same as field 1)
    supplier_serial_no = context.get("supplier_serial_no", f"COC_SV_Del000_{datetime.now().strftime('%d.%m.%Y')}")

    # Add file_name to context for template footer
    context["file_name"] = f"{supplier_serial_no}.docx"

    logger.info(f"Rendering template: {template_file}")
    logger.debug(f"Context keys: {list(context.keys())}")

    # Output path uses supplier_serial_no as filename (cross-platform)
    out_path = Path(tempfile.gettempdir()) / f"{supplier_serial_no}.docx"

    try:
        # Load and render template
        doc = DocxTemplate(str(template_file))
        doc.render(context)
        doc.save(str(out_path))

        logger.info(f"Successfully rendered document: {out_path}")

    except Exception as e:
        logger.error(f"Error rendering template: {e}")
        raise

    return out_path


def convert_to_pdf(docx_path: Path) -> Path:
    """
    Convert DOCX to PDF using LibreOffice headless.

    Args:
        docx_path: Path to the DOCX file

    Returns:
        Path to the generated PDF file
    """
    pdf_path = docx_path.with_suffix(".pdf")

    try:
        # Try LibreOffice conversion
        result = subprocess.run([
            'libreoffice', '--headless', '--convert-to', 'pdf',
            '--outdir', str(docx_path.parent),
            str(docx_path)
        ], capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and pdf_path.exists():
            logger.info(f"Successfully converted to PDF: {pdf_path}")
            return pdf_path
        else:
            logger.warning(f"LibreOffice conversion failed: {result.stderr}")

    except FileNotFoundError:
        logger.warning("LibreOffice not found, creating placeholder PDF")
    except subprocess.TimeoutExpired:
        logger.warning("LibreOffice conversion timed out")
    except Exception as e:
        logger.warning(f"PDF conversion error: {e}")

    # Fallback: create placeholder
    pdf_path.write_text(f"PDF version of {docx_path.name}")
    return pdf_path
