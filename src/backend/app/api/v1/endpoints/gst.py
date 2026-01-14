"""
GST API Endpoints - India GST Compliance Module
Routes for GSTR-1, GSTR-3B, reconciliation, and ITC management
"""
from decimal import Decimal
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.gst_service import GSTService, GSTCalculator, GSTINValidator
from app.schemas.gst import (
    # Request schemas
    GSTReturnCreate,
    GSTR1GenerateRequest,
    GSTR3BGenerateRequest,
    ReconciliationMatchRequest,
    GSTINValidationRequest,
    GSTCalculationRequest,
    GSTReturnListRequest,
    # Response schemas
    GSTReturnResponse,
    GSTReturnSummary,
    GSTR1GenerateResponse,
    GSTR3BGenerateResponse,
    ReconciliationReport,
    ITCEligibilityResponse,
    HSNSummaryResponse,
    GSTCalculation,
    GSTINValidationResponse,
    GSTDashboardResponse,
    PaginatedResponse,
    # Enums
    GSTReturnTypeEnum,
    GSTReturnStatusEnum,
)

router = APIRouter()


# ----- GST Returns List -----

@router.get(
    "/returns",
    response_model=PaginatedResponse,
    summary="List GST returns",
    description="Get all GST returns with optional filters for type, status, and period."
)
async def list_gst_returns(
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: Optional[str] = Query(None, min_length=15, max_length=15, description="Filter by GSTIN"),
    return_type: Optional[GSTReturnTypeEnum] = Query(None, description="Filter by return type (gstr1, gstr3b, etc.)"),
    status: Optional[GSTReturnStatusEnum] = Query(None, description="Filter by status"),
    financial_year: Optional[str] = Query(None, pattern=r"^\d{4}-\d{2}$", description="Financial year (e.g., 2024-25)"),
    page: int = Query(default=1, ge=1, description="Page number"),
    page_size: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    List all GST returns for a company.

    Supports filtering by:
    - GSTIN (for multi-GSTIN companies)
    - Return type (GSTR-1, GSTR-3B, etc.)
    - Filing status
    - Financial year

    Returns paginated list of returns with summary information.
    """
    service = GSTService(db)
    result = await service.get_returns(
        company_id=company_id,
        gstin=gstin,
        return_type=return_type,
        status=status,
        financial_year=financial_year,
        page=page,
        page_size=page_size
    )

    return PaginatedResponse(
        items=result["items"],
        total=result["total"],
        page=result["page"],
        page_size=result["page_size"],
        total_pages=result["total_pages"]
    )


# ----- GSTR-1 Endpoints -----

@router.post(
    "/returns/gstr1/generate",
    response_model=GSTR1GenerateResponse,
    summary="Generate GSTR-1",
    description="Generate GSTR-1 from sales invoices for a given period."
)
async def generate_gstr1(
    request: GSTR1GenerateRequest,
    company_id: UUID = Query(..., description="Company UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate GSTR-1 (Outward Supplies Return) from sales invoices.

    This endpoint:
    1. Fetches all approved invoices for the period
    2. Categorizes into B2B, B2CL, B2CS based on:
       - B2B: Sales to registered dealers (with GSTIN)
       - B2CL: Inter-state B2C sales > Rs.2.5 lakhs
       - B2CS: Other B2C sales (consolidated by state/rate)
    3. Includes credit notes and debit notes
    4. Generates HSN summary

    GST Rules Applied:
    - B2B threshold: Any amount (invoice-wise for registered)
    - B2CL threshold: > Rs.2,50,000 for inter-state unregistered
    - B2CS: Consolidated by state code and tax rate

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    # Validate GSTIN
    validation = await service.validate_gstin(request.gstin)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GSTIN: {', '.join(validation.errors)}"
        )

    result = await service.generate_gstr1(
        company_id=company_id,
        gstin=request.gstin,
        period=request.period,
        include_draft=request.include_draft_invoices
    )

    return GSTR1GenerateResponse(
        return_id=UUID(result["return_id"]),
        period=result["period"],
        status=result["status"],
        summary=result["summary"],
        b2b_count=result["summary"]["b2b"]["count"],
        b2c_count=result["summary"]["b2cl"]["count"] + len(result["summary"].get("b2cs", {})),
        credit_notes_count=result["summary"]["cdnr"]["count"],
        debit_notes_count=0,  # TODO: Add debit notes count
        total_taxable_value=Decimal(str(result["total_taxable_value"])),
        total_tax=Decimal(str(result["total_tax"]))
    )


@router.get(
    "/returns/gstr1/{period}",
    summary="Get GSTR-1 data",
    description="Get GSTR-1 data for a specific period."
)
async def get_gstr1(
    period: str,
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get GSTR-1 data for a specific period.

    Returns complete GSTR-1 data including:
    - B2B invoices (with recipient GSTIN, invoice details, tax breakdown)
    - B2CL invoices (large inter-state B2C)
    - B2CS summary (consolidated small B2C by state/rate)
    - Credit notes and debit notes
    - Export invoices
    - HSN summary

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    result = await service.get_gstr1_data(
        company_id=company_id,
        gstin=gstin,
        period=period
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GSTR-1 not found for period {period}"
        )

    return result


# ----- GSTR-3B Endpoints -----

@router.post(
    "/returns/gstr3b/generate",
    response_model=GSTR3BGenerateResponse,
    summary="Generate GSTR-3B",
    description="Generate GSTR-3B summary return from invoices and bills."
)
async def generate_gstr3b(
    request: GSTR3BGenerateRequest,
    company_id: UUID = Query(..., description="Company UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate GSTR-3B (Monthly Summary Return).

    GSTR-3B contains:
    - 3.1: Outward supplies and tax liability
    - 4: Input Tax Credit (ITC) available
    - 5: Exempt/Nil/Non-GST inward supplies
    - 6: Tax payable and payment

    This endpoint:
    1. Calculates output tax from sales invoices
    2. Calculates eligible ITC from purchase bills
    3. Applies ITC utilization rules (IGST -> CGST -> SGST)
    4. Computes net tax payable

    ITC Utilization Order (per GST rules):
    1. IGST credit used against IGST liability first
    2. Remaining IGST credit used against CGST, then SGST
    3. CGST credit used against CGST, then IGST
    4. SGST credit used against SGST, then IGST

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    # Validate GSTIN
    validation = await service.validate_gstin(request.gstin)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GSTIN: {', '.join(validation.errors)}"
        )

    result = await service.generate_gstr3b_summary(
        company_id=company_id,
        gstin=request.gstin,
        period=request.period,
        auto_calculate_itc=request.auto_calculate_itc
    )

    return GSTR3BGenerateResponse(
        return_id=UUID(result["return_id"]),
        period=result["period"],
        status=result["status"],
        liability_summary=result["liability_summary"],
        itc_summary=result["itc_summary"],
        net_tax_payable=result["net_tax_payable"],
        total_tax_payable=Decimal(str(result["total_tax_payable"]))
    )


@router.get(
    "/returns/gstr3b/{period}",
    summary="Get GSTR-3B data",
    description="Get GSTR-3B summary data for a specific period."
)
async def get_gstr3b(
    period: str,
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get GSTR-3B data for a specific period.

    Returns complete GSTR-3B summary including:
    - Outward supplies liability (taxable, zero-rated, nil, reverse charge)
    - ITC available and utilized
    - Net tax payable by tax head (CGST, SGST, IGST, Cess)
    - Cash and credit ledger balances

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    result = await service.get_gstr3b_data(
        company_id=company_id,
        gstin=gstin,
        period=period
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"GSTR-3B not found for period {period}"
        )

    return result


# ----- Reconciliation Endpoints -----

@router.get(
    "/reconciliation/{period}",
    response_model=ReconciliationReport,
    summary="Get reconciliation report",
    description="Get GSTR-2A reconciliation report for a period."
)
async def get_reconciliation(
    period: str,
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get GSTR-2A vs Books reconciliation report.

    Compares:
    - Purchase invoices in your books
    - GSTR-2A data (supplier's filed GSTR-1)

    Returns:
    - Matched invoices (found in both with matching values)
    - Value mismatches (found in both but amounts differ)
    - Only in books (not filed by supplier)
    - Only in GSTR-2A (not recorded in your books)

    This is critical for ITC eligibility as per GST rules.

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    report = await service.reconcile_gstr2a(
        company_id=company_id,
        gstin=gstin,
        period=period
    )

    return report


@router.post(
    "/reconciliation/{period}/match",
    response_model=ReconciliationReport,
    summary="Auto-match invoices",
    description="Run auto-matching for GSTR-2A reconciliation."
)
async def match_invoices(
    period: str,
    request: ReconciliationMatchRequest,
    company_id: UUID = Query(..., description="Company UUID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Run auto-matching for GSTR-2A reconciliation.

    Matching Logic:
    1. Match by supplier GSTIN + Invoice number (exact)
    2. Match by supplier GSTIN + Invoice date + Amount (fuzzy)
    3. Apply tolerance for minor amount differences

    Options:
    - tolerance_amount: Allow small differences (default Rs.1)
    - auto_accept_matched: Automatically accept matched invoices

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    report = await service.reconcile_gstr2a(
        company_id=company_id,
        gstin=request.gstin,
        period=period,
        tolerance_amount=request.tolerance_amount
    )

    return report


# ----- ITC Endpoints -----

@router.get(
    "/itc/eligible",
    response_model=ITCEligibilityResponse,
    summary="Get eligible ITC",
    description="Get Input Tax Credit eligibility for a period."
)
async def get_eligible_itc(
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    period: str = Query(..., pattern=r"^\d{6}$", description="Period (MMYYYY)"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get Input Tax Credit (ITC) eligibility for a period.

    ITC Eligibility Conditions (Section 16 of CGST Act):
    1. Possession of tax invoice or debit note
    2. Goods/services received
    3. Tax actually paid to government (supplier filed return)
    4. Return filed by the recipient
    5. Payment made within 180 days from invoice date

    Returns:
    - Eligible ITC (all conditions met)
    - Ineligible ITC (conditions not met)
    - At-risk ITC (approaching 180-day deadline)

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    result = await service.calculate_itc_eligibility(
        company_id=company_id,
        gstin=gstin,
        period=period
    )

    return result


# ----- HSN Summary -----

@router.get(
    "/hsn-summary/{period}",
    response_model=HSNSummaryResponse,
    summary="Get HSN summary",
    description="Get HSN/SAC summary for GSTR-1 filing."
)
async def get_hsn_summary(
    period: str,
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get HSN/SAC summary for GSTR-1.

    Groups all invoice items by HSN/SAC code with:
    - Total quantity
    - Taxable value
    - Tax breakup (CGST, SGST, IGST, Cess)

    HSN Codes:
    - 4 digits: Turnover > Rs.5 crore (mandatory)
    - 6 digits: Turnover Rs.1.5-5 crore
    - 8 digits: Export transactions

    SAC Codes: For services (starting with 99)

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    result = await service.prepare_hsn_summary(
        company_id=company_id,
        gstin=gstin,
        period=period
    )

    return result


# ----- GSTIN Validation -----

@router.post(
    "/validate-gstin",
    response_model=GSTINValidationResponse,
    summary="Validate GSTIN",
    description="Validate GSTIN format and checksum."
)
async def validate_gstin(
    request: GSTINValidationRequest
):
    """
    Validate GSTIN format and extract information.

    GSTIN Format: 22AAAAA0000A1Z5 (15 characters)
    - Position 1-2: State Code (01-37)
    - Position 3-12: PAN (10 characters)
    - Position 13: Entity Number (1-9, A-Z)
    - Position 14: Z (default)
    - Position 15: Checksum digit

    Validations:
    1. Length check (must be 15 characters)
    2. State code validation (01-37)
    3. PAN format validation
    4. Checksum verification (Luhn mod 36)

    Returns:
    - Validity status
    - Extracted state code and name
    - Extracted PAN
    - Entity type (Proprietorship, Company, etc.)
    - Checksum validation result
    """
    return GSTINValidator.validate(request.gstin)


# ----- GST Calculation -----

@router.post(
    "/calculate",
    response_model=GSTCalculation,
    summary="Calculate GST",
    description="Calculate GST on an amount."
)
async def calculate_gst(
    request: GSTCalculationRequest
):
    """
    Calculate GST on an amount.

    Supports:
    - Exclusive calculation (GST on top of amount)
    - Inclusive calculation (GST extracted from amount)
    - Intra-state (CGST + SGST, split equally)
    - Inter-state (IGST only)
    - Cess calculation (if applicable)

    Valid GST Rates: 0%, 5%, 12%, 18%, 28%

    Example:
    - Amount: Rs.10,000
    - GST Rate: 18%
    - Intra-state: CGST 9% (Rs.900) + SGST 9% (Rs.900) = Rs.1,800
    - Inter-state: IGST 18% (Rs.1,800)
    """
    return GSTCalculator.calculate_gst(
        amount=request.amount,
        gst_rate=request.gst_rate,
        cess_rate=request.cess_rate,
        is_inclusive=request.is_inclusive,
        is_igst=request.is_igst
    )


# ----- Dashboard -----

@router.get(
    "/dashboard",
    response_model=GSTDashboardResponse,
    summary="GST compliance dashboard",
    description="Get GST compliance dashboard with filing status and alerts."
)
async def get_gst_dashboard(
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get GST compliance dashboard.

    Provides:
    - Current period filing status (GSTR-1, GSTR-3B)
    - Upcoming due dates
    - Tax liability summary
    - ITC summary
    - Reconciliation status
    - Pending actions
    - Recent returns
    - Compliance alerts

    Due Dates (Regular taxpayers):
    - GSTR-1: 11th of next month
    - GSTR-3B: 20th of next month

    Alerts for:
    - Approaching deadlines
    - ITC at risk (180-day rule)
    - Unreconciled invoices
    - Filing delays
    """
    service = GSTService(db)

    # Validate GSTIN
    validation = await service.validate_gstin(gstin)
    if not validation.is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid GSTIN: {', '.join(validation.errors)}"
        )

    return await service.get_gst_dashboard(
        company_id=company_id,
        gstin=gstin
    )


# ----- GST Liability -----

@router.get(
    "/liability/{period}",
    summary="Get GST liability",
    description="Get GST liability summary for a period."
)
async def get_gst_liability(
    period: str,
    company_id: UUID = Query(..., description="Company UUID"),
    gstin: str = Query(..., min_length=15, max_length=15, description="Company GSTIN"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get GST liability for a period.

    Returns:
    - Output tax (from sales invoices)
    - Input tax credit (from purchase bills)
    - Net liability (output - input)

    Breakdown by tax head: CGST, SGST, IGST, Cess

    Period format: MMYYYY (e.g., 012025 for January 2025)
    """
    service = GSTService(db)

    return await service.get_gst_liability(
        company_id=company_id,
        gstin=gstin,
        period=period
    )


# ----- State Codes -----

@router.get(
    "/state-codes",
    summary="Get Indian state codes",
    description="Get list of all Indian state codes for GST."
)
async def get_state_codes():
    """
    Get list of all Indian state codes.

    Used for:
    - GSTIN first 2 digits
    - Place of supply in invoices
    - Determining intra/inter-state supply

    State codes range from 01 (Jammu & Kashmir) to 38 (Ladakh).
    """
    from app.models.gst import INDIAN_STATE_CODES

    return {
        "state_codes": [
            {"code": code, "name": name}
            for code, name in sorted(INDIAN_STATE_CODES.items())
        ]
    }


# ----- GST Rates -----

@router.get(
    "/rates",
    summary="Get GST rates",
    description="Get standard GST rates in India."
)
async def get_gst_rates():
    """
    Get standard GST rates in India.

    Standard Rates:
    - 0%: Essential commodities (unpacked food grains, etc.)
    - 5%: Essential items (packaged food, economy hotels, etc.)
    - 12%: Standard goods (processed food, computers, etc.)
    - 18%: Standard rate (most goods and services)
    - 28%: Luxury goods (cars, AC, etc.)

    Additional Cess:
    - Applicable on luxury/sin goods
    - Cars: 1% to 22% additional
    - Tobacco: Specific cess amounts
    - Aerated drinks: 12% additional
    """
    return {
        "rates": [
            {"rate": 0, "description": "Exempt/Nil rated - Essential commodities"},
            {"rate": 5, "description": "Lower rate - Essential items, economy services"},
            {"rate": 12, "description": "Standard lower - Processed foods, computers"},
            {"rate": 18, "description": "Standard rate - Most goods and services"},
            {"rate": 28, "description": "Higher rate - Luxury items, automobiles"},
        ],
        "cess_applicable": [
            {"item": "Motor vehicles", "cess": "1% to 22%"},
            {"item": "Aerated beverages", "cess": "12%"},
            {"item": "Tobacco products", "cess": "Various specific rates"},
            {"item": "Coal and lignite", "cess": "Rs.400 per tonne"},
        ]
    }
