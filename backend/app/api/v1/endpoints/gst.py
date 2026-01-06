"""
GST Compliance Endpoints - Phase 16
REST API endpoints for GST returns and HSN/SAC codes
"""
from datetime import date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.gst import GSTReturnType, GSTReturnStatus, HSNCodeType
from app.schemas.gst import (
    GSTReturnCreate,
    GSTReturnResponse,
    GSTR1Summary,
    GSTR1DetailedResponse,
    GSTR1InvoiceResponse,
    GSTR3BResponse,
    GSTR3BSummaryData,
    HSNSACCodeCreate,
    HSNSACCodeResponse,
    HSNSACSearchResult,
    HSNSummaryResponse,
    HSNSummaryItem,
    GSTDashboardStats,
    GSTPaymentChallan,
    AIHSNSuggestionRequest,
    AIHSNSuggestionResponse,
)
from app.services.gst import (
    HSNSACService,
    GSTReturnService,
    GSTR1Service,
    GSTR3BService,
    GSTDashboardService,
)

logger = get_logger(__name__)
router = APIRouter()


# ==================== HSN/SAC Endpoints ====================

@router.get("/hsn-sac/search", response_model=List[HSNSACSearchResult])
async def search_hsn_sac(
    q: str = Query(..., min_length=2, description="Search query"),
    code_type: Optional[HSNCodeType] = Query(None),
    limit: int = Query(20, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Search HSN/SAC codes"""
    return await HSNSACService.search_codes(db, q, code_type=code_type, limit=limit)


@router.get("/hsn-sac/{code}", response_model=HSNSACCodeResponse)
async def get_hsn_sac(
    code: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get HSN/SAC code details"""
    hsn_code = await HSNSACService.get_code(db, code)
    if not hsn_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HSN/SAC code not found")
    return hsn_code


@router.post("/hsn-sac/{code_id}/track-usage")
async def track_hsn_usage(
    code_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Track HSN/SAC code usage for AI learning"""
    await HSNSACService.increment_usage(db, code_id)
    return {"status": "ok"}


# ==================== GST Return Endpoints ====================

@router.post("/returns", response_model=GSTReturnResponse, status_code=status.HTTP_201_CREATED)
async def create_gst_return(
    return_data: GSTReturnCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new GST return"""
    # Check if return already exists for this period
    existing = await GSTReturnService.get_return_by_period(
        db,
        return_data.gstin,
        return_data.return_type,
        return_data.period_month,
        return_data.period_year,
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Return already exists for this period: {existing.return_period}"
        )

    gst_return = await GSTReturnService.create_return(db, return_data, current_user.id)
    return gst_return


@router.get("/returns/{return_id}", response_model=GSTReturnResponse)
async def get_gst_return(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GST return by ID"""
    gst_return = await GSTReturnService.get_return(db, return_id)
    if not gst_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GST return not found")
    return gst_return


# ==================== GSTR-1 Endpoints ====================

@router.get("/gstr1/{year}/{month}", response_model=GSTReturnResponse)
async def get_gstr1_by_period(
    year: int,
    month: int,
    gstin: str = Query(..., min_length=15, max_length=15),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GSTR-1 for a specific period"""
    gst_return = await GSTReturnService.get_return_by_period(
        db, gstin, GSTReturnType.GSTR1, month, year
    )
    if not gst_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GSTR-1 not found for this period")
    return gst_return


@router.post("/gstr1/{return_id}/generate", response_model=GSTReturnResponse)
async def generate_gstr1(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate GSTR-1 data from invoices"""
    try:
        gst_return = await GSTR1Service.generate_gstr1(db, return_id, current_user.id)
        return gst_return
    except ValueError as e:
        logger.error(f"Failed to generate GSTR-1 for return {return_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/gstr1/{return_id}/summary", response_model=GSTR1Summary)
async def get_gstr1_summary(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GSTR-1 summary"""
    try:
        return await GSTR1Service.get_gstr1_summary(db, return_id)
    except ValueError as e:
        logger.error(f"Failed to get GSTR-1 summary for return {return_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/gstr1/{return_id}/invoices", response_model=List[GSTR1InvoiceResponse])
async def get_gstr1_invoices(
    return_id: UUID,
    invoice_type: Optional[str] = Query(None, description="Filter by invoice type (B2B, B2CL, etc.)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GSTR-1 invoice details"""
    from sqlalchemy import select
    from app.models.gst import GSTR1Data, GSTInvoiceType

    query = select(GSTR1Data).where(GSTR1Data.return_id == return_id)

    if invoice_type:
        try:
            inv_type = GSTInvoiceType(invoice_type)
            query = query.where(GSTR1Data.invoice_type == inv_type)
        except ValueError:
            pass

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    invoices = result.scalars().all()

    return [GSTR1InvoiceResponse.model_validate(inv) for inv in invoices]


@router.get("/gstr1/{return_id}/hsn-summary", response_model=HSNSummaryResponse)
async def get_gstr1_hsn_summary(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get HSN summary for GSTR-1"""
    from sqlalchemy import select, func
    from app.models.gst import HSNSummary

    result = await db.execute(
        select(HSNSummary).where(HSNSummary.return_id == return_id)
    )
    items = result.scalars().all()

    total_value = sum(item.total_value for item in items)
    total_taxable = sum(item.taxable_value for item in items)
    total_igst = sum(item.igst_amount for item in items)
    total_cgst = sum(item.cgst_amount for item in items)
    total_sgst = sum(item.sgst_amount for item in items)
    total_cess = sum(item.cess_amount for item in items)

    return HSNSummaryResponse(
        return_id=return_id,
        items=[
            HSNSummaryItem(
                hsn_code=item.hsn_code,
                description=item.description,
                uqc=item.uqc,
                total_quantity=item.total_quantity,
                total_value=item.total_value,
                taxable_value=item.taxable_value,
                igst_amount=item.igst_amount,
                cgst_amount=item.cgst_amount,
                sgst_amount=item.sgst_amount,
                cess_amount=item.cess_amount,
                rate=item.rate,
            )
            for item in items
        ],
        total_value=total_value,
        total_taxable=total_taxable,
        total_igst=total_igst,
        total_cgst=total_cgst,
        total_sgst=total_sgst,
        total_cess=total_cess,
    )


# ==================== GSTR-3B Endpoints ====================

@router.get("/gstr3b/{year}/{month}", response_model=GSTReturnResponse)
async def get_gstr3b_by_period(
    year: int,
    month: int,
    gstin: str = Query(..., min_length=15, max_length=15),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GSTR-3B for a specific period"""
    gst_return = await GSTReturnService.get_return_by_period(
        db, gstin, GSTReturnType.GSTR3B, month, year
    )
    if not gst_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GSTR-3B not found for this period")
    return gst_return


@router.post("/gstr3b/{return_id}/generate", response_model=GSTReturnResponse)
async def generate_gstr3b(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate GSTR-3B data"""
    try:
        gst_return = await GSTR3BService.generate_gstr3b(db, return_id, current_user.id)
        return gst_return
    except ValueError as e:
        logger.error(f"Failed to generate GSTR-3B for return {return_id}: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/gstr3b/{return_id}/summary", response_model=GSTR3BSummaryData)
async def get_gstr3b_summary(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GSTR-3B summary"""
    from sqlalchemy import select
    from app.models.gst import GSTR3BSummary

    result = await db.execute(
        select(GSTR3BSummary).where(GSTR3BSummary.return_id == return_id)
    )
    summary = result.scalar_one_or_none()

    if not summary:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GSTR-3B summary not found")

    return GSTR3BSummaryData.model_validate(summary)


@router.get("/gstr3b/{return_id}/challan", response_model=GSTPaymentChallan)
async def get_gst_payment_challan(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GST payment challan for GSTR-3B"""
    try:
        return await GSTR3BService.get_payment_challan(db, return_id)
    except ValueError as e:
        logger.error(f"Failed to get payment challan for return {return_id}: {e}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# ==================== GST Dashboard ====================

@router.get("/dashboard", response_model=GSTDashboardStats)
async def get_gst_dashboard(
    gstin: str = Query(..., min_length=15, max_length=15),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get GST compliance dashboard statistics"""
    return await GSTDashboardService.get_dashboard_stats(db, gstin)


# ==================== Validation & Filing ====================

@router.post("/returns/{return_id}/validate", response_model=GSTReturnResponse)
async def validate_gst_return(
    return_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Validate GST return"""
    gst_return = await GSTReturnService.get_return(db, return_id)
    if not gst_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GST return not found")

    # Perform validation (simplified)
    errors = []
    warnings = []

    # Check if data exists
    if not gst_return.summary_data:
        errors.append({"field": "data", "message": "Return data not generated"})

    gst_return.validation_errors = errors if errors else None
    gst_return.warnings = warnings if warnings else None
    gst_return.is_validated = len(errors) == 0

    if gst_return.is_validated:
        gst_return.status = GSTReturnStatus.VALIDATED

    await db.commit()
    await db.refresh(gst_return)
    return gst_return


@router.post("/returns/{return_id}/mark-filed", response_model=GSTReturnResponse)
async def mark_return_filed(
    return_id: UUID,
    arn: str = Query(..., description="Application Reference Number"),
    filing_date: date = Query(...),
    acknowledgement: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark GST return as filed"""
    gst_return = await GSTReturnService.get_return(db, return_id)
    if not gst_return:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GST return not found")

    gst_return.status = GSTReturnStatus.FILED
    gst_return.arn = arn
    gst_return.filing_date = filing_date
    gst_return.acknowledgement_number = acknowledgement
    gst_return.filed_by = current_user.id

    await db.commit()
    await db.refresh(gst_return)
    return gst_return
