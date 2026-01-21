"""
AI-002: Document OCR and Vision Service
Extract text and data from documents using AI vision
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import base64


class DocumentType(str, Enum):
    """Supported document types."""
    INVOICE = "invoice"
    RECEIPT = "receipt"
    PAN_CARD = "pan_card"
    AADHAAR = "aadhaar"
    BANK_STATEMENT = "bank_statement"
    SALARY_SLIP = "salary_slip"
    FORM_16 = "form_16"
    GST_RETURN = "gst_return"
    UNKNOWN = "unknown"


@dataclass
class ExtractionResult:
    """Document extraction result."""
    document_type: DocumentType
    extracted_data: Dict[str, Any]
    confidence: float
    raw_text: str
    fields_found: List[str]
    processing_time_ms: int


class DocumentAIService:
    """
    AI-powered document processing service.

    Features:
    - OCR text extraction
    - Document type classification
    - Structured data extraction
    - Indian document format support (PAN, Aadhaar, GST)
    """

    # Field extraction patterns for Indian documents
    DOCUMENT_FIELDS = {
        DocumentType.INVOICE: [
            "invoice_number", "invoice_date", "due_date", "vendor_name",
            "vendor_gstin", "total_amount", "cgst", "sgst", "igst",
            "line_items", "billing_address", "shipping_address"
        ],
        DocumentType.PAN_CARD: [
            "pan_number", "name", "father_name", "date_of_birth", "signature"
        ],
        DocumentType.AADHAAR: [
            "aadhaar_number", "name", "date_of_birth", "gender", "address"
        ],
        DocumentType.BANK_STATEMENT: [
            "account_number", "account_holder", "bank_name", "ifsc_code",
            "statement_period", "opening_balance", "closing_balance", "transactions"
        ],
        DocumentType.SALARY_SLIP: [
            "employee_name", "employee_id", "month", "basic", "hra",
            "special_allowance", "pf_deduction", "esi_deduction", "tds",
            "gross_salary", "net_salary"
        ],
        DocumentType.FORM_16: [
            "employee_name", "pan", "tan", "assessment_year",
            "gross_salary", "exemptions", "deductions", "taxable_income",
            "tax_payable", "tax_deducted"
        ],
        DocumentType.GST_RETURN: [
            "gstin", "return_period", "filing_type", "turnover",
            "tax_payable", "itc_claimed", "tax_paid"
        ],
    }

    def __init__(self, ai_service):
        """Initialize with core AI service."""
        self.ai_service = ai_service

    async def extract_from_image(
        self,
        image_data: bytes,
        document_type: Optional[DocumentType] = None,
        mime_type: str = "image/png"
    ) -> ExtractionResult:
        """
        Extract data from document image.

        Args:
            image_data: Raw image bytes
            document_type: Optional document type hint
            mime_type: Image MIME type

        Returns:
            ExtractionResult with extracted data
        """
        import time
        start = time.time()

        # Encode image for vision API
        image_b64 = base64.b64encode(image_data).decode('utf-8')

        # Build extraction prompt
        type_hint = f"Document type: {document_type.value}" if document_type else "Auto-detect document type"
        fields = self.DOCUMENT_FIELDS.get(document_type, []) if document_type else []

        prompt = f"""Analyze this Indian document image and extract all relevant information.

{type_hint}

{f"Expected fields: {', '.join(fields)}" if fields else "Extract all visible fields."}

Return a JSON object with:
1. "document_type": detected type
2. "extracted_data": object with field names and values
3. "confidence": overall confidence 0-1
4. "raw_text": all visible text
5. "fields_found": list of field names extracted

Important:
- Parse Indian formats (DD/MM/YYYY dates, INR amounts)
- Validate PAN format: AAAAA9999A
- Validate GSTIN format: 22AAAAA0000A1Z5
- Validate Aadhaar format: XXXX XXXX XXXX
"""

        # In production, use Claude's vision API
        # This is a simulation
        detected_type = document_type or DocumentType.UNKNOWN

        # Simulated extraction based on document type
        extracted = self._simulate_extraction(detected_type)

        processing_time = int((time.time() - start) * 1000)

        return ExtractionResult(
            document_type=detected_type,
            extracted_data=extracted,
            confidence=0.92,
            raw_text="[Simulated OCR text]",
            fields_found=list(extracted.keys()),
            processing_time_ms=processing_time
        )

    async def extract_from_pdf(
        self,
        pdf_data: bytes,
        document_type: Optional[DocumentType] = None
    ) -> List[ExtractionResult]:
        """Extract data from PDF document (may have multiple pages)."""
        # In production, convert PDF to images and process each page
        # This is a simulation
        return [await self.extract_from_image(pdf_data, document_type, "application/pdf")]

    async def classify_document(self, image_data: bytes) -> Dict[str, Any]:
        """Classify document type without full extraction."""
        prompt = """Analyze this document image and classify it.

Return JSON with:
- document_type: one of [invoice, receipt, pan_card, aadhaar, bank_statement, salary_slip, form_16, gst_return, unknown]
- confidence: 0-1
- indicators: list of features that indicate the type
"""
        # Simulated classification
        return {
            "document_type": "invoice",
            "confidence": 0.95,
            "indicators": ["GST header", "Line items table", "Tax breakup"]
        }

    async def validate_extracted_data(
        self,
        data: Dict[str, Any],
        document_type: DocumentType
    ) -> Dict[str, Any]:
        """Validate extracted data against known formats."""
        import re

        validations = {}

        if document_type == DocumentType.PAN_CARD:
            pan = data.get("pan_number", "")
            validations["pan_format"] = bool(re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan))

        elif document_type == DocumentType.AADHAAR:
            aadhaar = data.get("aadhaar_number", "").replace(" ", "")
            validations["aadhaar_format"] = len(aadhaar) == 12 and aadhaar.isdigit()

        elif document_type == DocumentType.INVOICE:
            gstin = data.get("vendor_gstin", "")
            validations["gstin_format"] = bool(re.match(
                r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$',
                gstin
            ))

        return {
            "data": data,
            "validations": validations,
            "is_valid": all(validations.values()) if validations else True
        }

    def _simulate_extraction(self, doc_type: DocumentType) -> Dict[str, Any]:
        """Simulate extraction for demo purposes."""
        if doc_type == DocumentType.INVOICE:
            return {
                "invoice_number": "INV-2024-001234",
                "invoice_date": "15/01/2024",
                "due_date": "14/02/2024",
                "vendor_name": "Tech Solutions Pvt Ltd",
                "vendor_gstin": "27AABCT1234F1ZD",
                "total_amount": 118000.00,
                "cgst": 9000.00,
                "sgst": 9000.00,
                "igst": 0.00,
                "line_items": [
                    {"description": "Software License", "qty": 1, "rate": 100000, "amount": 100000}
                ]
            }
        elif doc_type == DocumentType.PAN_CARD:
            return {
                "pan_number": "ABCDE1234F",
                "name": "RAJESH KUMAR",
                "father_name": "SURESH KUMAR",
                "date_of_birth": "15/08/1985"
            }
        elif doc_type == DocumentType.SALARY_SLIP:
            return {
                "employee_name": "John Doe",
                "employee_id": "EMP001",
                "month": "January 2024",
                "basic": 50000,
                "hra": 20000,
                "special_allowance": 15000,
                "pf_deduction": 6000,
                "esi_deduction": 0,
                "tds": 8500,
                "gross_salary": 85000,
                "net_salary": 70500
            }
        return {}
