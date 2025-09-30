from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class SupplierBlock(BaseModel):
    name: str
    address: str
    contact: str
    email: str

class AcquirerBlock(BaseModel):
    name: str
    address_lines: List[str]

class Item(BaseModel):
    contract_item: str
    product_description_or_part: str
    quantity: int
    shipment_document: str
    undelivered_quantity: Optional[int] = None

class ValidationIssue(BaseModel):
    code: str
    message: str
    where: str

class ValidationResult(BaseModel):
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]

class ConversionOutput(BaseModel):
    pass  # Full implementation would go here

class JobData(BaseModel):
    id: str
    name: str
    submitted_by: str
    status: str
    created_at: datetime
    updated_at: datetime
