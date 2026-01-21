"""
API Endpoints for Digital Delegation of Authority (DoA) & Approval Workflows
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_current_company
from app.schemas.doa import (
    # Authority Matrix
    AuthorityMatrixCreate, AuthorityMatrixUpdate, AuthorityMatrixResponse, AuthorityMatrixListResponse,
    # Authority Holder
    AuthorityHolderCreate, AuthorityHolderUpdate, AuthorityHolderResponse,
    # Delegation
    DelegationCreate, DelegationUpdate, DelegationRevoke, DelegationResponse, DelegationListResponse,
    # Workflow Template
    WorkflowTemplateCreate, WorkflowTemplateUpdate, WorkflowTemplateResponse, WorkflowTemplateListResponse,
    WorkflowLevelCreate, WorkflowLevelResponse,
    # Approval Request
    ApprovalRequestCreate, ApprovalRequestUpdate, ApprovalRequestResponse,
    ApprovalRequestDetailResponse, ApprovalRequestListResponse,
    # Approval Action
    ApprovalActionCreate, ApprovalActionResponse, BulkApprovalAction, BulkApprovalResult,
    # Escalation
    EscalationCreate, ApprovalEscalationResponse,
    # Inbox
    ApprovalInboxResponse,
    # Audit
    ApprovalAuditLogListResponse,
    # Metrics
    ApprovalMetricsResponse, ApprovalDashboardMetrics,
    # Helpers
    UserAuthorityCheck, UserAuthorityResult, WorkflowMatch,
    # Enums
    AuthorityType, ApprovalStatus, WorkflowType, RiskLevel,
)
from app.models.user import User
from app.models.company import CompanyProfile

router = APIRouter()


# =============================================================================
# AUTHORITY MATRIX ENDPOINTS
# =============================================================================

@router.get("/authority-matrix", response_model=AuthorityMatrixListResponse, tags=["Authority Matrix"])
async def list_authority_matrix(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    authority_type: Optional[AuthorityType] = None,
    transaction_type: Optional[str] = None,
    is_active: Optional[bool] = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all authority matrix entries for the company"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.list_authority_matrix(
        db, company.id,
        authority_type=authority_type,
        transaction_type=transaction_type,
        is_active=is_active,
        page=page,
        page_size=page_size
    )


@router.post("/authority-matrix", response_model=AuthorityMatrixResponse, status_code=status.HTTP_201_CREATED, tags=["Authority Matrix"])
async def create_authority_matrix(
    data: AuthorityMatrixCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Create a new authority matrix entry"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.create_authority_matrix(db, company.id, data, current_user.id)


@router.get("/authority-matrix/{matrix_id}", response_model=AuthorityMatrixResponse, tags=["Authority Matrix"])
async def get_authority_matrix(
    matrix_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get authority matrix entry by ID"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    matrix = await service.get_authority_matrix(db, matrix_id, company.id)
    if not matrix:
        raise HTTPException(status_code=404, detail="Authority matrix not found")
    return matrix


@router.put("/authority-matrix/{matrix_id}", response_model=AuthorityMatrixResponse, tags=["Authority Matrix"])
async def update_authority_matrix(
    matrix_id: UUID,
    data: AuthorityMatrixUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Update authority matrix entry"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.update_authority_matrix(db, matrix_id, company.id, data, current_user.id)


@router.delete("/authority-matrix/{matrix_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Authority Matrix"])
async def delete_authority_matrix(
    matrix_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Delete (deactivate) authority matrix entry"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    await service.delete_authority_matrix(db, matrix_id, company.id, current_user.id)


# =============================================================================
# AUTHORITY HOLDER ENDPOINTS
# =============================================================================

@router.get("/authority-matrix/{matrix_id}/holders", response_model=List[AuthorityHolderResponse], tags=["Authority Holders"])
async def list_authority_holders(
    matrix_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    is_active: Optional[bool] = True,
):
    """List all holders for an authority matrix entry"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.list_authority_holders(db, matrix_id, company.id, is_active)


@router.post("/authority-holders", response_model=AuthorityHolderResponse, status_code=status.HTTP_201_CREATED, tags=["Authority Holders"])
async def create_authority_holder(
    data: AuthorityHolderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Grant authority to a user"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.create_authority_holder(db, company.id, data, current_user.id)


@router.put("/authority-holders/{holder_id}", response_model=AuthorityHolderResponse, tags=["Authority Holders"])
async def update_authority_holder(
    holder_id: UUID,
    data: AuthorityHolderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Update authority holder"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    return await service.update_authority_holder(db, holder_id, company.id, data)


@router.delete("/authority-holders/{holder_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Authority Holders"])
async def revoke_authority_holder(
    holder_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Revoke authority from a user"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    await service.revoke_authority_holder(db, holder_id, company.id, current_user.id)


@router.post("/authority-check", response_model=UserAuthorityResult, tags=["Authority Holders"])
async def check_user_authority(
    data: UserAuthorityCheck,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    user_id: Optional[UUID] = None,
):
    """Check if a user has authority for a transaction"""
    from app.services.doa.authority_service import AuthorityService
    service = AuthorityService()
    check_user = user_id or current_user.id
    return await service.check_user_authority(db, company.id, check_user, data)


# =============================================================================
# DELEGATION ENDPOINTS
# =============================================================================

@router.get("/delegations", response_model=DelegationListResponse, tags=["Delegations"])
async def list_delegations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    delegator_id: Optional[UUID] = None,
    delegate_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List delegations"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.list_delegations(
        db, company.id,
        delegator_id=delegator_id,
        delegate_id=delegate_id,
        is_active=is_active,
        page=page,
        page_size=page_size
    )


@router.post("/delegations", response_model=DelegationResponse, status_code=status.HTTP_201_CREATED, tags=["Delegations"])
async def create_delegation(
    data: DelegationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Create a new delegation"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.create_delegation(db, company.id, current_user.id, data)


@router.get("/delegations/my-delegations", response_model=List[DelegationResponse], tags=["Delegations"])
async def get_my_delegations(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get delegations where current user is delegator"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.get_user_delegations(db, company.id, current_user.id, as_delegator=True)


@router.get("/delegations/delegated-to-me", response_model=List[DelegationResponse], tags=["Delegations"])
async def get_delegated_to_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get delegations where current user is delegate"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.get_user_delegations(db, company.id, current_user.id, as_delegator=False)


@router.get("/delegations/{delegation_id}", response_model=DelegationResponse, tags=["Delegations"])
async def get_delegation(
    delegation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get delegation by ID"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    delegation = await service.get_delegation(db, delegation_id, company.id)
    if not delegation:
        raise HTTPException(status_code=404, detail="Delegation not found")
    return delegation


@router.put("/delegations/{delegation_id}", response_model=DelegationResponse, tags=["Delegations"])
async def update_delegation(
    delegation_id: UUID,
    data: DelegationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Update delegation"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.update_delegation(db, delegation_id, company.id, data)


@router.post("/delegations/{delegation_id}/revoke", response_model=DelegationResponse, tags=["Delegations"])
async def revoke_delegation(
    delegation_id: UUID,
    data: DelegationRevoke,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Revoke a delegation"""
    from app.services.doa.delegation_service import DelegationService
    service = DelegationService()
    return await service.revoke_delegation(db, delegation_id, company.id, current_user.id, data.reason)


# =============================================================================
# WORKFLOW TEMPLATE ENDPOINTS
# =============================================================================

@router.get("/workflows", response_model=WorkflowTemplateListResponse, tags=["Workflow Templates"])
async def list_workflow_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    transaction_type: Optional[str] = None,
    workflow_type: Optional[WorkflowType] = None,
    is_active: Optional[bool] = True,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List workflow templates"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    return await service.list_workflow_templates(
        db, company.id,
        transaction_type=transaction_type,
        workflow_type=workflow_type,
        is_active=is_active,
        page=page,
        page_size=page_size
    )


@router.post("/workflows", response_model=WorkflowTemplateResponse, status_code=status.HTTP_201_CREATED, tags=["Workflow Templates"])
async def create_workflow_template(
    data: WorkflowTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Create a new workflow template"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    return await service.create_workflow_template(db, company.id, data, current_user.id)


@router.get("/workflows/{workflow_id}", response_model=WorkflowTemplateResponse, tags=["Workflow Templates"])
async def get_workflow_template(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get workflow template by ID"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    workflow = await service.get_workflow_template(db, workflow_id, company.id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow template not found")
    return workflow


@router.put("/workflows/{workflow_id}", response_model=WorkflowTemplateResponse, tags=["Workflow Templates"])
async def update_workflow_template(
    workflow_id: UUID,
    data: WorkflowTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Update workflow template"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    return await service.update_workflow_template(db, workflow_id, company.id, data)


@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Workflow Templates"])
async def delete_workflow_template(
    workflow_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Delete (deactivate) workflow template"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    await service.delete_workflow_template(db, workflow_id, company.id)


@router.post("/workflows/{workflow_id}/clone", response_model=WorkflowTemplateResponse, tags=["Workflow Templates"])
async def clone_workflow_template(
    workflow_id: UUID,
    new_name: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Clone a workflow template"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    return await service.clone_workflow_template(db, workflow_id, company.id, new_name, current_user.id)


@router.post("/workflows/match", response_model=WorkflowMatch, tags=["Workflow Templates"])
async def find_matching_workflow(
    transaction_type: str,
    amount: Optional[float] = None,
    extra_conditions: Optional[dict] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Find matching workflow for a transaction"""
    from app.services.doa.workflow_service import WorkflowService
    service = WorkflowService()
    return await service.find_matching_workflow(
        db, company.id, transaction_type, amount, extra_conditions
    )


# =============================================================================
# APPROVAL REQUEST ENDPOINTS
# =============================================================================

@router.get("/requests", response_model=ApprovalRequestListResponse, tags=["Approval Requests"])
async def list_approval_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    status: Optional[ApprovalStatus] = None,
    transaction_type: Optional[str] = None,
    requester_id: Optional[UUID] = None,
    risk_level: Optional[RiskLevel] = None,
    is_urgent: Optional[bool] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List approval requests"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.list_approval_requests(
        db, company.id,
        status=status,
        transaction_type=transaction_type,
        requester_id=requester_id,
        risk_level=risk_level,
        is_urgent=is_urgent,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.post("/requests", response_model=ApprovalRequestResponse, status_code=status.HTTP_201_CREATED, tags=["Approval Requests"])
async def create_approval_request(
    data: ApprovalRequestCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Create a new approval request"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    ip_address = request.client.host if request.client else None
    return await service.create_approval_request(
        db, company.id, current_user.id, data, ip_address
    )


@router.get("/requests/my-requests", response_model=ApprovalRequestListResponse, tags=["Approval Requests"])
async def get_my_approval_requests(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    status: Optional[ApprovalStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """Get approval requests submitted by current user"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.list_approval_requests(
        db, company.id,
        requester_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )


@router.get("/requests/{request_id}", response_model=ApprovalRequestDetailResponse, tags=["Approval Requests"])
async def get_approval_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get approval request by ID with full details"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    approval_request = await service.get_approval_request_detail(db, request_id, company.id)
    if not approval_request:
        raise HTTPException(status_code=404, detail="Approval request not found")
    return approval_request


@router.put("/requests/{request_id}", response_model=ApprovalRequestResponse, tags=["Approval Requests"])
async def update_approval_request(
    request_id: UUID,
    data: ApprovalRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Update approval request (only if in draft status)"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.update_approval_request(db, request_id, company.id, data, current_user.id)


@router.post("/requests/{request_id}/cancel", response_model=ApprovalRequestResponse, tags=["Approval Requests"])
async def cancel_approval_request(
    request_id: UUID,
    reason: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Cancel an approval request"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.cancel_approval_request(db, request_id, company.id, current_user.id, reason)


@router.post("/requests/{request_id}/recall", response_model=ApprovalRequestResponse, tags=["Approval Requests"])
async def recall_approval_request(
    request_id: UUID,
    reason: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Recall an approval request (only by requester, if still pending)"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.recall_approval_request(db, request_id, company.id, current_user.id, reason)


# =============================================================================
# APPROVAL INBOX ENDPOINTS
# =============================================================================

@router.get("/inbox", response_model=ApprovalInboxResponse, tags=["Approval Inbox"])
async def get_approval_inbox(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    transaction_type: Optional[str] = None,
    priority_min: Optional[int] = None,
    is_urgent: Optional[bool] = None,
    sla_status: Optional[str] = None,  # "on_track", "at_risk", "breached"
    sort_by: str = Query("assigned_at", regex="^(assigned_at|due_at|priority|amount)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$"),
):
    """Get approval inbox for current user"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    return await service.get_approval_inbox(
        db, company.id, current_user.id,
        transaction_type=transaction_type,
        priority_min=priority_min,
        is_urgent=is_urgent,
        sla_status=sla_status,
        sort_by=sort_by,
        sort_order=sort_order
    )


# =============================================================================
# APPROVAL ACTION ENDPOINTS
# =============================================================================

@router.post("/actions/{action_id}/approve", response_model=ApprovalActionResponse, tags=["Approval Actions"])
async def approve_request(
    action_id: UUID,
    data: ApprovalActionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Approve an approval request"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await service.process_approval_action(
        db, action_id, company.id, current_user.id,
        action="approve",
        comments=data.comments,
        conditions=data.conditions,
        ip_address=ip_address,
        user_agent=user_agent,
        channel="web"
    )


@router.post("/actions/{action_id}/reject", response_model=ApprovalActionResponse, tags=["Approval Actions"])
async def reject_request(
    action_id: UUID,
    data: ApprovalActionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Reject an approval request"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await service.process_approval_action(
        db, action_id, company.id, current_user.id,
        action="reject",
        comments=data.comments,
        ip_address=ip_address,
        user_agent=user_agent,
        channel="web"
    )


@router.post("/actions/{action_id}/delegate", response_model=ApprovalActionResponse, tags=["Approval Actions"])
async def delegate_approval(
    action_id: UUID,
    data: ApprovalActionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Delegate an approval to another user"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    if not data.delegate_to:
        raise HTTPException(status_code=400, detail="delegate_to is required")
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await service.delegate_approval(
        db, action_id, company.id, current_user.id, data.delegate_to,
        comments=data.comments,
        ip_address=ip_address,
        user_agent=user_agent
    )


@router.post("/actions/{action_id}/request-info", response_model=ApprovalActionResponse, tags=["Approval Actions"])
async def request_more_info(
    action_id: UUID,
    data: ApprovalActionCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Request more information from requester"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await service.process_approval_action(
        db, action_id, company.id, current_user.id,
        action="request_info",
        comments=data.comments,
        ip_address=ip_address,
        user_agent=user_agent,
        channel="web"
    )


@router.post("/actions/bulk", response_model=BulkApprovalResult, tags=["Approval Actions"])
async def bulk_approval_action(
    data: BulkApprovalAction,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Perform bulk approval action"""
    from app.services.doa.approval_service import ApprovalService
    service = ApprovalService()
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    return await service.bulk_approval_action(
        db, company.id, current_user.id, data,
        ip_address=ip_address,
        user_agent=user_agent
    )


# =============================================================================
# ESCALATION ENDPOINTS
# =============================================================================

@router.post("/requests/{request_id}/escalate", response_model=ApprovalEscalationResponse, tags=["Escalations"])
async def escalate_request(
    request_id: UUID,
    data: EscalationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Manually escalate an approval request"""
    from app.services.doa.escalation_service import EscalationService
    service = EscalationService()
    return await service.manual_escalate(
        db, request_id, company.id, current_user.id,
        to_approver_id=data.to_approver_id,
        reason=data.reason
    )


@router.get("/requests/{request_id}/escalations", response_model=List[ApprovalEscalationResponse], tags=["Escalations"])
async def get_request_escalations(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get escalation history for a request"""
    from app.services.doa.escalation_service import EscalationService
    service = EscalationService()
    return await service.get_request_escalations(db, request_id, company.id)


# =============================================================================
# AUDIT LOG ENDPOINTS
# =============================================================================

@router.get("/audit-logs", response_model=ApprovalAuditLogListResponse, tags=["Audit Logs"])
async def list_audit_logs(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    request_id: Optional[UUID] = None,
    action: Optional[str] = None,
    actor_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
):
    """List approval audit logs"""
    from app.services.doa.audit_service import AuditService
    service = AuditService()
    return await service.list_audit_logs(
        db, company.id,
        request_id=request_id,
        action=action,
        actor_id=actor_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.get("/requests/{request_id}/audit-trail", response_model=List[ApprovalAuditLogListResponse], tags=["Audit Logs"])
async def get_request_audit_trail(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get complete audit trail for a request"""
    from app.services.doa.audit_service import AuditService
    service = AuditService()
    return await service.get_request_audit_trail(db, request_id, company.id)


# =============================================================================
# METRICS & DASHBOARD ENDPOINTS
# =============================================================================

@router.get("/dashboard", response_model=ApprovalDashboardMetrics, tags=["Dashboard"])
async def get_approval_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Get approval dashboard metrics for current user"""
    from app.services.doa.metrics_service import DoAMetricsService
    service = DoAMetricsService()
    return await service.get_dashboard_metrics(db, company.id, current_user.id)


@router.get("/metrics", response_model=List[ApprovalMetricsResponse], tags=["Metrics"])
async def get_approval_metrics(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
    from_date: date = Query(...),
    to_date: date = Query(...),
):
    """Get approval metrics for date range"""
    from app.services.doa.metrics_service import DoAMetricsService
    service = DoAMetricsService()
    return await service.get_metrics_range(db, company.id, from_date, to_date)


@router.post("/metrics/calculate", status_code=status.HTTP_202_ACCEPTED, tags=["Metrics"])
async def calculate_daily_metrics(
    metric_date: date = Query(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    company: CompanyProfile = Depends(get_current_company),
):
    """Trigger calculation of daily metrics"""
    from app.services.doa.metrics_service import DoAMetricsService
    service = DoAMetricsService()
    calc_date = metric_date or date.today()
    await service.calculate_daily_metrics(db, company.id, calc_date)
    return {"message": f"Metrics calculation triggered for {calc_date}"}
