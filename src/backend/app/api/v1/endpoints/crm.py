"""
CRM API Endpoints
Lead, Contact, Customer, Opportunity, and Activity management
India-specific with GSTIN validation
"""
from datetime import datetime, date
from typing import Annotated, Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.crm import (
    LeadSource, LeadStatus, OpportunityStage, ActivityType, EntityType
)
from app.schemas.crm import (
    # Lead schemas
    LeadCreate, LeadUpdate, LeadStatusUpdate, LeadResponse,
    LeadListResponse, LeadScoreResponse, LeadConvertRequest, LeadConvertResponse,
    # Contact schemas
    ContactCreate, ContactUpdate, ContactResponse, ContactListResponse,
    # Customer schemas
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse,
    Customer360View, CustomerTransactionSummary, StateWiseReport, StateWiseDistribution,
    # Opportunity schemas
    OpportunityCreate, OpportunityUpdate, OpportunityStageUpdate,
    OpportunityResponse, OpportunityListResponse, PipelineSummary, SalesForecastResponse,
    # Activity schemas
    ActivityCreate, ActivityUpdate, ActivityCompleteRequest, FollowUpRequest,
    ActivityResponse, ActivityListResponse,
    # Note schemas
    NoteCreate, NoteUpdate, NoteResponse, NoteListResponse,
    # Dashboard schemas
    DashboardMetrics, SalesFunnelReport,
    # Common schemas
    PaginatedResponse
)
from app.services.crm_service import CRMService


router = APIRouter()


# ============================================================================
# Lead Endpoints
# ============================================================================

@router.get("/leads", response_model=LeadListResponse)
async def list_leads(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[LeadStatus] = None,
    source: Optional[LeadSource] = None,
    assigned_to: Optional[UUID] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|contact_name|expected_value|score)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List leads with filtering and pagination.

    Filters:
    - status: Lead status (new, contacted, qualified, etc.)
    - source: Lead source (website, referral, etc.)
    - assigned_to: User ID assigned to the lead
    - search: Search in contact name, company name, email, lead number
    """
    company_id = UUID(current_user.company_id)

    leads, total = await CRMService.list_leads(
        db=db,
        company_id=company_id,
        page=page,
        limit=limit,
        status=status,
        source=source,
        assigned_to=assigned_to,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return LeadListResponse(
        data=leads,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/leads", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    lead_data: LeadCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new lead.

    Auto-generates lead number (LD-YYYYMM-XXXX) and calculates initial lead score.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    lead = await CRMService.create_lead(
        db=db,
        company_id=company_id,
        lead_data=lead_data,
        created_by=user_id
    )

    return lead


@router.get("/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a lead by ID."""
    company_id = UUID(current_user.company_id)

    lead = await CRMService.get_lead_by_id(db, lead_id, company_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.put("/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: UUID,
    lead_data: LeadUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a lead."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    lead = await CRMService.update_lead(
        db=db,
        lead_id=lead_id,
        company_id=company_id,
        lead_data=lead_data,
        updated_by=user_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.patch("/leads/{lead_id}/status", response_model=LeadResponse)
async def update_lead_status(
    lead_id: UUID,
    status_update: LeadStatusUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update lead status/stage."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    lead = await CRMService.update_lead_stage(
        db=db,
        lead_id=lead_id,
        company_id=company_id,
        status_update=status_update,
        updated_by=user_id
    )

    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    return lead


@router.get("/leads/{lead_id}/score", response_model=LeadScoreResponse)
async def get_lead_score(
    lead_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get lead score with breakdown of factors.

    Scoring factors:
    - Company info completeness (0-20)
    - Contact info completeness (0-20)
    - Expected value (0-20)
    - Source quality (0-15)
    - Recency (0-10)
    """
    company_id = UUID(current_user.company_id)

    lead = await CRMService.get_lead_by_id(db, lead_id, company_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Lead not found"
        )

    score_data = CRMService.calculate_lead_score(lead)
    return LeadScoreResponse(**score_data)


@router.post("/leads/{lead_id}/convert", response_model=LeadConvertResponse)
async def convert_lead(
    lead_id: UUID,
    convert_data: LeadConvertRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Convert a lead to a customer.

    Optionally creates an opportunity. Validates GSTIN and PAN if provided.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    try:
        result = await CRMService.convert_lead_to_customer(
            db=db,
            lead_id=lead_id,
            company_id=company_id,
            convert_data=convert_data,
            converted_by=user_id
        )
        return LeadConvertResponse(**result)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ============================================================================
# Contact Endpoints
# ============================================================================

@router.get("/contacts", response_model=ContactListResponse)
async def list_contacts(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    customer_id: Optional[UUID] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = True
):
    """List contacts with filtering and pagination."""
    company_id = UUID(current_user.company_id)

    contacts, total = await CRMService.list_contacts(
        db=db,
        company_id=company_id,
        customer_id=customer_id,
        page=page,
        limit=limit,
        search=search,
        is_active=is_active
    )

    return ContactListResponse(
        data=contacts,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/contacts", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    contact_data: ContactCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new contact for a customer."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    try:
        contact = await CRMService.create_contact(
            db=db,
            company_id=company_id,
            contact_data=contact_data,
            created_by=user_id
        )
        return contact
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a contact by ID."""
    company_id = UUID(current_user.company_id)

    contact = await CRMService.get_contact_by_id(db, contact_id, company_id)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    contact_data: ContactUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a contact."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    contact = await CRMService.update_contact(
        db=db,
        contact_id=contact_id,
        company_id=company_id,
        contact_data=contact_data,
        updated_by=user_id
    )

    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )

    return contact


# ============================================================================
# Customer Endpoints
# ============================================================================

@router.get("/customers", response_model=CustomerListResponse)
async def list_customers(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    state: Optional[str] = None,
    is_active: Optional[bool] = True,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|company_name|total_revenue)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """
    List customers with filtering and pagination.

    Filters:
    - state: Indian state for GST purposes
    - is_active: Active status
    - search: Search in company name, customer code, GSTIN, email
    """
    company_id = UUID(current_user.company_id)

    customers, total = await CRMService.list_customers(
        db=db,
        company_id=company_id,
        page=page,
        limit=limit,
        state=state,
        is_active=is_active,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return CustomerListResponse(
        data=customers,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/customers", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new customer.

    Validates GSTIN and PAN formats. Auto-generates customer code if not provided.
    Derives state from GSTIN.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    customer = await CRMService.create_customer(
        db=db,
        company_id=company_id,
        customer_data=customer_data,
        created_by=user_id
    )

    return customer


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get a customer by ID."""
    company_id = UUID(current_user.company_id)

    customer = await CRMService.get_customer_by_id(db, customer_id, company_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: UUID,
    customer_data: CustomerUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a customer."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    customer = await CRMService.update_customer(
        db=db,
        customer_id=customer_id,
        company_id=company_id,
        customer_data=customer_data,
        updated_by=user_id
    )

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return customer


@router.get("/customers/{customer_id}/360-view")
async def get_customer_360_view(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get complete 360-degree view of a customer.

    Includes:
    - Customer details
    - Contacts
    - Opportunities
    - Recent activities
    - Transaction summary
    """
    company_id = UUID(current_user.company_id)

    view = await CRMService.get_customer_360_view(db, customer_id, company_id)
    if not view:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return view


@router.get("/customers/{customer_id}/transactions")
async def get_customer_transactions(
    customer_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get customer transactions (invoices and payments).

    Returns transaction history with amounts in INR.
    """
    company_id = UUID(current_user.company_id)

    customer = await CRMService.get_customer_by_id(db, customer_id, company_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    from sqlalchemy import select, func, desc, union_all, literal
    from app.models.invoice import Invoice
    from app.models.payment import Payment, PaymentType

    # Query invoices for this customer
    invoice_query = select(Invoice).where(
        Invoice.company_id == company_id,
        Invoice.customer_id == customer_id
    ).order_by(desc(Invoice.invoice_date))

    invoice_result = await db.execute(invoice_query)
    invoices = invoice_result.scalars().all()

    # Query payments received from this customer
    payment_query = select(Payment).where(
        Payment.company_id == company_id,
        Payment.party_id == customer_id,
        Payment.payment_type == PaymentType.RECEIVED
    ).order_by(desc(Payment.payment_date))

    payment_result = await db.execute(payment_query)
    payments = payment_result.scalars().all()

    # Build transactions list (combined and sorted)
    transactions = []
    for inv in invoices:
        transactions.append({
            "type": "invoice",
            "id": str(inv.id),
            "number": inv.invoice_number,
            "date": inv.invoice_date.isoformat() if inv.invoice_date else None,
            "amount": float(inv.grand_total) if hasattr(inv, 'grand_total') and inv.grand_total else float(inv.subtotal or 0) + float(inv.total_tax or 0),
            "status": inv.status.value if hasattr(inv.status, 'value') else str(inv.status) if inv.status else "draft",
            "due_date": inv.due_date.isoformat() if inv.due_date else None
        })

    for pmt in payments:
        transactions.append({
            "type": "payment",
            "id": str(pmt.id),
            "number": pmt.payment_number,
            "date": pmt.payment_date.isoformat() if pmt.payment_date else None,
            "amount": float(pmt.amount or 0),
            "status": pmt.status.value if hasattr(pmt.status, 'value') else str(pmt.status) if pmt.status else "completed",
            "payment_mode": pmt.payment_mode.value if hasattr(pmt.payment_mode, 'value') else str(pmt.payment_mode) if pmt.payment_mode else None
        })

    # Sort by date descending
    transactions.sort(key=lambda x: x["date"] or "", reverse=True)

    # Calculate totals
    total_invoice_amount = sum(float(inv.subtotal or 0) + float(inv.total_tax or 0) for inv in invoices)
    total_payment_amount = sum(float(pmt.amount or 0) for pmt in payments)

    # Apply pagination
    total = len(transactions)
    start = (page - 1) * limit
    end = start + limit
    paginated_transactions = transactions[start:end]

    return {
        "customer_id": str(customer_id),
        "transactions": paginated_transactions,
        "summary": {
            "total_invoices": len(invoices),
            "total_invoice_amount": f"{total_invoice_amount:.2f}",
            "total_payments": len(payments),
            "total_payment_amount": f"{total_payment_amount:.2f}",
            "outstanding_amount": str(customer.outstanding_receivable) if customer.outstanding_receivable else "0.00",
            "currency": "INR"
        },
        "meta": {
            "page": page,
            "limit": limit,
            "total": total
        }
    }


@router.get("/customers/distribution/state-wise", response_model=StateWiseReport)
async def get_state_wise_customer_distribution(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get state-wise customer distribution.

    India-specific report showing customer count and revenue by state.
    """
    company_id = UUID(current_user.company_id)

    distribution = await CRMService.get_state_wise_distribution(db, company_id)

    total_customers = sum(d["customer_count"] for d in distribution)
    total_revenue = sum(d["total_revenue"] for d in distribution)

    return StateWiseReport(
        total_customers=total_customers,
        total_revenue=total_revenue,
        distribution=[StateWiseDistribution(**d) for d in distribution]
    )


# ============================================================================
# Opportunity Endpoints
# ============================================================================

@router.get("/opportunities", response_model=OpportunityListResponse)
async def list_opportunities(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    stage: Optional[OpportunityStage] = None,
    customer_id: Optional[UUID] = None,
    owner_id: Optional[UUID] = None,
    is_closed: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("created_at", pattern="^(created_at|updated_at|title|value|expected_close_date)$"),
    sort_order: str = Query("desc", pattern="^(asc|desc)$")
):
    """List opportunities with filtering and pagination."""
    company_id = UUID(current_user.company_id)

    opportunities, total = await CRMService.list_opportunities(
        db=db,
        company_id=company_id,
        page=page,
        limit=limit,
        stage=stage,
        customer_id=customer_id,
        owner_id=owner_id,
        is_closed=is_closed,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return OpportunityListResponse(
        data=opportunities,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    opportunity_data: OpportunityCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new opportunity.

    Auto-generates opportunity number (OP-YYYYMM-XXXX) and calculates weighted value.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    opportunity = await CRMService.create_opportunity(
        db=db,
        company_id=company_id,
        opportunity_data=opportunity_data,
        created_by=user_id
    )

    return opportunity


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get an opportunity by ID."""
    company_id = UUID(current_user.company_id)

    opportunity = await CRMService.get_opportunity_by_id(db, opportunity_id, company_id)
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    return opportunity


@router.put("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: UUID,
    opportunity_data: OpportunityUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an opportunity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    opportunity = await CRMService.update_opportunity(
        db=db,
        opportunity_id=opportunity_id,
        company_id=company_id,
        opportunity_data=opportunity_data,
        updated_by=user_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    return opportunity


@router.patch("/opportunities/{opportunity_id}/stage", response_model=OpportunityResponse)
async def update_opportunity_stage(
    opportunity_id: UUID,
    stage_update: OpportunityStageUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Update opportunity stage.

    Automatically adjusts probability based on stage. Handles won/lost scenarios.
    """
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    opportunity = await CRMService.update_opportunity_stage(
        db=db,
        opportunity_id=opportunity_id,
        company_id=company_id,
        stage_update=stage_update,
        updated_by=user_id
    )

    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )

    return opportunity


@router.get("/opportunities/pipeline/summary", response_model=PipelineSummary)
async def get_pipeline_summary(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    owner_id: Optional[UUID] = None
):
    """
    Get pipeline summary.

    Shows opportunity count, value, and weighted value by stage.
    Includes conversion rate and average deal size.
    """
    company_id = UUID(current_user.company_id)

    summary = await CRMService.get_pipeline_summary(
        db=db,
        company_id=company_id,
        owner_id=owner_id
    )

    return PipelineSummary(**summary)


@router.get("/opportunities/forecast", response_model=SalesForecastResponse)
async def get_sales_forecast(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    months: int = Query(6, ge=1, le=12)
):
    """
    Get sales forecast.

    Projects expected and weighted revenue based on expected close dates.
    """
    company_id = UUID(current_user.company_id)

    forecast = await CRMService.get_sales_forecast(
        db=db,
        company_id=company_id,
        forecast_months=months
    )

    return SalesForecastResponse(**forecast)


# ============================================================================
# Activity Endpoints
# ============================================================================

@router.get("/activities", response_model=ActivityListResponse)
async def list_activities(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    entity_type: Optional[EntityType] = None,
    entity_id: Optional[UUID] = None,
    activity_type: Optional[ActivityType] = None,
    status: Optional[str] = Query(None, pattern="^(scheduled|in_progress|completed|cancelled)$"),
    owner_id: Optional[UUID] = None,
    scheduled_from: Optional[datetime] = None,
    scheduled_to: Optional[datetime] = None,
    sort_by: str = Query("scheduled_at", pattern="^(scheduled_at|created_at|subject)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$")
):
    """List activities with filtering and pagination."""
    company_id = UUID(current_user.company_id)

    activities, total = await CRMService.list_activities(
        db=db,
        company_id=company_id,
        page=page,
        limit=limit,
        entity_type=entity_type,
        entity_id=entity_id,
        activity_type=activity_type,
        status=status,
        owner_id=owner_id,
        scheduled_from=scheduled_from,
        scheduled_to=scheduled_to,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return ActivityListResponse(
        data=activities,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/activities", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    activity_data: ActivityCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new activity (call, meeting, task, etc.)."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    activity = await CRMService.create_activity(
        db=db,
        company_id=company_id,
        activity_data=activity_data,
        created_by=user_id
    )

    return activity


@router.get("/activities/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get an activity by ID."""
    company_id = UUID(current_user.company_id)

    activity = await CRMService.get_activity_by_id(db, activity_id, company_id)
    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


@router.put("/activities/{activity_id}", response_model=ActivityResponse)
async def update_activity(
    activity_id: UUID,
    activity_data: ActivityUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an activity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    activity = await CRMService.update_activity(
        db=db,
        activity_id=activity_id,
        company_id=company_id,
        activity_data=activity_data,
        updated_by=user_id
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


@router.post("/activities/{activity_id}/complete", response_model=ActivityResponse)
async def complete_activity(
    activity_id: UUID,
    complete_data: ActivityCompleteRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Mark an activity as completed."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    activity = await CRMService.complete_activity(
        db=db,
        activity_id=activity_id,
        company_id=company_id,
        complete_data=complete_data,
        completed_by=user_id
    )

    if not activity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Activity not found"
        )

    return activity


@router.get("/activities/upcoming/list", response_model=List[ActivityResponse])
async def get_upcoming_activities(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    days: int = Query(7, ge=1, le=30),
    limit: int = Query(20, ge=1, le=100)
):
    """Get upcoming activities for the current user."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    activities = await CRMService.get_upcoming_activities(
        db=db,
        company_id=company_id,
        user_id=user_id,
        days=days,
        limit=limit
    )

    return activities


@router.post("/activities/followup", response_model=ActivityResponse, status_code=status.HTTP_201_CREATED)
async def schedule_followup(
    followup_data: FollowUpRequest,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Schedule a follow-up activity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    activity = await CRMService.schedule_followup(
        db=db,
        company_id=company_id,
        followup_data=followup_data,
        created_by=user_id
    )

    return activity


# ============================================================================
# Note Endpoints
# ============================================================================

@router.get("/notes", response_model=NoteListResponse)
async def list_notes(
    entity_type: EntityType,
    entity_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100)
):
    """List notes for an entity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    notes, total = await CRMService.list_notes(
        db=db,
        company_id=company_id,
        entity_type=entity_type,
        entity_id=entity_id,
        user_id=user_id,
        page=page,
        limit=limit
    )

    return NoteListResponse(
        data=notes,
        meta={
            "page": page,
            "limit": limit,
            "total": total,
            "pages": (total + limit - 1) // limit
        }
    )


@router.post("/notes", response_model=NoteResponse, status_code=status.HTTP_201_CREATED)
async def create_note(
    note_data: NoteCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new note on an entity."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    note = await CRMService.create_note(
        db=db,
        company_id=company_id,
        note_data=note_data,
        created_by=user_id
    )

    return note


@router.put("/notes/{note_id}", response_model=NoteResponse)
async def update_note(
    note_id: UUID,
    note_data: NoteUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a note (only by creator)."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    note = await CRMService.update_note(
        db=db,
        note_id=note_id,
        company_id=company_id,
        note_data=note_data,
        updated_by=user_id
    )

    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to update it"
        )

    return note


@router.delete("/notes/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a note (only by creator)."""
    company_id = UUID(current_user.company_id)
    user_id = UUID(current_user.user_id)

    success = await CRMService.delete_note(
        db=db,
        note_id=note_id,
        company_id=company_id,
        deleted_by=user_id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or you don't have permission to delete it"
        )


# ============================================================================
# Dashboard and Reports
# ============================================================================

@router.get("/dashboard", response_model=DashboardMetrics)
async def get_crm_dashboard(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """
    Get CRM dashboard metrics.

    Includes:
    - Lead metrics (total, new this month, by status, by source)
    - Customer metrics (total, new this month, by state)
    - Opportunity metrics (pipeline value, stages, won/lost)
    - Activity metrics (today, overdue)
    - Conversion rate and average deal size
    """
    company_id = UUID(current_user.company_id)

    metrics = await CRMService.get_dashboard_metrics(db, company_id)
    return DashboardMetrics(**metrics)


@router.get("/reports/funnel", response_model=SalesFunnelReport)
async def get_sales_funnel_report(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """
    Get sales funnel report.

    Shows stage-wise breakdown with:
    - Count and value at each stage
    - Conversion rate between stages
    - Overall conversion rate
    """
    company_id = UUID(current_user.company_id)

    report = await CRMService.get_sales_funnel_report(
        db=db,
        company_id=company_id,
        start_date=start_date,
        end_date=end_date
    )

    return SalesFunnelReport(**report)
