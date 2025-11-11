import re
import pdfplumber
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from .config import load_config
import logging

logger = logging.getLogger(__name__)

def extract_from_pdfs(company_coc_path: Optional[str], packing_slip_path: Optional[str]) -> Dict[str, Any]:
    """Extract data from PDFs using pdfplumber"""

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

    # Extract from Company COC
    if company_coc_path and Path(company_coc_path).exists():
        logger.info(f"Extracting from Company COC: {company_coc_path}")
        coc_data = extract_company_coc(company_coc_path)
        result["extracted"]["from_company_coc"] = coc_data
        logger.info(f"Extracted COC data: {coc_data}")
    else:
        logger.warning(f"Company COC not provided or not found: {company_coc_path}")

    # Extract from Packing Slip
    if packing_slip_path and Path(packing_slip_path).exists():
        logger.info(f"Extracting from Packing Slip: {packing_slip_path}")
        ps_data = extract_packing_slip(packing_slip_path)
        result["extracted"]["from_packing_slip"] = ps_data
        logger.info(f"Extracted Packing Slip data: {ps_data}")
    else:
        logger.warning(f"Packing Slip not provided or not found: {packing_slip_path}")

    # Merge extracted data into part_I
    result["part_I"] = merge_extracted_data(
        result["extracted"]["from_company_coc"],
        result["extracted"]["from_packing_slip"]
    )

    logger.info(f"Merged part_I data: {result['part_I']}")

    return result


def extract_company_coc(pdf_path: str) -> Dict[str, Any]:
    """Extract data from Company COC PDF

    Expected format example:
    - Order: 697.12.5011.01
    - Shipment no: 6SH264587
    - Product: 20580903700; PNR-1000N WPTT
    - QTY: 100
    - Serial Numbers: NL13721, NL13722, ...
    - QA Signer: YESHAYA ORLY
    - Date: 20/Mar/2025
    """
    data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            # Get all text from first page
            if pdf.pages:
                text = pdf.pages[0].extract_text()
                logger.debug(f"COC PDF text (first 500 chars): {text[:500]}")

                # Extract Contract/Order number
                # Pattern: "Order 697.12.5011.01" or "Contract 697.12.5011.01"
                contract_patterns = [
                    r'Order[:\s]+(\d+\.\d+\.\d+\.\d+)',
                    r'Contract[:\s]+(\d+\.\d+\.\d+\.\d+)',
                    r'Order\s+No[:\s]+(\d+\.\d+\.\d+\.\d+)',
                ]
                for pattern in contract_patterns:
                    contract_match = re.search(pattern, text, re.IGNORECASE)
                    if contract_match:
                        data['contract_number'] = contract_match.group(1)
                        logger.info(f"Found contract number: {data['contract_number']}")
                        break

                # Extract Shipment number
                # Pattern: "Shipment no. 6SH264587" or "Shipment: 6SH264587"
                shipment_patterns = [
                    r'Shipment\s+no[.:\s]+(\w+)',
                    r'Shipment[:\s]+(\w+)',
                ]
                for pattern in shipment_patterns:
                    shipment_match = re.search(pattern, text, re.IGNORECASE)
                    if shipment_match:
                        data['shipment_no'] = shipment_match.group(1)
                        logger.info(f"Found shipment number: {data['shipment_no']}")
                        break

                # Extract Product info
                # Pattern: "20580903700 PNR-1000N WPTT" or similar
                # Need to be careful not to capture too much
                product_patterns = [
                    r'(\d{11})\s+(PNR-\S+\s+\w+)',  # More specific: code + PNR-XXX + one word
                    r'(\d{11})[;\s]+(PNR-[\w-]+(?:\s+\w+)?)',  # code; PNR-XXX optionally one more word
                    r'(\d{11})\s+([\w-]+Radio[\w\s-]*)',
                ]
                for pattern in product_patterns:
                    product_match = re.search(pattern, text)
                    if product_match:
                        data['product_code'] = product_match.group(1)
                        data['product_name'] = product_match.group(2).strip()
                        data['product_description'] = f"{product_match.group(1)}; {product_match.group(2).strip()}"
                        logger.info(f"Found product: {data['product_description']}")
                        break

                # Extract Quantity
                # Pattern: Look for quantity field - should be 1-4 digits, not 11 digits
                # Avoid matching product codes (11 digits)
                qty_patterns = [
                    r'(?:QTY|Quantity)\s+(?:Order|Shipped)[:\s]+(\d{1,4})(?:\s|$)',  # 1-4 digits only
                    r'Quantity[:\s]+(\d{1,4})(?:\s|$)',
                    r'QTY[:\s]+(\d{1,4})(?:\s|$)',
                    r'(?:QTY|Quantity).*?(?:Shipped|Delivered)[:\s]+(\d{1,4})',
                ]
                for pattern in qty_patterns:
                    qty_match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                    if qty_match:
                        qty_value = int(qty_match.group(1))
                        # Sanity check - quantity should be reasonable (1-10000)
                        if 1 <= qty_value <= 10000:
                            data['quantity'] = qty_value
                            logger.info(f"Found quantity: {data['quantity']}")
                            break

                # Extract Serial Numbers
                # Pattern: Multiple lines with format "NL13721", "NL13722", etc.
                # Look for the serial number section and extract all NL##### patterns
                serial_section_match = re.search(r'Serial\s+Number.*?(?=We certify|Quality|$)', text, re.DOTALL | re.IGNORECASE)
                if serial_section_match:
                    serial_text = serial_section_match.group(0)
                    serials = re.findall(r'NL\d{5}', serial_text)  # NL followed by exactly 5 digits
                    if serials:
                        data['serials'] = serials
                        data['serial_count'] = len(serials)
                        logger.info(f"Found {len(serials)} serial numbers (first: {serials[0]}, last: {serials[-1]})")
                else:
                    # Fallback: search entire document for NL##### patterns
                    serials = re.findall(r'NL\d{5}', text)
                    if serials:
                        data['serials'] = serials
                        data['serial_count'] = len(serials)
                        logger.info(f"Found {len(serials)} serial numbers via fallback search")

                # Extract Customer/Acquirer
                # Pattern: "NETHERLANDS MINISTRY OF DEFENCE" or similar
                customer_patterns = [
                    r'(?:Customer|Acquirer)[:\s]+\n?([\w\s]+?)(?:\n\n|\nPart\s+number|$)',
                    r'(NETHERLANDS MINISTRY OF DEFENCE)',
                ]
                for pattern in customer_patterns:
                    customer_match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                    if customer_match:
                        if len(customer_match.groups()) > 0:
                            data['customer'] = customer_match.group(1).strip()
                        else:
                            data['customer'] = customer_match.group(0).strip()
                        # Clean up any extra newlines or "Customer" prefix
                        data['customer'] = re.sub(r'^Customer\s*', '', data['customer'], flags=re.IGNORECASE)
                        data['customer'] = data['customer'].strip()
                        logger.info(f"Found customer: {data['customer']}")
                        break

                # Extract QA Signer and Date
                # Pattern: "YESHAYA ORLY 20/Mar/2025" or similar
                # Need to capture name (letters and spaces only) before date
                qa_patterns = [
                    r'Quality\s+Authority.*?\n([A-Z][A-Z\s]+?)\s+\d+\s+(\d+/\w+/\d+)',  # Name, then number, then date
                    r'Quality\s+Authority.*?\n([A-Z][A-Z\s]+?)\s+(\d+/\w+/\d+)',  # Name directly before date
                    r'QA.*?\n([A-Z][A-Z\s]+?)\s+(\d+/\w+/\d+)',
                ]
                for pattern in qa_patterns:
                    qa_match = re.search(pattern, text, re.DOTALL)
                    if qa_match:
                        data['qa_signer'] = qa_match.group(1).strip()
                        data['date'] = qa_match.group(2)
                        logger.info(f"Found QA signer: {data['qa_signer']}, Date: {data['date']}")
                        break

    except Exception as e:
        logger.error(f"Error extracting from Company COC: {str(e)}", exc_info=True)
        data['extraction_error'] = str(e)

    return data


def extract_packing_slip(pdf_path: str) -> Dict[str, Any]:
    """Extract data from Packing Slip PDF

    Expected format example:
    - Ship To: [address]
    - Contract: 697.12.5011.01
    - Customer Item: 123456
    - Part No: 20580903700
    - Description: PNR-1000N WPTT
    - Quantity: 100.00 EA
    """
    data = {}

    try:
        with pdfplumber.open(pdf_path) as pdf:
            if pdf.pages:
                text = pdf.pages[0].extract_text()
                logger.debug(f"Packing Slip PDF text (first 500 chars): {text[:500]}")

                # Extract Ship To address
                ship_to_match = re.search(r'Ship\s+To[:\s]+([\s\S]+?)(?:Sold\s+To|Contract|Our\s+Reference)', text, re.IGNORECASE)
                if ship_to_match:
                    data['ship_to'] = ship_to_match.group(1).strip()
                    # Clean up - take first few lines, remove "Sold To:" if it appears
                    ship_lines = data['ship_to'].split('\n')[:5]
                    cleaned_lines = []
                    for line in ship_lines:
                        line = line.strip()
                        # Skip lines that contain "Sold To" or "BCD"
                        if line and not re.search(r'Sold\s+To|^BCD\s', line, re.IGNORECASE):
                            cleaned_lines.append(line)
                    data['ship_to'] = '\n'.join(cleaned_lines)
                    logger.info(f"Found ship to: {data['ship_to'][:50]}...")

                # Extract Contract number
                contract_patterns = [
                    r'Contract[:\s]+[\w\s]*?([\d.]+)',
                    r'Our\s+Reference[:\s]+([\d.]+)',
                ]
                for pattern in contract_patterns:
                    contract_match = re.search(pattern, text, re.IGNORECASE)
                    if contract_match:
                        data['contract_number'] = contract_match.group(1).strip()
                        logger.info(f"Found contract: {data['contract_number']}")
                        break

                # Extract Customer Item
                cust_item_match = re.search(r'Customers?\s+Item[:\s]+(\d+)', text, re.IGNORECASE)
                if cust_item_match:
                    data['customer_item'] = cust_item_match.group(1)
                    logger.info(f"Found customer item: {data['customer_item']}")

                # Extract Part Number and Description
                # Pattern: "20580903700 PNR-1000N WPTT 100.00 EA"
                part_patterns = [
                    r'(\d{11})\s+([\w\s-]+?)\s+(\d+\.\d+)\s+EA',
                    r'Part\s+No[:\s]+(\d{11}).*?Description[:\s]+([\w\s-]+)',
                ]
                for pattern in part_patterns:
                    part_match = re.search(pattern, text, re.DOTALL)
                    if part_match:
                        data['part_no'] = part_match.group(1)
                        data['description'] = part_match.group(2).strip()
                        if len(part_match.groups()) >= 3:
                            try:
                                data['quantity'] = int(float(part_match.group(3)))
                            except:
                                pass
                        logger.info(f"Found part: {data['part_no']} - {data.get('description')}")
                        break

                # Extract Quantity if not found above
                if 'quantity' not in data:
                    qty_patterns = [
                        r'(\d+\.\d+)\s+EA',
                        r'Quantity[:\s]+(\d+)',
                    ]
                    for pattern in qty_patterns:
                        qty_match = re.search(pattern, text, re.IGNORECASE)
                        if qty_match:
                            try:
                                data['quantity'] = int(float(qty_match.group(1)))
                                logger.info(f"Found quantity: {data['quantity']}")
                            except:
                                pass
                            break

    except Exception as e:
        logger.error(f"Error extracting from Packing Slip: {str(e)}", exc_info=True)
        data['extraction_error'] = str(e)

    return data


def merge_extracted_data(coc_data: Dict, ps_data: Dict) -> Dict[str, Any]:
    """Merge data from both sources, preferring COC data when available

    Priority:
    1. Company COC data (primary source for most fields)
    2. Packing Slip data (fallback or additional fields)
    """
    merged = {}

    # Contract number - prefer PS (more reliable), fallback to COC
    merged['contract_number'] = ps_data.get('contract_number') or coc_data.get('contract_number') or ''

    # Shipment number - only from COC
    merged['shipment_no'] = coc_data.get('shipment_no') or ''

    # Quantity - prefer PS (more reliable format), fallback to COC
    merged['quantity'] = ps_data.get('quantity') or coc_data.get('quantity') or 0

    # Serial numbers - only from COC
    merged['serials'] = coc_data.get('serials', [])
    merged['serial_count'] = len(merged['serials'])

    # Product description - build from available data
    product_parts = []
    if coc_data.get('product_code'):
        product_parts.append(coc_data['product_code'])
    elif ps_data.get('part_no'):
        product_parts.append(ps_data['part_no'])

    if coc_data.get('product_name'):
        product_parts.append(coc_data['product_name'])
    elif ps_data.get('description'):
        product_parts.append(ps_data['description'])

    if ps_data.get('customer_item'):
        product_parts.append(f"Customer Item {ps_data['customer_item']}")

    merged['product_description'] = '; '.join(product_parts) if product_parts else ''

    # Customer/Acquirer - from COC or Ship To from PS
    merged['customer'] = coc_data.get('customer') or ''
    merged['ship_to'] = ps_data.get('ship_to') or ''

    # Date - from COC
    merged['date'] = coc_data.get('date') or ''

    # QA Signer - from COC
    merged['qa_signer'] = coc_data.get('qa_signer') or ''

    logger.info(f"Merged data - contract: {merged.get('contract_number')}, "
                f"shipment: {merged.get('shipment_no')}, "
                f"quantity: {merged.get('quantity')}, "
                f"serials: {merged.get('serial_count')}")

    return merged


def normalize_date(date_str: str) -> str:
    """Normalize date to DD/MMM/YYYY format

    Handles formats like:
    - 20/Mar/2025 (already correct)
    - 20-03-2025
    - 2025-03-20
    - 03/20/2025
    """
    if not date_str:
        return ""

    # If already in correct format, return as-is
    if re.match(r'\d{2}/\w{3}/\d{4}', date_str):
        return date_str

    # Try parsing various formats
    formats = [
        '%d/%m/%Y',
        '%Y-%m-%d',
        '%m/%d/%Y',
        '%d-%m-%Y',
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%d/%b/%Y')
        except ValueError:
            continue

    # If no format matches, return original
    logger.warning(f"Could not normalize date: {date_str}")
    return date_str
