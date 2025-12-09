"""
Statutory Compliance API endpoints.
WBS Reference: Phase 9 - Company Onboarding & Statutory
"""
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.statutory import FilingStatus, TransferType
from app.schemas.statutory import (
    # Company
    CompanyProfileCreate,
    CompanyProfileUpdate,
    CompanyProfileResponse,
    CompanyStatutoryUpdate,
    CompanyStatutoryResponse,
    CompanyBankAccountCreate,
    CompanyBankAccountUpdate,
    CompanyBankAccountResponse,
    AuthorizedSignatoryCreate,
    AuthorizedSignatoryUpdate,
    AuthorizedSignatoryResponse,
    CompanyFullResponse,
    # PF
    PFFilingCreate,
    PFFilingResponse,
    PFFilingDetailedResponse,
    PFFilingAcknowledge,
    ECRGenerateRequest,
    # ESI
    ESIFilingResponse,
    ESIFilingDetailedResponse,
    ESIFilingChallan,
    ESIReturnGenerateRequest,
    # TDS
    TDSChallanCreate,
    TDSChallanUpdate,
    TDSChallanResponse,
    TDSFilingResponse,
    TDSFilingDetailedResponse,
    TDSFilingAcknowledge,
    TDS24QGenerateRequest,
    # Disbursement
    SalaryDisbursementResponse,
    SalaryDisbursementDetailedResponse,
    SalaryDisbursementProcess,
    NEFTFileGenerateRequest,
    # Dashboard
    StatutoryDashboardStats,
)
from app.services.statutory import StatutoryService

router = APIRouter()


# Company Profile Endpoints

@router.get("/company", response_model=CompanyFullResponse)
async def get_company(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company profile with all related data."""
    company = await StatutoryService.get_company_profile(db)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found. Please complete company setup.",
        )
    return company


@router.post("/company", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    data: CompanyProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create company profile (first-time setup)."""
    existing = await StatutoryService.get_company_profile(db)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile already exists. Use PUT to update.",
        )

    company = await StatutoryService.create_company_profile(db, **data.model_dump())
    await db.commit()
    return company


@router.put("/company", response_model=CompanyProfileResponse)
async def update_company(
    data: CompanyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update company profile."""
    company = await StatutoryService.get_company_profile(db)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    updated = await StatutoryService.update_company_profile(
        db, company, **data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return updated


@router.put("/company/statutory", response_model=CompanyStatutoryResponse)
async def update_company_statutory(
    data: CompanyStatutoryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update company statutory registrations."""
    company = await StatutoryService.get_company_profile(db)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    statutory = await StatutoryService.create_or_update_statutory(
        db, company.id, **data.model_dump(exclude_unset=True)
    )
    await db.commit()
    return statutory


# Company Bank Accounts

@router.get("/company/bank-accounts", response_model=list[CompanyBankAccountResponse])
async def list_bank_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List company bank accounts."""
    company = await StatutoryService.get_company_profile(db)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company profile not found",
        )

    accounts = await StatutoryService.get_bank_accounts(db, company.id)
    return accounts


@router.post("/company/bank-accounts", response_model=CompanyBankAccountResponse, status_code=status.HTTP_201_CREATED)
async def create_bank_account(
    data: CompanyBankAccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add company bank account."""
    account = await StatutoryService.create_bank_account(db, **data.model_dump())
    await db.commit()
    return account


# Authorized Signatories

@router.post("/company/signatories", response_model=AuthorizedSignatoryResponse, status_code=status.HTTP_201_CREATED)
async def create_signatory(
    data: AuthorizedSignatoryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add authorized signatory."""
    signatory = await StatutoryService.create_signatory(db, **data.model_dump())
    await db.commit()
    return signatory


# PF ECR Endpoints

@router.post("/pf/ecr/generate", response_model=PFFilingResponse)
async def generate_pf_ecr(
    data: ECRGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate PF ECR filing for a month."""
    try:
        filing = await StatutoryService.generate_pf_ecr(
            db, data.month, data.year, current_user.id
        )
        await db.commit()
        return filing
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/pf/ecr", response_model=list[PFFilingResponse])
async def list_pf_filings(
    year: Optional[int] = Query(None),
    status_filter: Optional[FilingStatus] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List PF ECR filings."""
    filings, total = await StatutoryService.get_pf_filings(
        db, year=year, status=status_filter, page=page, size=size
    )
    return filings


@router.get("/pf/ecr/{filing_id}", response_model=PFFilingDetailedResponse)
async def get_pf_filing(
    filing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get PF ECR filing details."""
    filing = await StatutoryService.get_pf_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PF filing not found",
        )
    return filing


@router.get("/pf/ecr/{filing_id}/download")
async def download_ecr_file(
    filing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download ECR file."""
    filing = await StatutoryService.get_pf_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PF filing not found",
        )

    if filing.status == FilingStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ECR not yet generated",
        )

    content = StatutoryService.generate_ecr_file(filing, filing.details)
    filename = f"ECR_{filing.year}_{filing.month:02d}.txt"

    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/pf/ecr/{filing_id}/acknowledge", response_model=PFFilingResponse)
async def acknowledge_pf_filing(
    filing_id: UUID,
    data: PFFilingAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge PF filing submission."""
    filing = await StatutoryService.get_pf_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PF filing not found",
        )

    updated = await StatutoryService.acknowledge_pf_filing(
        db, filing, data.trrn, data.acknowledgement_number, data.acknowledgement_date
    )
    await db.commit()
    return updated


# ESI Return Endpoints

@router.post("/esi/return/generate", response_model=ESIFilingResponse)
async def generate_esi_return(
    data: ESIReturnGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate ESI return filing for a contribution period."""
    try:
        filing = await StatutoryService.generate_esi_return(
            db, data.year, data.start_month, data.end_month, current_user.id
        )
        await db.commit()
        return filing
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/esi/return/{filing_id}", response_model=ESIFilingDetailedResponse)
async def get_esi_filing(
    filing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get ESI filing details."""
    filing = await StatutoryService.get_esi_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ESI filing not found",
        )
    return filing


@router.post("/esi/return/{filing_id}/challan", response_model=ESIFilingResponse)
async def update_esi_challan(
    filing_id: UUID,
    data: ESIFilingChallan,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update ESI filing with challan details."""
    filing = await StatutoryService.get_esi_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ESI filing not found",
        )

    updated = await StatutoryService.update_esi_challan(
        db, filing, data.challan_number, data.challan_date
    )
    await db.commit()
    return updated


# TDS Endpoints

@router.post("/tds/challans", response_model=TDSChallanResponse, status_code=status.HTTP_201_CREATED)
async def create_tds_challan(
    data: TDSChallanCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create TDS challan record."""
    challan = await StatutoryService.create_tds_challan(db, **data.model_dump())
    await db.commit()
    return challan


@router.get("/tds/challans", response_model=list[TDSChallanResponse])
async def list_tds_challans(
    financial_year: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List TDS challans."""
    challans = await StatutoryService.get_tds_challans(db, financial_year)
    return challans


@router.post("/tds/24q/generate", response_model=TDSFilingResponse)
async def generate_tds_24q(
    data: TDS24QGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate TDS 24Q filing for a quarter."""
    try:
        filing = await StatutoryService.generate_tds_24q(
            db, data.quarter, data.financial_year, current_user.id
        )
        await db.commit()
        return filing
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/tds/24q/{filing_id}", response_model=TDSFilingDetailedResponse)
async def get_tds_filing(
    filing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get TDS 24Q filing details."""
    filing = await StatutoryService.get_tds_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TDS filing not found",
        )
    return filing


@router.post("/tds/24q/{filing_id}/acknowledge", response_model=TDSFilingResponse)
async def acknowledge_tds_filing(
    filing_id: UUID,
    data: TDSFilingAcknowledge,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Acknowledge TDS 24Q filing submission."""
    filing = await StatutoryService.get_tds_filing(db, filing_id)
    if not filing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="TDS filing not found",
        )

    updated = await StatutoryService.acknowledge_tds_filing(
        db,
        filing,
        data.provisional_receipt_number,
        data.acknowledgement_number,
        data.filing_date,
    )
    await db.commit()
    return updated


# Salary Disbursement Endpoints

@router.post("/disbursements/generate", response_model=SalaryDisbursementResponse)
async def generate_bank_file(
    data: NEFTFileGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate salary bank transfer file."""
    try:
        disbursement = await StatutoryService.generate_bank_file(
            db,
            data.payroll_run_id,
            data.company_bank_account_id,
            data.disbursement_date,
            data.transfer_type,
            current_user.id,
        )
        await db.commit()
        return disbursement
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get("/disbursements/{disbursement_id}", response_model=SalaryDisbursementDetailedResponse)
async def get_disbursement(
    disbursement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get salary disbursement details."""
    disbursement = await StatutoryService.get_disbursement(db, disbursement_id)
    if not disbursement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disbursement not found",
        )
    return disbursement


@router.get("/disbursements/{disbursement_id}/download")
async def download_bank_file(
    disbursement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download bank transfer file."""
    disbursement = await StatutoryService.get_disbursement(db, disbursement_id)
    if not disbursement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disbursement not found",
        )

    # Get company bank account
    company = await StatutoryService.get_company_profile(db)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company profile not found",
        )

    # Find the bank account
    account = None
    for acc in company.bank_accounts:
        if acc.id == disbursement.company_bank_account_id:
            account = acc
            break

    if not account:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company bank account not found",
        )

    content = StatutoryService.generate_neft_file(disbursement, disbursement.details, account)
    filename = f"NEFT_{disbursement.disbursement_date.strftime('%Y%m%d')}.txt"

    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


@router.post("/disbursements/{disbursement_id}/process", response_model=SalaryDisbursementResponse)
async def process_disbursement(
    disbursement_id: UUID,
    data: SalaryDisbursementProcess,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark disbursement as processing."""
    disbursement = await StatutoryService.get_disbursement(db, disbursement_id)
    if not disbursement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disbursement not found",
        )

    updated = await StatutoryService.process_disbursement(
        db, disbursement, data.batch_reference, data.utr_number
    )
    await db.commit()
    return updated


@router.post("/disbursements/{disbursement_id}/complete", response_model=SalaryDisbursementResponse)
async def complete_disbursement(
    disbursement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete salary disbursement."""
    disbursement = await StatutoryService.get_disbursement(db, disbursement_id)
    if not disbursement:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Disbursement not found",
        )

    updated = await StatutoryService.complete_disbursement(db, disbursement)
    await db.commit()
    return updated


# Dashboard

@router.get("/dashboard", response_model=StatutoryDashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get statutory compliance dashboard statistics."""
    stats = await StatutoryService.get_dashboard_stats(db)
    return stats
