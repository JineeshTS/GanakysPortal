"""
Digital Signature API Endpoints
Handles signature requests, documents, signers, and verification
"""
from datetime import datetime, date
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user, get_current_company
from app.schemas.digital_signature import (
    # Provider
    SignatureProviderCreate, SignatureProviderUpdate, SignatureProviderResponse,
    SignatureProviderListResponse,
    # Certificate
    SignatureCertificateCreate, SignatureCertificateUpdate, SignatureCertificateResponse,
    SignatureCertificateListResponse, CertificateVerifyRequest, CertificateRevokeRequest,
    # Template
    SignatureTemplateCreate, SignatureTemplateUpdate, SignatureTemplateResponse,
    SignatureTemplateListResponse,
    # Request
    SignatureRequestCreate, SignatureRequestUpdate, SignatureRequestResponse,
    SignatureRequestDetailResponse, SignatureRequestListResponse,
    # Signer
    SignerResponse, DelegateSignatureRequest, RejectSignatureRequest,
    # Document/Signing
    DocumentResponse, SignDocumentRequest, SignFieldRequest, DocumentSignatureResponse,
    # Verification
    VerificationRequest, VerificationResponse,
    # Audit
    SignatureAuditLogResponse, SignatureAuditLogListResponse,
    # Metrics
    SignatureMetricsResponse, SignatureDashboardMetrics,
    # Portal
    SignerAccessResponse, SendReminderRequest,
    # Bulk
    BulkSignatureAction, BulkActionResult,
)
from app.services.digital_signature import (
    SignatureProviderService, SignatureCertificateService,
    SignatureTemplateService, SignatureRequestService,
    SignatureService, SignatureVerificationService,
    SignatureAuditService, SignatureMetricsService,
)

router = APIRouter(prefix="/signatures", tags=["Digital Signatures"])

# Service instances
provider_service = SignatureProviderService()
certificate_service = SignatureCertificateService()
template_service = SignatureTemplateService()
request_service = SignatureRequestService()
signature_service = SignatureService()
verification_service = SignatureVerificationService()
audit_service = SignatureAuditService()
metrics_service = SignatureMetricsService()


# ==================== Provider Endpoints ====================

@router.post("/providers", response_model=SignatureProviderResponse)
async def create_provider(
    provider_in: SignatureProviderCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Create a new signature provider configuration"""
    return await provider_service.create_provider(
        db=db,
        company_id=company_id,
        provider_in=provider_in
    )


@router.get("/providers", response_model=SignatureProviderListResponse)
async def list_providers(
    provider_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List signature providers"""
    return await provider_service.list_providers(
        db=db,
        company_id=company_id,
        provider_type=provider_type,
        is_active=is_active,
        page=page,
        page_size=page_size
    )


@router.get("/providers/{provider_id}", response_model=SignatureProviderResponse)
async def get_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get provider by ID"""
    provider = await provider_service.get_provider(db, provider_id, company_id)
    if not provider:
        raise HTTPException(status_code=404, detail="Provider not found")
    return provider


@router.patch("/providers/{provider_id}", response_model=SignatureProviderResponse)
async def update_provider(
    provider_id: UUID,
    provider_in: SignatureProviderUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Update provider"""
    return await provider_service.update_provider(
        db=db,
        provider_id=provider_id,
        company_id=company_id,
        provider_in=provider_in
    )


@router.delete("/providers/{provider_id}")
async def delete_provider(
    provider_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Delete provider"""
    await provider_service.delete_provider(db, provider_id, company_id)
    return {"status": "deleted"}


# ==================== Certificate Endpoints ====================

@router.post("/certificates", response_model=SignatureCertificateResponse)
async def create_certificate(
    certificate_in: SignatureCertificateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Register a new digital certificate"""
    return await certificate_service.create_certificate(
        db=db,
        company_id=company_id,
        certificate_in=certificate_in
    )


@router.get("/certificates", response_model=SignatureCertificateListResponse)
async def list_certificates(
    user_id: Optional[UUID] = None,
    certificate_type: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List certificates"""
    return await certificate_service.list_certificates(
        db=db,
        company_id=company_id,
        user_id=user_id,
        certificate_type=certificate_type,
        status=status,
        page=page,
        page_size=page_size
    )


@router.get("/certificates/{certificate_id}", response_model=SignatureCertificateResponse)
async def get_certificate(
    certificate_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get certificate by ID"""
    cert = await certificate_service.get_certificate(db, certificate_id, company_id)
    if not cert:
        raise HTTPException(status_code=404, detail="Certificate not found")
    return cert


@router.post("/certificates/{certificate_id}/verify", response_model=SignatureCertificateResponse)
async def verify_certificate(
    certificate_id: UUID,
    verify_in: CertificateVerifyRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Verify a certificate"""
    return await certificate_service.verify_certificate(
        db=db,
        certificate_id=certificate_id,
        company_id=company_id,
        verified_by=current_user.id,
        method=verify_in.verification_method
    )


@router.post("/certificates/{certificate_id}/revoke", response_model=SignatureCertificateResponse)
async def revoke_certificate(
    certificate_id: UUID,
    revoke_in: CertificateRevokeRequest,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Revoke a certificate"""
    return await certificate_service.revoke_certificate(
        db=db,
        certificate_id=certificate_id,
        company_id=company_id,
        revoked_by=current_user.id,
        reason=revoke_in.reason
    )


# ==================== Template Endpoints ====================

@router.post("/templates", response_model=SignatureTemplateResponse)
async def create_template(
    template_in: SignatureTemplateCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Create a new signature template"""
    return await template_service.create_template(
        db=db,
        company_id=company_id,
        template_in=template_in,
        created_by=current_user.id
    )


@router.get("/templates", response_model=SignatureTemplateListResponse)
async def list_templates(
    document_type: Optional[str] = None,
    signature_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List signature templates"""
    return await template_service.list_templates(
        db=db,
        company_id=company_id,
        document_type=document_type,
        signature_type=signature_type,
        is_active=is_active,
        search=search,
        page=page,
        page_size=page_size
    )


@router.get("/templates/{template_id}", response_model=SignatureTemplateResponse)
async def get_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get template by ID"""
    template = await template_service.get_template(db, template_id, company_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.patch("/templates/{template_id}", response_model=SignatureTemplateResponse)
async def update_template(
    template_id: UUID,
    template_in: SignatureTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Update template"""
    return await template_service.update_template(
        db=db,
        template_id=template_id,
        company_id=company_id,
        template_in=template_in
    )


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Delete template (soft delete)"""
    await template_service.delete_template(db, template_id, company_id)
    return {"status": "deleted"}


# ==================== Request Endpoints ====================

@router.post("/requests", response_model=SignatureRequestDetailResponse)
async def create_request(
    request_in: SignatureRequestCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Create a new signature request"""
    return await request_service.create_request(
        db=db,
        company_id=company_id,
        requester_id=current_user.id,
        requester_name=current_user.full_name,
        requester_email=current_user.email,
        request_in=request_in,
        background_tasks=background_tasks
    )


@router.get("/requests", response_model=SignatureRequestListResponse)
async def list_requests(
    status: Optional[str] = None,
    document_type: Optional[str] = None,
    signature_type: Optional[str] = None,
    source_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List signature requests"""
    return await request_service.list_requests(
        db=db,
        company_id=company_id,
        status=status,
        document_type=document_type,
        signature_type=signature_type,
        source_type=source_type,
        from_date=from_date,
        to_date=to_date,
        search=search,
        page=page,
        page_size=page_size
    )


@router.get("/requests/my-requests", response_model=SignatureRequestListResponse)
async def list_my_requests(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List requests created by current user"""
    return await request_service.list_requests(
        db=db,
        company_id=company_id,
        requester_id=current_user.id,
        status=status,
        page=page,
        page_size=page_size
    )


@router.get("/requests/pending-signatures", response_model=SignatureRequestListResponse)
async def list_pending_signatures(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List requests pending current user's signature"""
    return await request_service.list_pending_for_user(
        db=db,
        company_id=company_id,
        user_id=current_user.id,
        page=page,
        page_size=page_size
    )


@router.get("/requests/{request_id}", response_model=SignatureRequestDetailResponse)
async def get_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get request by ID with full details"""
    request = await request_service.get_request_detail(db, request_id, company_id)
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@router.patch("/requests/{request_id}", response_model=SignatureRequestResponse)
async def update_request(
    request_id: UUID,
    request_in: SignatureRequestUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Update request (only draft status)"""
    return await request_service.update_request(
        db=db,
        request_id=request_id,
        company_id=company_id,
        request_in=request_in
    )


@router.post("/requests/{request_id}/send", response_model=SignatureRequestResponse)
async def send_request(
    request_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Send request to signers"""
    return await request_service.send_request(
        db=db,
        request_id=request_id,
        company_id=company_id,
        sent_by=current_user.id,
        background_tasks=background_tasks
    )


@router.post("/requests/{request_id}/cancel", response_model=SignatureRequestResponse)
async def cancel_request(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Cancel a signature request"""
    return await request_service.cancel_request(
        db=db,
        request_id=request_id,
        company_id=company_id,
        cancelled_by=current_user.id
    )


@router.post("/requests/{request_id}/remind", response_model=dict)
async def send_reminder(
    request_id: UUID,
    reminder_in: SendReminderRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Send reminder to pending signers"""
    count = await request_service.send_reminders(
        db=db,
        request_id=request_id,
        company_id=company_id,
        signer_id=reminder_in.signer_id,
        message=reminder_in.message,
        background_tasks=background_tasks
    )
    return {"reminders_sent": count}


# ==================== Document Endpoints ====================

@router.post("/requests/{request_id}/documents", response_model=DocumentResponse)
async def upload_document(
    request_id: UUID,
    file: UploadFile = File(...),
    document_order: int = Query(1, ge=1),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Upload a document to a signature request"""
    return await request_service.add_document(
        db=db,
        request_id=request_id,
        company_id=company_id,
        file=file,
        document_order=document_order,
        uploaded_by=current_user.id
    )


@router.get("/requests/{request_id}/documents", response_model=List[DocumentResponse])
async def list_documents(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List documents in a request"""
    return await request_service.list_documents(db, request_id, company_id)


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID,
    signed: bool = False,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Download document (original or signed)"""
    return await request_service.download_document(
        db=db,
        document_id=document_id,
        company_id=company_id,
        signed=signed
    )


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Delete a document from request"""
    await request_service.delete_document(db, document_id, company_id)
    return {"status": "deleted"}


# ==================== Signer Endpoints ====================

@router.get("/requests/{request_id}/signers", response_model=List[SignerResponse])
async def list_signers(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List signers for a request"""
    return await request_service.list_signers(db, request_id, company_id)


@router.get("/signers/{signer_id}", response_model=SignerResponse)
async def get_signer(
    signer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get signer details"""
    signer = await signature_service.get_signer(db, signer_id, company_id)
    if not signer:
        raise HTTPException(status_code=404, detail="Signer not found")
    return signer


# ==================== Signing Endpoints ====================

@router.get("/sign/{access_token}", response_model=SignerAccessResponse)
async def get_signing_session(
    access_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Get signing session for signer portal (no auth required)"""
    session = await signature_service.get_signing_session(db, access_token)
    if not session:
        raise HTTPException(status_code=404, detail="Invalid or expired signing link")
    return session


@router.post("/sign/{access_token}/view")
async def mark_document_viewed(
    access_token: str,
    db: AsyncSession = Depends(get_db),
):
    """Mark document as viewed by signer"""
    await signature_service.mark_viewed(db, access_token)
    return {"status": "viewed"}


@router.post("/sign/{access_token}/sign", response_model=List[DocumentSignatureResponse])
async def sign_documents(
    access_token: str,
    sign_in: SignDocumentRequest,
    db: AsyncSession = Depends(get_db),
):
    """Sign all documents in request"""
    return await signature_service.sign_documents(
        db=db,
        access_token=access_token,
        sign_in=sign_in
    )


@router.post("/sign/{access_token}/sign-field", response_model=DocumentSignatureResponse)
async def sign_field(
    access_token: str,
    field_in: SignFieldRequest,
    db: AsyncSession = Depends(get_db),
):
    """Sign a specific field"""
    return await signature_service.sign_field(
        db=db,
        access_token=access_token,
        field_in=field_in
    )


@router.post("/sign/{access_token}/reject")
async def reject_signature(
    access_token: str,
    reject_in: RejectSignatureRequest,
    db: AsyncSession = Depends(get_db),
):
    """Reject signing request"""
    await signature_service.reject_signature(
        db=db,
        access_token=access_token,
        reason=reject_in.reason
    )
    return {"status": "rejected"}


@router.post("/sign/{access_token}/delegate", response_model=SignerResponse)
async def delegate_signature(
    access_token: str,
    delegate_in: DelegateSignatureRequest,
    db: AsyncSession = Depends(get_db),
):
    """Delegate signing to another person"""
    return await signature_service.delegate_signature(
        db=db,
        access_token=access_token,
        delegate_in=delegate_in
    )


@router.post("/sign/{access_token}/send-otp")
async def send_signing_otp(
    access_token: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Send OTP for signing verification"""
    await signature_service.send_otp(db, access_token, background_tasks)
    return {"status": "otp_sent"}


@router.post("/sign/{access_token}/verify-otp")
async def verify_signing_otp(
    access_token: str,
    otp_code: str,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP for signing"""
    result = await signature_service.verify_otp(db, access_token, otp_code)
    if not result:
        raise HTTPException(status_code=400, detail="Invalid OTP")
    return {"status": "verified"}


# ==================== Verification Endpoints ====================

@router.post("/verify/signature/{signature_id}", response_model=VerificationResponse)
async def verify_signature(
    signature_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Verify a signature"""
    return await verification_service.verify_signature(
        db=db,
        signature_id=signature_id,
        company_id=company_id,
        verified_by=current_user.id
    )


@router.post("/verify/document/{document_id}", response_model=VerificationResponse)
async def verify_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Verify all signatures on a document"""
    return await verification_service.verify_document(
        db=db,
        document_id=document_id,
        company_id=company_id,
        verified_by=current_user.id
    )


@router.get("/verify/document/{document_id}/signatures", response_model=List[DocumentSignatureResponse])
async def get_document_signatures(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get all signatures on a document"""
    return await verification_service.get_document_signatures(db, document_id, company_id)


# ==================== Audit Endpoints ====================

@router.get("/audit-logs", response_model=SignatureAuditLogListResponse)
async def list_audit_logs(
    request_id: Optional[UUID] = None,
    action: Optional[str] = None,
    actor_id: Optional[UUID] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """List signature audit logs"""
    return await audit_service.list_audit_logs(
        db=db,
        company_id=company_id,
        request_id=request_id,
        action=action,
        actor_id=actor_id,
        from_date=from_date,
        to_date=to_date,
        page=page,
        page_size=page_size
    )


@router.get("/requests/{request_id}/audit-trail", response_model=List[SignatureAuditLogResponse])
async def get_request_audit_trail(
    request_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get complete audit trail for a request"""
    return await audit_service.get_request_audit_trail(db, request_id, company_id)


# ==================== Metrics Endpoints ====================

@router.get("/metrics/dashboard", response_model=SignatureDashboardMetrics)
async def get_dashboard_metrics(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get signature dashboard metrics"""
    return await metrics_service.get_dashboard_metrics(
        db=db,
        company_id=company_id,
        user_id=current_user.id
    )


@router.get("/metrics/range", response_model=List[SignatureMetricsResponse])
async def get_metrics_range(
    from_date: date,
    to_date: date,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Get metrics for a date range"""
    return await metrics_service.get_metrics_range(
        db=db,
        company_id=company_id,
        from_date=from_date,
        to_date=to_date
    )


# ==================== Bulk Operations ====================

@router.post("/bulk/cancel", response_model=BulkActionResult)
async def bulk_cancel_requests(
    action_in: BulkSignatureAction,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Bulk cancel requests"""
    return await request_service.bulk_cancel(
        db=db,
        company_id=company_id,
        request_ids=action_in.request_ids,
        cancelled_by=current_user.id
    )


@router.post("/bulk/remind", response_model=BulkActionResult)
async def bulk_send_reminders(
    action_in: BulkSignatureAction,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
    company_id: UUID = Depends(get_current_company),
):
    """Bulk send reminders"""
    return await request_service.bulk_remind(
        db=db,
        company_id=company_id,
        request_ids=action_in.request_ids,
        background_tasks=background_tasks
    )
