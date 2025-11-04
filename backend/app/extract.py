import re
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from .config import load_config

logger = logging.getLogger(__name__)

def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """Extract data from PDFs"""
    try:
        config = load_config()

        result = {
            "extracted": {"from_packing_slip": {}, "from_company_coc": {}},
            "part_I": {},
            "part_II": {},
            "render_vars": {
                "docx_template": "COC_SV_Del165_20.03.2025.docx",
                "output_filename": "",
                "date_format": "DD/MMM/YYYY"
            },
            "validation": {"errors": [], "warnings": []}
        }

        # Implementation would extract from actual PDFs
        # For now, return sample structure
        return result
    except Exception as e:
        logger.error(f"Error extracting from PDFs: {str(e)}")
        raise

def extract_from_company_coc(file_path: str) -> Dict[str, Any]:
    """Extract data from company COC PDF"""
    try:
        # TODO: Implement actual PDF extraction
        # For now, return empty structure
        return {
            "contract_number": "",
            "items": [],
            "supplier_info": {}
        }
    except Exception as e:
        logger.error(f"Error extracting from company COC: {str(e)}")
        raise

def extract_from_packing_slip(file_path: str) -> Dict[str, Any]:
    """Extract data from packing slip PDF"""
    try:
        # TODO: Implement actual PDF extraction
        # For now, return empty structure
        return {
            "serials": [],
            "shipping_info": {}
        }
    except Exception as e:
        logger.error(f"Error extracting from packing slip: {str(e)}")
        raise

def map_to_template_vars(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
    """Map extracted data to template variables"""
    try:
        # TODO: Implement actual mapping logic
        # For now, return the extracted data as-is
        return extracted_data
    except Exception as e:
        logger.error(f"Error mapping to template vars: {str(e)}")
        raise

def normalize_date(date_str: str) -> str:
    """Normalize date to DD/MMM/YYYY format"""
    try:
        if not date_str:
            return ""
        # Try to parse common date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y"]:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%d/%b/%Y")
            except ValueError:
                continue
        # If no format matches, return as-is
        return date_str
    except Exception as e:
        logger.error(f"Error normalizing date '{date_str}': {str(e)}")
        return date_str

def normalize_date_to_ddmmyyyy(date_str: str) -> str:
    """Normalize date to DD/MM/YYYY format"""
    try:
        if not date_str:
            return ""
        # Try to parse common date formats
        for fmt in ["%Y-%m-%d", "%d-%m-%Y", "%m/%d/%Y", "%d/%m/%Y", "%d/%b/%Y"]:
            try:
                parsed = datetime.strptime(date_str, fmt)
                return parsed.strftime("%d/%m/%Y")
            except ValueError:
                continue
        # If no format matches, return as-is
        return date_str
    except Exception as e:
        logger.error(f"Error normalizing date to DD/MM/YYYY '{date_str}': {str(e)}")
        return date_str

def validate_extracted_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted data before processing"""
    try:
        errors = []
        warnings = []

        # Basic validation
        if not data:
            errors.append("No data extracted")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }
    except Exception as e:
        logger.error(f"Error validating extracted data: {str(e)}")
        return {
            "valid": False,
            "errors": [f"Validation error: {str(e)}"],
            "warnings": []
        }
