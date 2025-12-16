"""
TDS Compliance Endpoints - Phase 17
REST API endpoints for TDS on vendor payments
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.vendor import TDSSection
from app.models.tds import TDSDepositStatus, TDSCertificateStatus, TDS26QStatus
from app.schemas.tds import (
    TDSDeductionCreate,
    TDSDeductionResponse,
    TDSDeductionListResponse,
    TDSChallanCreate,
    TDSChallanResponse,
    TDSCertificateCreate,
    TDSCertificateResponse,
    TDS26QReturnCreate,
    TDS26QReturnResponse,
    TDSPayableSummary,
    TDSDashboardStats,
    TDSVendorSummary,
    TDSQuarterlyReport,
    TDSThresholdInfo,
)
from app.services.tds import (
    TDSService,
    TDSChallanService,
    TDSCertificateService,
    TDS26QService,
    TDSReportService,
)

router = APIRouter()


# ==================== TDS Deduction Endpoints ====================

@router.post("/deductions", response_model=TDSDeductionResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_deduction(
    deduction_data: TDSDeductionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a TDS deduction record"""
    try:
        deduction = await TDSService.create_deduction(db, deduction_data, current_user.id)
        return deduction
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/deductions", response_model=dict)
async def list_tds_deductions(
    financial_year: Optional[str] = Query(None, description="e.g., 2024-25"),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    tds_section: Optional[TDSSection] = Query(None),
    deposit_status: Optional[TDSDepositStatus] = Query(None),
    vendor_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List TDS deductions"""
    deductions, total = await TDSService.get_deductions(
        db,
        financial_year=financial_year,
        quarter=quarter,
        tds_section=tds_section,
        deposit_status=deposit_status,
        vendor_id=vendor_id,
        skip=skip,
        limit=limit,
    )

    items = []
    for d in deductions:
        items.append(TDSDeductionListResponse(
            id=d.id,
            tds_section=d.tds_section,
            vendor_id=d.vendor_id,
            vendor_name=d.vendor.vendor_name if d.vendor else "Unknown",
            vendor_pan=d.vendor_pan,
            deduction_date=d.deduction_date,
            gross_amount=d.gross_amount,
            total_tds=d.total_tds,
            deposit_status=d.deposit_status,
            certificate_status=d.certificate_status,
        ))

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.get("/deductions/{deduction_id}", response_model=TDSDeductionResponse)
async def get_tds_deduction(
    deduction_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS deduction by ID"""
    deduction = await TDSService.get_deduction(db, deduction_id)
    if not deduction:
        raise HTTPException(status_code=404, detail="TDS deduction not found")
    return deduction


# ==================== TDS Challan Endpoints ====================

@router.post("/challans", response_model=TDSChallanResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_challan(
    challan_data: TDSChallanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create TDS challan and link deductions"""
    try:
        challan = await TDSChallanService.create_challan(db, challan_data, current_user.id)
        return challan
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/challans", response_model=dict)
async def list_tds_challans(
    financial_year: Optional[str] = Query(None),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List TDS challans"""
    challans, total = await TDSChallanService.get_challans(
        db,
        financial_year=financial_year,
        quarter=quarter,
        skip=skip,
        limit=limit,
    )

    return {
        "items": [TDSChallanResponse.model_validate(c) for c in challans],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ==================== TDS Certificate Endpoints ====================

@router.post("/certificates/generate", response_model=TDSCertificateResponse, status_code=status.HTTP_201_CREATED)
async def generate_tds_certificate(
    cert_data: TDSCertificateCreate,
    deductor_tan: str = Query(..., max_length=10),
    deductor_name: str = Query(...),
    deductor_address: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate TDS certificate (Form 16A) for a vendor"""
    try:
        certificate = await TDSCertificateService.generate_certificate(
            db,
            cert_data,
            deductor_tan=deductor_tan,
            deductor_name=deductor_name,
            deductor_address=deductor_address or "",
            created_by=current_user.id,
        )
        return certificate
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/certificates", response_model=dict)
async def list_tds_certificates(
    vendor_id: Optional[UUID] = Query(None),
    financial_year: Optional[str] = Query(None),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List TDS certificates"""
    certificates, total = await TDSCertificateService.get_certificates(
        db,
        vendor_id=vendor_id,
        financial_year=financial_year,
        quarter=quarter,
        skip=skip,
        limit=limit,
    )

    return {
        "items": [TDSCertificateResponse.model_validate(c) for c in certificates],
        "total": total,
        "skip": skip,
        "limit": limit,
    }


@router.post("/certificates/{certificate_id}/issue", response_model=TDSCertificateResponse)
async def issue_tds_certificate(
    certificate_id: UUID,
    issued_to: str = Query(...),
    issued_via: str = Query("email", description="email, download, or physical"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark certificate as issued"""
    from app.models.tds import TDSCertificate

    certificate = await db.get(TDSCertificate, certificate_id)
    if not certificate:
        raise HTTPException(status_code=404, detail="Certificate not found")

    certificate.status = TDSCertificateStatus.ISSUED
    certificate.issued_date = date.today()
    certificate.issued_to = issued_to
    certificate.issued_via = issued_via

    await db.commit()
    await db.refresh(certificate)
    return certificate


# ==================== TDS 26Q Return Endpoints ====================

@router.post("/26q/returns", response_model=TDS26QReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_26q_return(
    return_data: TDS26QReturnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create TDS 26Q return"""
    try:
        tds_return = await TDS26QService.create_return(db, return_data, current_user.id)
        return tds_return
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/26q/returns/{return_id}/generate", response_model=TDS26QReturnResponse)
async def generate_26q_data(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate 26Q data from deductions"""
    try:
        tds_return = await TDS26QService.generate_26q_data(db, return_id)
        return tds_return
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/26q/returns/{return_id}", response_model=TDS26QReturnResponse)
async def get_26q_return(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS 26Q return by ID"""
    from app.models.tds import TDS26QReturn

    tds_return = await db.get(TDS26QReturn, return_id)
    if not tds_return:
        raise HTTPException(status_code=404, detail="Return not found")
    return tds_return


@router.post("/26q/returns/{return_id}/mark-filed", response_model=TDS26QReturnResponse)
async def mark_26q_filed(
    return_id: UUID,
    provisional_receipt_number: str = Query(...),
    filing_date: date = Query(...),
    token_number: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark 26Q return as filed"""
    from app.models.tds import TDS26QReturn

    tds_return = await db.get(TDS26QReturn, return_id)
    if not tds_return:
        raise HTTPException(status_code=404, detail="Return not found")

    tds_return.status = TDS26QStatus.FILED
    tds_return.provisional_receipt_number = provisional_receipt_number
    tds_return.filing_date = filing_date
    tds_return.token_number = token_number
    tds_return.filed_by = current_user.id

    await db.commit()
    await db.refresh(tds_return)
    return tds_return


# ==================== TDS Dashboard & Reports ====================

@router.get("/dashboard", response_model=TDSDashboardStats)
async def get_tds_dashboard(
    tan: str = Query(..., max_length=10),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS compliance dashboard"""
    return await TDSReportService.get_dashboard_stats(db, tan)


@router.get("/reports/payable-summary", response_model=List[TDSPayableSummary])
async def get_tds_payable_summary(
    financial_year: str = Query(..., description="e.g., 2024-25"),
    quarter: int = Query(..., ge=1, le=4),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS payable summary by section"""
    return await TDSReportService.get_payable_summary(db, financial_year, quarter)


@router.get("/reports/pending-deposits", response_model=dict)
async def get_pending_deposits(
    financial_year: Optional[str] = Query(None),
    quarter: Optional[int] = Query(None, ge=1, le=4),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get pending TDS deposits"""
    deductions, total = await TDSService.get_deductions(
        db,
        financial_year=financial_year,
        quarter=quarter,
        deposit_status=TDSDepositStatus.PENDING,
        skip=skip,
        limit=limit,
    )

    items = []
    for d in deductions:
        items.append(TDSDeductionListResponse(
            id=d.id,
            tds_section=d.tds_section,
            vendor_id=d.vendor_id,
            vendor_name=d.vendor.vendor_name if d.vendor else "Unknown",
            vendor_pan=d.vendor_pan,
            deduction_date=d.deduction_date,
            gross_amount=d.gross_amount,
            total_tds=d.total_tds,
            deposit_status=d.deposit_status,
            certificate_status=d.certificate_status,
        ))

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
    }


# ==================== TDS Sections Reference ====================

@router.get("/sections", response_model=List[TDSThresholdInfo])
async def get_tds_sections(
    current_user: User = Depends(get_current_user),
):
    """Get TDS sections with rates and thresholds"""
    from app.models.vendor import TDS_RATES

    section_info = {
        TDSSection.SECTION_194C_IND: {
            "description": "Section 194C - Contractors (Individual/HUF)",
            "threshold": 30000,
            "annual_threshold": 100000,
        },
        TDSSection.SECTION_194C_OTH: {
            "description": "Section 194C - Contractors (Others)",
            "threshold": 30000,
            "annual_threshold": 100000,
        },
        TDSSection.SECTION_194J: {
            "description": "Section 194J - Professional/Technical Fees",
            "threshold": 30000,
            "annual_threshold": None,
        },
        TDSSection.SECTION_194H: {
            "description": "Section 194H - Commission/Brokerage",
            "threshold": 15000,
            "annual_threshold": None,
        },
        TDSSection.SECTION_194I_RENT_LAND: {
            "description": "Section 194I - Rent (Land/Building)",
            "threshold": 240000,
            "annual_threshold": None,
        },
        TDSSection.SECTION_194I_RENT_PLANT: {
            "description": "Section 194I - Rent (Plant/Machinery)",
            "threshold": 240000,
            "annual_threshold": None,
        },
        TDSSection.SECTION_194Q: {
            "description": "Section 194Q - Purchase of Goods",
            "threshold": 5000000,
            "annual_threshold": None,
        },
        TDSSection.SECTION_194A: {
            "description": "Section 194A - Interest (Other than Bank)",
            "threshold": 5000,
            "annual_threshold": None,
        },
    }

    result = []
    for section, rate in TDS_RATES.items():
        if section in section_info:
            info = section_info[section]
            result.append(TDSThresholdInfo(
                tds_section=section,
                section_description=info["description"],
                threshold_amount=info["threshold"],
                annual_threshold=info["annual_threshold"],
                standard_rate=rate,
                rate_without_pan=20,  # 20% for no PAN
            ))

    return result
