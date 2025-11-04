import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .config import load_config

def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """Extract data from PDFs"""
    config = load_config()

    # Generate supplier serial number
    today = datetime.now()
    # Format: COC_SV_Del{last3digits}_{date}.docx
    supplier_serial = f"COC_SV_Del{today.day:03d}_{today.strftime('%d.%m.%Y')}.docx"

    result = {
        "extracted": {"from_packing_slip": {}, "from_company_coc": {}},
        "part_I": {
            "supplier_serial_no": supplier_serial,
            "contract_number": "",
            "applicable_to": "",
            "items": [],
            "serials": [],
            "remarks": "",
            "date": ""
        },
        "part_II": {},
        "render_vars": {
            "docx_template": supplier_serial,
            "output_filename": "",
            "date_format": "DD/MMM/YYYY"
        },
        "validation": {"errors": [], "warnings": []}
    }

    # Implementation would extract from actual PDFs
    # For now, return sample structure
    return result

def normalize_date(date_str: str) -> str:
    """Normalize date to DD/MMM/YYYY format"""
    if not date_str:
        return ""
    # Implementation would handle various date formats
    return date_str
