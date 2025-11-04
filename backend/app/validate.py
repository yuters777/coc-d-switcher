from typing import Dict, Any, List
import re
from datetime import datetime

def validate_conversion(data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
    """Validate conversion data with enhanced rules"""

    errors = []
    warnings = []

    part_i = data.get("part_I", {})

    # Handle malformed data
    if part_i is None:
        part_i = {}

    # Check serial count matches quantity
    serials = part_i.get("serials", [])
    items = part_i.get("items", [])

    if items:
        quantity = items[0].get("quantity", 0)
        if len(serials) != quantity:
            errors.append({
                "code": "SERIAL_COUNT_MISMATCH",
                "message": f"Serial count ({len(serials)}) does not match quantity ({quantity})",
                "where": "part_I.serials"
            })

    # Check contract number present
    if not part_i.get("contract_number"):
        errors.append({
            "code": "MISSING_CONTRACT",
            "message": "Contract number is missing",
            "where": "part_I.contract_number"
        })

    return {"errors": errors, "warnings": warnings}
