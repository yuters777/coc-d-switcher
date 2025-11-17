import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from .config import load_config

def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """Extract data from PDFs"""
    config = load_config()

    result = {
        "extracted": {"from_packing_slip": {}, "from_company_coc": {}},
        "part_I": {},
        "part_II": {},
        "render_vars": {
            "docx_template": "COC_SV_Del165_20.03.2025.docx",
            "output_filename": "",
            "date_format_display": "DD/Mon/YYYY",
            "date_format_filename": "DD.MM.YYYY"
        },
        "validation": {"errors": [], "warnings": []}
    }

    # Implementation would extract from actual PDFs
    # For now, return sample structure
    return result

def normalize_date(date_str: str, output_format: str = "display") -> str:
    """Normalize date to specified format

    Args:
        date_str: Input date string in various formats
        output_format: 'display' for DD/Mon/YYYY (e.g., 20/Mar/2025)
                      or 'filename' for DD.MM.YYYY (e.g., 20.03.2025)

    Returns:
        Formatted date string
    """
    if not date_str:
        return ""

    # Try to parse various common date formats
    date_formats = [
        "%d/%m/%Y",      # 20/03/2025
        "%d.%m.%Y",      # 20.03.2025
        "%d-%m-%Y",      # 20-03-2025
        "%d/%b/%Y",      # 20/Mar/2025
        "%d/%B/%Y",      # 20/March/2025
        "%Y-%m-%d",      # 2025-03-20
        "%d.%m.%y",      # 20.03.25
        "%d/%m/%y",      # 20/03/25
    ]

    parsed_date = None
    for fmt in date_formats:
        try:
            parsed_date = datetime.strptime(date_str.strip(), fmt)
            break
        except ValueError:
            continue

    if not parsed_date:
        # If parsing fails, return original
        return date_str

    # Format based on requested output
    if output_format == "filename":
        return parsed_date.strftime("%d.%m.%Y")
    else:  # display format
        return parsed_date.strftime("%d/%b/%Y")
