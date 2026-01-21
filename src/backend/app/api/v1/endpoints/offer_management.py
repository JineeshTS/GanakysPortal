"""
Offer Management API Endpoints
Handles offer creation, approval workflow, and candidate response tracking
"""
from datetime import datetime, date, timedelta
from typing import Optional, List
from uuid import UUID, uuid4
from decimal import Decimal
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field, EmailStr

from app.db.session import get_db
from app.api.deps import get_current_user

router = APIRouter()


# ============================================================================
# Request/Response Models
# ============================================================================

class SalaryComponents(BaseModel):
    base_salary: Decimal
    currency: str = "INR"
    bonus: Optional[Decimal] = None
    bonus_type: Optional[str] = None  # annual, signing, performance
    stock_options: Optional[int] = None
    other_benefits: Optional[dict] = None


class OfferCreateRequest(BaseModel):
    application_id: UUID
    position_title: str
    department_id: Optional[UUID] = None
    reporting_to: Optional[UUID] = None
    salary: SalaryComponents
    start_date: date
    offer_expiry_date: date
    employment_type: str = "full_time"  # full_time, part_time, contract
    location: Optional[str] = None
    remote_policy: Optional[str] = None  # onsite, hybrid, remote
    probation_period_months: int = 3
    notice_period_days: int = 30
    additional_terms: Optional[str] = None
    requires_approval: bool = True
    approvers: Optional[List[UUID]] = None


class OfferResponse(BaseModel):
    id: str
    application_id: str
    candidate_name: str
    candidate_email: str
    job_title: str
    position_title: str
    status: str
    salary: dict
    start_date: str
    offer_expiry_date: str
    employment_type: str
    location: Optional[str] = None
    remote_policy: Optional[str] = None
    created_at: str
    created_by: Optional[str] = None
    approval_status: str
    approvals: List[dict] = []
    candidate_response: Optional[dict] = None


class OfferApprovalRequest(BaseModel):
    decision: str = Field(..., description="approve or reject")
    comments: Optional[str] = None


class CandidateOfferResponse(BaseModel):
    decision: str = Field(..., description="accept, reject, negotiate")
    negotiation_notes: Optional[str] = None
    expected_salary: Optional[Decimal] = None
    preferred_start_date: Optional[date] = None


class OfferNegotiationRequest(BaseModel):
    revised_salary: Optional[SalaryComponents] = None
    revised_start_date: Optional[date] = None
    revised_expiry_date: Optional[date] = None
    notes: str


class OfferLetterTemplate(BaseModel):
    id: str
    name: str
    template_content: str
    variables: List[str]
    is_default: bool


# ============================================================================
# Offer CRUD Endpoints
# ============================================================================

@router.post("/", response_model=OfferResponse)
async def create_offer(
    request: OfferCreateRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new job offer for a candidate.
    """
    company_id = current_user.get("company_id")

    # Verify application exists and is at the right stage
    app_result = await db.execute(
        text("""
            SELECT a.*, c.first_name, c.last_name, c.email, j.title as job_title
            FROM applications a
            JOIN candidates c ON a.candidate_id = c.id
            JOIN job_openings j ON a.job_opening_id = j.id
            WHERE a.id = :app_id
        """).bindparams(app_id=request.application_id)
    )
    application = app_result.first()

    if not application:
        raise HTTPException(status_code=404, detail="Application not found")

    # Check for existing active offer
    existing_result = await db.execute(
        text("""
            SELECT id FROM offers
            WHERE application_id = :app_id
              AND status NOT IN ('rejected', 'withdrawn', 'expired')
        """).bindparams(app_id=request.application_id)
    )

    if existing_result.first():
        raise HTTPException(
            status_code=400,
            detail="An active offer already exists for this application"
        )

    # Create offer
    offer_id = uuid4()
    approval_status = "pending" if request.requires_approval else "approved"

    await db.execute(
        text("""
            INSERT INTO offers (
                id, company_id, application_id, position_title, department_id,
                reporting_to, base_salary, currency, bonus, bonus_type,
                stock_options, other_benefits, start_date, offer_expiry_date,
                employment_type, location, remote_policy,
                probation_period_months, notice_period_days, additional_terms,
                status, approval_status, created_by, created_at, updated_at
            ) VALUES (
                :id, :company_id, :app_id, :position, :dept_id,
                :reporting_to, :base_salary, :currency, :bonus, :bonus_type,
                :stock_options, :other_benefits, :start_date, :expiry_date,
                :employment_type, :location, :remote_policy,
                :probation, :notice, :additional_terms,
                'draft', :approval_status, :created_by, NOW(), NOW()
            )
        """).bindparams(
            id=offer_id,
            company_id=company_id,
            app_id=request.application_id,
            position=request.position_title,
            dept_id=request.department_id,
            reporting_to=request.reporting_to,
            base_salary=request.salary.base_salary,
            currency=request.salary.currency,
            bonus=request.salary.bonus,
            bonus_type=request.salary.bonus_type,
            stock_options=request.salary.stock_options,
            other_benefits=json.dumps(request.salary.other_benefits) if request.salary.other_benefits else None,
            start_date=request.start_date,
            expiry_date=request.offer_expiry_date,
            employment_type=request.employment_type,
            location=request.location,
            remote_policy=request.remote_policy,
            probation=request.probation_period_months,
            notice=request.notice_period_days,
            additional_terms=request.additional_terms,
            approval_status=approval_status,
            created_by=current_user.get("id")
        )
    )

    # Create approval records if needed
    if request.requires_approval and request.approvers:
        for i, approver_id in enumerate(request.approvers):
            approval_id = uuid4()
            await db.execute(
                text("""
                    INSERT INTO offer_approvals (
                        id, offer_id, approver_id, approval_order,
                        status, created_at
                    ) VALUES (
                        :id, :offer_id, :approver_id, :order,
                        'pending', NOW()
                    )
                """).bindparams(
                    id=approval_id,
                    offer_id=offer_id,
                    approver_id=approver_id,
                    order=i + 1
                )
            )

    # Update application stage
    await db.execute(
        text("""
            UPDATE applications
            SET stage = 'offer', updated_at = NOW()
            WHERE id = :app_id
        """).bindparams(app_id=request.application_id)
    )

    await db.commit()

    # Notify approvers if needed
    if request.requires_approval and request.approvers:
        background_tasks.add_task(
            notify_approvers,
            offer_id=offer_id,
            approver_ids=request.approvers,
            candidate_name=f"{application.first_name} {application.last_name}",
            position=request.position_title
        )

    return await _get_offer_response(db, offer_id)


@router.get("/", response_model=List[OfferResponse])
async def list_offers(
    status: Optional[str] = Query(None),
    job_id: Optional[UUID] = Query(None),
    pending_approval: bool = Query(False),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all offers with filters.
    """
    company_id = current_user.get("company_id")

    query = """
        SELECT o.id
        FROM offers o
        JOIN applications a ON o.application_id = a.id
        JOIN job_openings j ON a.job_opening_id = j.id
        WHERE (o.company_id = :company_id OR :company_id IS NULL)
    """

    params = {"company_id": company_id}

    if status:
        query += " AND o.status = :status"
        params["status"] = status

    if job_id:
        query += " AND a.job_opening_id = :job_id"
        params["job_id"] = job_id

    if pending_approval:
        query += " AND o.approval_status = 'pending'"

    query += " ORDER BY o.created_at DESC"

    result = await db.execute(text(query).bindparams(**params))
    offer_ids = [row.id for row in result.fetchall()]

    offers = []
    for oid in offer_ids:
        offers.append(await _get_offer_response(db, oid))

    return offers


@router.get("/{offer_id}", response_model=OfferResponse)
async def get_offer(
    offer_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get offer details.
    """
    return await _get_offer_response(db, offer_id)


@router.put("/{offer_id}")
async def update_offer(
    offer_id: UUID,
    request: OfferCreateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update an offer (only if in draft status).
    """
    # Check offer status
    result = await db.execute(
        text("SELECT status FROM offers WHERE id = :id")
        .bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "draft":
        raise HTTPException(
            status_code=400,
            detail="Can only update offers in draft status"
        )

    # Update offer
    await db.execute(
        text("""
            UPDATE offers SET
                position_title = :position,
                department_id = :dept_id,
                reporting_to = :reporting_to,
                base_salary = :base_salary,
                currency = :currency,
                bonus = :bonus,
                bonus_type = :bonus_type,
                stock_options = :stock_options,
                other_benefits = :other_benefits,
                start_date = :start_date,
                offer_expiry_date = :expiry_date,
                employment_type = :employment_type,
                location = :location,
                remote_policy = :remote_policy,
                probation_period_months = :probation,
                notice_period_days = :notice,
                additional_terms = :additional_terms,
                updated_at = NOW()
            WHERE id = :id
        """).bindparams(
            id=offer_id,
            position=request.position_title,
            dept_id=request.department_id,
            reporting_to=request.reporting_to,
            base_salary=request.salary.base_salary,
            currency=request.salary.currency,
            bonus=request.salary.bonus,
            bonus_type=request.salary.bonus_type,
            stock_options=request.salary.stock_options,
            other_benefits=json.dumps(request.salary.other_benefits) if request.salary.other_benefits else None,
            start_date=request.start_date,
            expiry_date=request.offer_expiry_date,
            employment_type=request.employment_type,
            location=request.location,
            remote_policy=request.remote_policy,
            probation=request.probation_period_months,
            notice=request.notice_period_days,
            additional_terms=request.additional_terms
        )
    )
    await db.commit()

    return await _get_offer_response(db, offer_id)


# ============================================================================
# Offer Approval Workflow
# ============================================================================

@router.post("/{offer_id}/submit-for-approval")
async def submit_for_approval(
    offer_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Submit an offer for approval.
    """
    result = await db.execute(
        text("SELECT status, approval_status FROM offers WHERE id = :id")
        .bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "draft":
        raise HTTPException(status_code=400, detail="Offer is not in draft status")

    await db.execute(
        text("""
            UPDATE offers
            SET status = 'pending_approval', updated_at = NOW()
            WHERE id = :id
        """).bindparams(id=offer_id)
    )
    await db.commit()

    return {"message": "Offer submitted for approval", "status": "pending_approval"}


@router.post("/{offer_id}/approve", response_model=OfferResponse)
async def approve_offer(
    offer_id: UUID,
    request: OfferApprovalRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve or reject an offer (for approvers).
    """
    user_id = current_user.get("id")

    # Check if user is an approver for this offer
    approval_result = await db.execute(
        text("""
            SELECT id, approval_order
            FROM offer_approvals
            WHERE offer_id = :offer_id AND approver_id = :user_id AND status = 'pending'
        """).bindparams(offer_id=offer_id, user_id=user_id)
    )
    approval = approval_result.first()

    if not approval:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to approve this offer or it's not pending your approval"
        )

    # Update approval
    new_status = "approved" if request.decision == "approve" else "rejected"
    await db.execute(
        text("""
            UPDATE offer_approvals
            SET status = :status, comments = :comments, decided_at = NOW()
            WHERE id = :id
        """).bindparams(id=approval.id, status=new_status, comments=request.comments)
    )

    # Check if all approvals are complete
    remaining_result = await db.execute(
        text("""
            SELECT COUNT(*) as pending
            FROM offer_approvals
            WHERE offer_id = :offer_id AND status = 'pending'
        """).bindparams(offer_id=offer_id)
    )
    remaining = remaining_result.scalar()

    # Check if any rejection
    rejected_result = await db.execute(
        text("""
            SELECT COUNT(*) as rejected
            FROM offer_approvals
            WHERE offer_id = :offer_id AND status = 'rejected'
        """).bindparams(offer_id=offer_id)
    )
    rejected_count = rejected_result.scalar()

    # Update offer status based on approvals
    if rejected_count > 0:
        offer_approval_status = "rejected"
        offer_status = "rejected"
    elif remaining == 0:
        offer_approval_status = "approved"
        offer_status = "approved"
    else:
        offer_approval_status = "pending"
        offer_status = "pending_approval"

    await db.execute(
        text("""
            UPDATE offers
            SET approval_status = :approval_status, status = :status, updated_at = NOW()
            WHERE id = :offer_id
        """).bindparams(offer_id=offer_id, approval_status=offer_approval_status, status=offer_status)
    )

    await db.commit()

    return await _get_offer_response(db, offer_id)


# ============================================================================
# Offer Sending & Candidate Response
# ============================================================================

@router.post("/{offer_id}/send")
async def send_offer(
    offer_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send the offer to the candidate.
    """
    # Get offer details
    result = await db.execute(
        text("""
            SELECT o.*, c.email, c.first_name, c.last_name
            FROM offers o
            JOIN applications a ON o.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            WHERE o.id = :id
        """).bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.approval_status != "approved":
        raise HTTPException(status_code=400, detail="Offer must be approved before sending")

    if offer.status == "sent":
        raise HTTPException(status_code=400, detail="Offer has already been sent")

    # Update offer status
    await db.execute(
        text("""
            UPDATE offers
            SET status = 'sent', sent_at = NOW(), updated_at = NOW()
            WHERE id = :id
        """).bindparams(id=offer_id)
    )

    # Update application status
    await db.execute(
        text("""
            UPDATE applications
            SET status = 'offer_sent', updated_at = NOW()
            WHERE id = :app_id
        """).bindparams(app_id=offer.application_id)
    )

    await db.commit()

    # Send email notification
    background_tasks.add_task(
        send_offer_email,
        offer_id=offer_id,
        candidate_email=offer.email,
        candidate_name=f"{offer.first_name} {offer.last_name}",
        position=offer.position_title,
        salary=float(offer.base_salary),
        start_date=offer.start_date
    )

    return {"message": "Offer sent successfully", "status": "sent"}


@router.post("/{offer_id}/candidate-response")
async def record_candidate_response(
    offer_id: UUID,
    request: CandidateOfferResponse,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Record candidate's response to the offer.
    """
    # Get offer
    result = await db.execute(
        text("SELECT * FROM offers WHERE id = :id")
        .bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "sent":
        raise HTTPException(status_code=400, detail="Offer has not been sent yet")

    # Record response
    response_data = {
        "decision": request.decision,
        "negotiation_notes": request.negotiation_notes,
        "expected_salary": float(request.expected_salary) if request.expected_salary else None,
        "preferred_start_date": request.preferred_start_date.isoformat() if request.preferred_start_date else None,
        "responded_at": datetime.utcnow().isoformat()
    }

    # Update status based on decision
    if request.decision == "accept":
        new_status = "accepted"
        app_status = "offer_accepted"
    elif request.decision == "reject":
        new_status = "rejected"
        app_status = "rejected"
    else:  # negotiate
        new_status = "negotiating"
        app_status = "offer_sent"

    await db.execute(
        text("""
            UPDATE offers
            SET status = :status,
                candidate_response = :response,
                responded_at = NOW(),
                updated_at = NOW()
            WHERE id = :id
        """).bindparams(
            id=offer_id,
            status=new_status,
            response=json.dumps(response_data)
        )
    )

    # Update application status
    await db.execute(
        text("""
            UPDATE applications
            SET status = :status, updated_at = NOW()
            WHERE id = :app_id
        """).bindparams(app_id=offer.application_id, status=app_status)
    )

    await db.commit()

    # Notify hiring team
    background_tasks.add_task(
        notify_offer_response,
        offer_id=offer_id,
        decision=request.decision
    )

    return {"message": f"Response recorded: {request.decision}", "status": new_status}


@router.post("/{offer_id}/revise")
async def revise_offer(
    offer_id: UUID,
    request: OfferNegotiationRequest,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a revised offer during negotiation.
    """
    # Get current offer
    result = await db.execute(
        text("SELECT * FROM offers WHERE id = :id")
        .bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "negotiating":
        raise HTTPException(status_code=400, detail="Offer is not in negotiation")

    # Update offer with revisions
    updates = ["revision_count = COALESCE(revision_count, 0) + 1", "updated_at = NOW()"]
    params = {"id": offer_id}

    if request.revised_salary:
        updates.append("base_salary = :base_salary")
        updates.append("bonus = :bonus")
        params["base_salary"] = request.revised_salary.base_salary
        params["bonus"] = request.revised_salary.bonus

    if request.revised_start_date:
        updates.append("start_date = :start_date")
        params["start_date"] = request.revised_start_date

    if request.revised_expiry_date:
        updates.append("offer_expiry_date = :expiry_date")
        params["expiry_date"] = request.revised_expiry_date

    updates.append("revision_notes = :notes")
    params["notes"] = request.notes

    updates.append("status = 'sent'")

    query = f"UPDATE offers SET {', '.join(updates)} WHERE id = :id"
    await db.execute(text(query).bindparams(**params))
    await db.commit()

    # Resend offer
    background_tasks.add_task(
        send_revised_offer_email,
        offer_id=offer_id
    )

    return {"message": "Revised offer sent", "status": "sent"}


# ============================================================================
# Offer Completion (Leading to Hire)
# ============================================================================

@router.post("/{offer_id}/complete-hire")
async def complete_hire(
    offer_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Complete the hiring process after offer acceptance.
    Triggers onboarding workflow.
    """
    # Get offer details
    result = await db.execute(
        text("""
            SELECT o.*, a.candidate_id, a.job_opening_id
            FROM offers o
            JOIN applications a ON o.application_id = a.id
            WHERE o.id = :id
        """).bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    if offer.status != "accepted":
        raise HTTPException(status_code=400, detail="Offer has not been accepted")

    # Update offer status
    await db.execute(
        text("""
            UPDATE offers
            SET status = 'hired', hired_at = NOW(), updated_at = NOW()
            WHERE id = :id
        """).bindparams(id=offer_id)
    )

    # Update application status
    await db.execute(
        text("""
            UPDATE applications
            SET status = 'hired', stage = 'hired', updated_at = NOW()
            WHERE id = :app_id
        """).bindparams(app_id=offer.application_id)
    )

    await db.commit()

    # Trigger onboarding workflow
    background_tasks.add_task(
        initiate_onboarding,
        offer_id=offer_id,
        candidate_id=offer.candidate_id,
        job_id=offer.job_opening_id,
        start_date=offer.start_date,
        position_title=offer.position_title,
        department_id=offer.department_id
    )

    return {"message": "Hire completed, onboarding initiated", "status": "hired"}


# ============================================================================
# Helper Functions
# ============================================================================

async def _get_offer_response(db: AsyncSession, offer_id: UUID) -> OfferResponse:
    """Get formatted offer response."""
    result = await db.execute(
        text("""
            SELECT
                o.*,
                c.first_name, c.last_name, c.email,
                j.title as job_title,
                u.email as created_by_email
            FROM offers o
            JOIN applications a ON o.application_id = a.id
            JOIN candidates c ON a.candidate_id = c.id
            JOIN job_openings j ON a.job_opening_id = j.id
            LEFT JOIN users u ON o.created_by = u.id
            WHERE o.id = :id
        """).bindparams(id=offer_id)
    )
    offer = result.first()

    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Get approvals
    approvals_result = await db.execute(
        text("""
            SELECT oa.*, u.first_name, u.last_name, u.email
            FROM offer_approvals oa
            JOIN users u ON oa.approver_id = u.id
            WHERE oa.offer_id = :offer_id
            ORDER BY oa.approval_order
        """).bindparams(offer_id=offer_id)
    )
    approvals = approvals_result.fetchall()

    return OfferResponse(
        id=str(offer.id),
        application_id=str(offer.application_id),
        candidate_name=f"{offer.first_name} {offer.last_name}",
        candidate_email=offer.email,
        job_title=offer.job_title,
        position_title=offer.position_title,
        status=offer.status,
        salary={
            "base_salary": float(offer.base_salary),
            "currency": offer.currency,
            "bonus": float(offer.bonus) if offer.bonus else None,
            "bonus_type": offer.bonus_type,
            "stock_options": offer.stock_options,
            "other_benefits": json.loads(offer.other_benefits) if offer.other_benefits else None
        },
        start_date=offer.start_date.isoformat(),
        offer_expiry_date=offer.offer_expiry_date.isoformat(),
        employment_type=offer.employment_type,
        location=offer.location,
        remote_policy=offer.remote_policy,
        created_at=offer.created_at.isoformat(),
        created_by=offer.created_by_email,
        approval_status=offer.approval_status,
        approvals=[
            {
                "approver_name": f"{a.first_name} {a.last_name}",
                "approver_email": a.email,
                "status": a.status,
                "comments": a.comments,
                "decided_at": a.decided_at.isoformat() if a.decided_at else None
            }
            for a in approvals
        ],
        candidate_response=json.loads(offer.candidate_response) if offer.candidate_response else None
    )


async def notify_approvers(offer_id: UUID, approver_ids: List[UUID], candidate_name: str, position: str):
    """Notify approvers about pending offer."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        # Get approver details
        for approver_id in approver_ids:
            result = await db.execute(
                text("SELECT id, email, first_name, last_name FROM users WHERE id = :id")
                .bindparams(id=approver_id)
            )
            approver = result.first()

            if approver:
                recipient = NotificationRecipient(
                    id=str(approver.id),
                    email=approver.email,
                    name=f"{approver.first_name} {approver.last_name}",
                    role="approver"
                )

                await notification_service.trigger_notification(
                    event=NotificationEvent.OFFER_PENDING_APPROVAL,
                    recipients=[recipient],
                    context={
                        "approver_name": recipient.name,
                        "candidate_name": candidate_name,
                        "position_title": position,
                        "offer_id": str(offer_id)
                    }
                )


async def send_offer_email(offer_id: UUID, candidate_email: str, candidate_name: str, position: str, salary: float, start_date: date):
    """Send offer letter to candidate."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        # Get company name
        result = await db.execute(
            text("""
                SELECT c.name as company_name, o.department_id, d.name as department_name,
                       o.offer_expiry_date, o.base_salary, o.currency
                FROM offers o
                JOIN applications a ON o.application_id = a.id
                JOIN job_openings j ON a.job_opening_id = j.id
                JOIN companies c ON j.company_id = c.id
                LEFT JOIN departments d ON o.department_id = d.id
                WHERE o.id = :offer_id
            """).bindparams(offer_id=offer_id)
        )
        offer_data = result.first()

        if offer_data:
            recipient = NotificationRecipient(
                id=str(offer_id),
                email=candidate_email,
                name=candidate_name,
                role="candidate"
            )

            salary_summary = f"{offer_data.currency} {offer_data.base_salary:,.0f} per annum"

            await notification_service.trigger_notification(
                event=NotificationEvent.OFFER_SENT,
                recipients=[recipient],
                context={
                    "candidate_name": candidate_name,
                    "company_name": offer_data.company_name,
                    "position_title": position,
                    "department": offer_data.department_name or "Not specified",
                    "start_date": start_date.strftime("%B %d, %Y"),
                    "salary_summary": salary_summary,
                    "expiry_date": offer_data.offer_expiry_date.strftime("%B %d, %Y"),
                    "response_link": f"/candidate/offers/{offer_id}/respond"
                }
            )


async def send_revised_offer_email(offer_id: UUID):
    """Send revised offer to candidate."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        # Get offer details
        result = await db.execute(
            text("""
                SELECT o.*, c.first_name, c.last_name, c.email,
                       co.name as company_name, d.name as department_name
                FROM offers o
                JOIN applications a ON o.application_id = a.id
                JOIN candidates c ON a.candidate_id = c.id
                JOIN job_openings j ON a.job_opening_id = j.id
                JOIN companies co ON j.company_id = co.id
                LEFT JOIN departments d ON o.department_id = d.id
                WHERE o.id = :offer_id
            """).bindparams(offer_id=offer_id)
        )
        offer = result.first()

        if offer:
            recipient = NotificationRecipient(
                id=str(offer_id),
                email=offer.email,
                name=f"{offer.first_name} {offer.last_name}",
                role="candidate"
            )

            salary_summary = f"{offer.currency} {offer.base_salary:,.0f} per annum"

            await notification_service.trigger_notification(
                event=NotificationEvent.OFFER_SENT,
                recipients=[recipient],
                context={
                    "candidate_name": f"{offer.first_name} {offer.last_name}",
                    "company_name": offer.company_name,
                    "position_title": offer.position_title,
                    "department": offer.department_name or "Not specified",
                    "start_date": offer.start_date.strftime("%B %d, %Y"),
                    "salary_summary": salary_summary,
                    "expiry_date": offer.offer_expiry_date.strftime("%B %d, %Y"),
                    "response_link": f"/candidate/offers/{offer_id}/respond",
                    "revision_notice": "This is a revised offer based on our recent discussions."
                }
            )


async def notify_offer_response(offer_id: UUID, decision: str):
    """Notify hiring team of candidate's response."""
    from app.db.session import async_session_maker
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        notification_service = RecruitmentNotificationService(db)

        # Get offer and hiring team details
        result = await db.execute(
            text("""
                SELECT o.*, c.first_name, c.last_name, c.email,
                       j.hiring_manager_id, co.name as company_name,
                       d.name as department_name,
                       hm.email as hm_email, hm.first_name as hm_first, hm.last_name as hm_last
                FROM offers o
                JOIN applications a ON o.application_id = a.id
                JOIN candidates c ON a.candidate_id = c.id
                JOIN job_openings j ON a.job_opening_id = j.id
                JOIN companies co ON j.company_id = co.id
                LEFT JOIN departments d ON o.department_id = d.id
                LEFT JOIN users hm ON j.hiring_manager_id = hm.id
                WHERE o.id = :offer_id
            """).bindparams(offer_id=offer_id)
        )
        offer = result.first()

        if offer:
            # Determine event type based on decision
            if decision == "accept":
                event = NotificationEvent.OFFER_ACCEPTED
            elif decision == "reject":
                event = NotificationEvent.OFFER_REJECTED
            else:
                event = NotificationEvent.OFFER_NEGOTIATION

            # Notify hiring manager
            if offer.hm_email:
                recipient = NotificationRecipient(
                    id=str(offer.hiring_manager_id),
                    email=offer.hm_email,
                    name=f"{offer.hm_first} {offer.hm_last}",
                    role="hiring_manager"
                )

                await notification_service.trigger_notification(
                    event=event,
                    recipients=[recipient],
                    context={
                        "candidate_name": f"{offer.first_name} {offer.last_name}",
                        "company_name": offer.company_name,
                        "position_title": offer.position_title,
                        "department": offer.department_name or "Not specified",
                        "start_date": offer.start_date.strftime("%B %d, %Y"),
                        "decision": decision
                    }
                )


async def initiate_onboarding(
    offer_id: UUID,
    candidate_id: UUID,
    job_id: UUID,
    start_date: date,
    position_title: str,
    department_id: Optional[UUID]
):
    """Initiate onboarding workflow for hired candidate."""
    from app.db.session import async_session_maker
    from app.services.recruitment.onboarding_integration import OnboardingIntegrationService
    from app.services.recruitment.notification_service import (
        RecruitmentNotificationService,
        NotificationEvent,
        NotificationRecipient
    )

    async with async_session_maker() as db:
        # Get company_id from job
        job_result = await db.execute(
            text("SELECT company_id, hiring_manager_id FROM job_openings WHERE id = :id")
            .bindparams(id=job_id)
        )
        job = job_result.first()

        # Initiate onboarding
        onboarding_service = OnboardingIntegrationService(db)
        result = await onboarding_service.initiate_onboarding(
            offer_id=offer_id,
            candidate_id=candidate_id,
            job_id=job_id,
            start_date=start_date,
            position_title=position_title,
            department_id=department_id,
            reporting_to=job.hiring_manager_id if job else None,
            company_id=job.company_id if job else None
        )

        # Get candidate details for notification
        candidate_result = await db.execute(
            text("""
                SELECT c.*, co.name as company_name
                FROM candidates c
                JOIN applications a ON a.candidate_id = c.id
                JOIN job_openings j ON a.job_opening_id = j.id
                JOIN companies co ON j.company_id = co.id
                WHERE c.id = :candidate_id
            """).bindparams(candidate_id=candidate_id)
        )
        candidate = candidate_result.first()

        if candidate:
            notification_service = RecruitmentNotificationService(db)
            recipient = NotificationRecipient(
                id=str(candidate.id),
                email=candidate.email,
                name=f"{candidate.first_name} {candidate.last_name}",
                role="candidate"
            )

            await notification_service.trigger_notification(
                event=NotificationEvent.ONBOARDING_INITIATED,
                recipients=[recipient],
                context={
                    "candidate_name": f"{candidate.first_name} {candidate.last_name}",
                    "company_name": candidate.company_name,
                    "position_title": position_title,
                    "start_date": start_date.strftime("%B %d, %Y"),
                    "arrival_time": "9:00 AM",
                    "office_location": "Please check your joining letter",
                    "reporting_person": "HR Department",
                    "preboarding_link": f"/candidate/onboarding/{result['onboarding_id']}/preboarding",
                    "buddy_name": "will be assigned",
                    "hr_email": "hr@company.com"
                }
            )
