from typing import Dict, Any, List
import re
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def validate_conversion(data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Validate conversion data with enhanced rules"""

    errors = []
    warnings = []

    try:
        part_i = data.get("part_I", {})

        # Check serial count matches quantity
        serials = part_i.get("serials", [])
        items = part_i.get("items", [])

        # Fixed: Check if items exist and have length, not just truthy
        if items and len(items) > 0:
            quantity = items[0].get("quantity", 0)
            # Validate serials count matches quantity (even if serials is empty list)
            if len(serials) != quantity:
                errors.append({
                    "code": "SERIAL_COUNT_MISMATCH",
                    "message": f"Serial count ({len(serials)}) does not match quantity ({quantity})",
                    "where": "part_I.serials"
                })
        elif not items or len(items) == 0:
            # No items found
            errors.append({
                "code": "MISSING_ITEMS",
                "message": "No items found in part_I",
                "where": "part_I.items"
            })

        # Check contract number present
        if not part_i.get("contract_number"):
            errors.append({
                "code": "MISSING_CONTRACT",
                "message": "Contract number is missing",
                "where": "part_I.contract_number"
            })
    except Exception as e:
        logger.error(f"Error during validation: {str(e)}")
        errors.append({
            "code": "VALIDATION_ERROR",
            "message": f"Validation failed: {str(e)}",
            "where": "validation"
        })

    return {"errors": errors, "warnings": warnings}
