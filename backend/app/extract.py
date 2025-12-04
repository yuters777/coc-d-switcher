"""
COC-D Data Extraction Module

This module handles extraction of data from PDF files (Company COC and Packing Slip)
and mapping to template variables.
"""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from .config import load_config


def normalize_date_to_ddmmyyyy(date_str: str) -> str:
    """
    Normalize date string to DD.MM.YYYY format.

    Handles various input formats:
    - DD/MMM/YYYY (e.g., "20/Mar/2025")
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

    # Try DD/MMM/YYYY format (e.g., "20/Mar/2025")
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

    return date_str


def calculate_supplier_serial_no(shipment_no: str, date_str: str) -> str:
    """
    Calculate the Supplier Serial Number for the COC document.

    Format: COC_SV_Del{XXX}_{DD.MM.YYYY}.docx
    Where XXX is the last 3 digits of the shipment number.

    Args:
        shipment_no: Shipment number (e.g., "6SH264587")
        date_str: Date string to be normalized

    Returns:
        Formatted supplier serial number (e.g., "COC_SV_Del587_20.03.2025.docx")
    """
    # Extract last 3 digits from shipment number
    digits = re.sub(r'[^0-9]', '', str(shipment_no))
    del_number = digits[-3:] if len(digits) >= 3 else digits.zfill(3)

    # Normalize the date
    normalized_date = normalize_date_to_ddmmyyyy(date_str)

    if not normalized_date:
        normalized_date = datetime.now().strftime("%d.%m.%Y")

    return f"COC_SV_Del{del_number}_{normalized_date}.docx"


def extract_from_company_coc(pdf_path: Optional[str]) -> Dict[str, Any]:
    """
    Extract data from Company COC PDF.

    Args:
        pdf_path: Path to the Company COC PDF file

    Returns:
        Dictionary containing extracted COC data
    """
    if not pdf_path:
        return {}

    # In production, use PDF extraction library
    # For now, return sample structure
    return {
        "order": "",
        "customer_part_no": "",
        "product_name": "",
        "quantity": 0,
        "shipment_no": "",
        "date": "",
        "acquirer": "",
        "serials": []
    }


def extract_from_packing_slip(pdf_path: Optional[str]) -> Dict[str, Any]:
    """
    Extract data from Packing Slip PDF.

    Args:
        pdf_path: Path to the Packing Slip PDF file

    Returns:
        Dictionary containing extracted packing slip data
    """
    if not pdf_path:
        return {}

    # In production, use PDF extraction library
    # For now, return sample structure
    return {
        "delivery_address": "",
        "shipment_document": "",
        "packing_slip_no": ""
    }


def map_to_template_vars(coc_data: Dict[str, Any], packing_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Map extracted data to template variables.

    This function transforms the raw extracted data from COC and Packing Slip
    into the flat template variable format expected by docxtpl.

    Args:
        coc_data: Dictionary from Company COC extraction
        packing_data: Dictionary from Packing Slip extraction

    Returns:
        Dictionary with all template variables
    """
    # Get key values
    shipment_no = coc_data.get("shipment_no", "")
    date_str = coc_data.get("date", "")

    # Calculate supplier serial number
    supplier_serial = calculate_supplier_serial_no(shipment_no, date_str)

    # Extract delivery number from shipment number (last 3 digits)
    digits = re.sub(r'[^0-9]', '', str(shipment_no))
    partial_delivery = digits[-3:] if len(digits) >= 3 else digits

    template_vars = {
        # Supplier Serial No
        "supplier_serial_no": supplier_serial,

        # Contract fields
        "contract_number": coc_data.get("order", ""),
        "contract_item": coc_data.get("customer_part_no", ""),

        # Product info
        "product_description": coc_data.get("product_name", ""),
        "quantity": coc_data.get("quantity", 0),

        # Shipment info
        "shipment_no": shipment_no,
        "partial_delivery_number": partial_delivery,
        "final_delivery_number": "N/A",

        # Acquirer and delivery
        "acquirer": coc_data.get("acquirer", ""),
        "delivery_address": packing_data.get("delivery_address", ""),

        # Date
        "date": normalize_date_to_ddmmyyyy(date_str),

        # Undelivered quantity (to be filled manually)
        "undelivered_quantity": "",

        # Remarks
        "remarks": "",

        # Serials
        "serials": coc_data.get("serials", [])
    }

    return template_vars


def validate_extracted_data(template_vars: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """
    Validate extracted data and identify missing required fields.

    Args:
        template_vars: Dictionary of template variables

    Returns:
        Dictionary with 'errors' and 'warnings' lists
    """
    errors = []
    warnings = []

    # Required fields validation
    required_fields = {
        "supplier_serial_no": "MISSING_SUPPLIER_SERIAL",
        "contract_number": "MISSING_CONTRACT_NUMBER",
        "contract_item": "MISSING_CONTRACT_ITEM",
        "product_description": "MISSING_PRODUCT_DESCRIPTION",
        "quantity": "MISSING_QUANTITY"
    }

    for field, error_code in required_fields.items():
        value = template_vars.get(field)
        if not value or (isinstance(value, (int, float)) and value == 0):
            errors.append({
                "code": error_code,
                "message": f"Required field '{field}' is missing or empty",
                "where": f"template_vars.{field}"
            })

    # Warnings for optional but recommended fields
    optional_fields = ["delivery_address", "acquirer", "remarks"]
    for field in optional_fields:
        if not template_vars.get(field):
            warnings.append({
                "code": f"EMPTY_{field.upper()}",
                "message": f"Optional field '{field}' is empty",
                "where": f"template_vars.{field}"
            })

    return {"errors": errors, "warnings": warnings}


def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """
    Extract data from both PDF files and prepare for rendering.

    This is the main extraction entry point that:
    1. Extracts data from Company COC PDF
    2. Extracts data from Packing Slip PDF
    3. Maps to template variables
    4. Validates the extracted data

    Args:
        company_coc_path: Path to Company COC PDF
        packing_slip_path: Path to Packing Slip PDF

    Returns:
        Complete extraction result with raw data, template vars, and validation
    """
    config = load_config()

    # Extract from both sources
    coc_data = extract_from_company_coc(company_coc_path)
    packing_data = extract_from_packing_slip(packing_slip_path)

    # Map to template variables
    template_vars = map_to_template_vars(coc_data, packing_data)

    # Validate
    validation = validate_extracted_data(template_vars)

    result = {
        "extracted_raw": {
            "from_coc": coc_data,
            "from_packing_slip": packing_data
        },
        "extracted": {
            "from_packing_slip": packing_data,
            "from_company_coc": coc_data
        },
        "template_vars": template_vars,
        "part_I": {},
        "part_II": {},
        "render_vars": {
            "docx_template": config.get("template_name", "COC_SV_Del165_20.03.2025.docx"),
            "output_filename": template_vars.get("supplier_serial_no", ""),
            "date_format": "DD.MM.YYYY"
        },
        "validation": validation
    }

    return result


def normalize_date(date_str: str) -> str:
    """
    Normalize date to DD/MMM/YYYY format.

    Legacy function - use normalize_date_to_ddmmyyyy for DD.MM.YYYY format.

    Args:
        date_str: Input date string

    Returns:
        Normalized date string
    """
    if not date_str:
        return ""
    return normalize_date_to_ddmmyyyy(date_str)
