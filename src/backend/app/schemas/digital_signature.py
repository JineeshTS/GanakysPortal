"""
Digital Signature Schemas
Pydantic schemas for digital signature operations
"""
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict


# Enums
class SignatureProviderType(str, Enum):
    internal = "internal"
    aadhaar_esign = "aadhaar_esign"
    dsc = "dsc"
    emudhra = "emudhra"
    ncode = "ncode"
    sify = "sify"
    docusign = "docusign"
    adobe_sign = "adobe_sign"


class CertificateType(str, Enum):
    class_1 = "class_1"
    class_2 = "class_2"
    class_3 = "class_3"
    aadhaar = "aadhaar"
    organizational = "organizational"


class CertificateStatus(str, Enum):
    pending = "pending"
    active = "active"
    expired = "expired"
    revoked = "revoked"
    suspended = "suspended"


class SignatureStatus(str, Enum):
    draft = "draft"
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"
    expired = "expired"
    cancelled = "cancelled"


class SignerStatus(str, Enum):
    pending = "pending"
    viewed = "viewed"
    signed = "signed"
    rejected = "rejected"
    delegated = "delegated"


class SignatureType(str, Enum):
    electronic = "electronic"
    digital = "digital"
    aadhaar_esign = "aadhaar_esign"
    dsc = "dsc"


class DocumentType(str, Enum):
    pdf = "pdf"
    contract = "contract"
    agreement = "agreement"
    invoice = "invoice"
    purchase_order = "purchase_order"
    hr_document = "hr_document"
    legal_document = "legal_document"
    compliance_document = "compliance_document"
    other = "other"


# Signature Provider Schemas
class SignatureProviderBase(BaseModel):
    name: str = Field(..., max_length=100)
    provider_type: SignatureProviderType
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    config: Optional[Dict[str, Any]] = {}
    supported_signature_types: Optional[List[str]] = []
    supported_document_types: Optional[List[str]] = []
    max_signers_per_document: int = 10
    max_document_size_mb: int = 25
    signature_validity_days: int = 30


class SignatureProviderCreate(SignatureProviderBase):
    api_key: Optional[str] = None
    api_secret: Optional[str] = None


class SignatureProviderUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    max_signers_per_document: Optional[int] = None
    max_document_size_mb: Optional[int] = None
    signature_validity_days: Optional[int] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None


class SignatureProviderResponse(SignatureProviderBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


# Certificate Schemas
class SignatureCertificateBase(BaseModel):
    certificate_number: str = Field(..., max_length=100)
    certificate_type: CertificateType
    subject_name: str = Field(..., max_length=255)
    subject_email: Optional[str] = None
    subject_organization: Optional[str] = None
    valid_from: datetime
    valid_to: datetime


class SignatureCertificateCreate(SignatureCertificateBase):
    provider_id: Optional[UUID] = None
    user_id: Optional[UUID] = None
    certificate_data: Optional[str] = None
    public_key: Optional[str] = None
    serial_number: Optional[str] = None
    issuer: Optional[str] = None


class SignatureCertificateUpdate(BaseModel):
    status: Optional[CertificateStatus] = None
    is_verified: Optional[bool] = None
    verification_method: Optional[str] = None


class SignatureCertificateResponse(SignatureCertificateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    provider_id: Optional[UUID]
    user_id: Optional[UUID]
    serial_number: Optional[str]
    issuer: Optional[str]
    status: CertificateStatus
    is_verified: bool
    verified_at: Optional[datetime]
    total_signatures: int
    last_used_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class CertificateVerifyRequest(BaseModel):
    verification_method: str = "manual"


class CertificateRevokeRequest(BaseModel):
    reason: str = Field(..., min_length=1)


# Template Schemas
class SignerRoleConfig(BaseModel):
    role_name: str
    order: int
    required: bool = True
    allow_delegation: bool = False


class FieldPlacement(BaseModel):
    page: int
    x: float
    y: float
    width: float
    height: float
    required: bool = True
    role: Optional[str] = None


class SignatureTemplateBase(BaseModel):
    name: str = Field(..., max_length=200)
    description: Optional[str] = None
    template_code: str = Field(..., max_length=50)
    document_type: DocumentType = DocumentType.pdf
    signature_type: SignatureType = SignatureType.electronic
    signing_order: str = "sequential"
    expiry_days: int = 30
    reminder_frequency_days: int = 3
    allow_decline: bool = True
    allow_delegation: bool = False
    require_reason_on_decline: bool = True
    require_otp: bool = False
    require_aadhaar: bool = False
    require_pan: bool = False
    auto_archive: bool = True


class SignatureTemplateCreate(SignatureTemplateBase):
    signer_roles: Optional[List[SignerRoleConfig]] = []
    signature_fields: Optional[List[FieldPlacement]] = []
    initials_fields: Optional[List[FieldPlacement]] = []
    date_fields: Optional[List[FieldPlacement]] = []
    text_fields: Optional[List[FieldPlacement]] = []
    checkbox_fields: Optional[List[FieldPlacement]] = []
    on_complete_webhook: Optional[str] = None
    on_complete_email_template: Optional[str] = None


class SignatureTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None
    signature_type: Optional[SignatureType] = None
    signing_order: Optional[str] = None
    signer_roles: Optional[List[SignerRoleConfig]] = None
    signature_fields: Optional[List[FieldPlacement]] = None
    initials_fields: Optional[List[FieldPlacement]] = None
    date_fields: Optional[List[FieldPlacement]] = None
    text_fields: Optional[List[FieldPlacement]] = None
    expiry_days: Optional[int] = None
    reminder_frequency_days: Optional[int] = None
    allow_decline: Optional[bool] = None
    allow_delegation: Optional[bool] = None
    require_otp: Optional[bool] = None
    require_aadhaar: Optional[bool] = None
    is_active: Optional[bool] = None


class SignatureTemplateResponse(SignatureTemplateBase):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    signer_roles: List[Dict[str, Any]]
    signature_fields: List[Dict[str, Any]]
    initials_fields: List[Dict[str, Any]]
    date_fields: List[Dict[str, Any]]
    text_fields: List[Dict[str, Any]]
    checkbox_fields: List[Dict[str, Any]]
    on_complete_webhook: Optional[str]
    on_complete_email_template: Optional[str]
    is_active: bool
    version: int
    created_by: Optional[UUID]
    created_at: datetime
    updated_at: datetime


# Signer Schemas
class SignerInput(BaseModel):
    signer_user_id: Optional[UUID] = None
    signer_name: str = Field(..., max_length=200)
    signer_email: EmailStr
    signer_phone: Optional[str] = None
    signer_designation: Optional[str] = None
    signer_role: Optional[str] = None
    signing_order: int = 1


class SignerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    signer_user_id: Optional[UUID]
    signer_name: str
    signer_email: str
    signer_phone: Optional[str]
    signer_designation: Optional[str]
    signer_role: Optional[str]
    signing_order: int
    is_current: bool
    status: SignerStatus
    viewed_at: Optional[datetime]
    signed_at: Optional[datetime]
    rejected_at: Optional[datetime]
    rejection_reason: Optional[str]
    delegated_to_name: Optional[str]
    delegated_to_email: Optional[str]
    delegated_at: Optional[datetime]
    auth_method: Optional[str]
    otp_verified: bool
    aadhaar_verified: bool
    reminder_count: int
    last_reminder_at: Optional[datetime]
    created_at: datetime


# Document Schemas
class DocumentInput(BaseModel):
    document_name: str = Field(..., max_length=255)
    document_type: Optional[str] = "pdf"
    signature_fields: Optional[List[FieldPlacement]] = []
    initials_fields: Optional[List[FieldPlacement]] = []
    date_fields: Optional[List[FieldPlacement]] = []
    text_fields: Optional[List[FieldPlacement]] = []
    document_order: int = 1


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    request_id: UUID
    document_name: str
    document_type: Optional[str]
    document_size: Optional[int]
    page_count: int
    original_file_path: Optional[str]
    signed_file_path: Optional[str]
    original_hash: Optional[str]
    signed_hash: Optional[str]
    signature_fields: List[Dict[str, Any]]
    initials_fields: List[Dict[str, Any]]
    date_fields: List[Dict[str, Any]]
    text_fields: List[Dict[str, Any]]
    is_signed: bool
    signed_at: Optional[datetime]
    document_order: int
    created_at: datetime


# Request Schemas
class SignatureRequestCreate(BaseModel):
    template_id: Optional[UUID] = None
    subject: str = Field(..., max_length=500)
    message: Optional[str] = None
    document_type: Optional[DocumentType] = None
    signature_type: SignatureType = SignatureType.electronic
    source_type: Optional[str] = None
    source_id: Optional[UUID] = None
    source_reference: Optional[str] = None
    signing_order: str = "sequential"
    allow_decline: bool = True
    allow_delegation: bool = False
    expires_in_days: int = 30
    reminder_frequency_days: int = 3
    signers: List[SignerInput]
    metadata_json: Optional[Dict[str, Any]] = {}
    tags: Optional[List[str]] = []


class SignatureRequestUpdate(BaseModel):
    subject: Optional[str] = None
    message: Optional[str] = None
    expires_at: Optional[datetime] = None
    reminder_frequency_days: Optional[int] = None
    metadata_json: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class SignatureRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    template_id: Optional[UUID]
    request_number: str
    subject: str
    message: Optional[str]
    requester_id: UUID
    requester_name: Optional[str]
    requester_email: Optional[str]
    document_type: Optional[DocumentType]
    signature_type: Optional[SignatureType]
    source_type: Optional[str]
    source_id: Optional[UUID]
    source_reference: Optional[str]
    status: SignatureStatus
    current_signer_order: int
    total_signers: int
    completed_signers: int
    signing_order: str
    allow_decline: bool
    allow_delegation: bool
    sent_at: Optional[datetime]
    expires_at: Optional[datetime]
    completed_at: Optional[datetime]
    reminder_frequency_days: int
    last_reminder_at: Optional[datetime]
    reminder_count: int
    completion_type: Optional[str]
    metadata_json: Dict[str, Any]
    tags: List[str]
    created_at: datetime
    updated_at: datetime


class SignatureRequestDetailResponse(SignatureRequestResponse):
    documents: List[DocumentResponse] = []
    signers: List[SignerResponse] = []


# Signing Actions
class SignDocumentRequest(BaseModel):
    signature_data: str = Field(..., description="Base64 encoded signature image")
    signature_type: SignatureType = SignatureType.electronic
    certificate_id: Optional[UUID] = None
    otp_code: Optional[str] = None
    aadhaar_otp: Optional[str] = None


class SignFieldRequest(BaseModel):
    document_id: UUID
    field_type: str = "signature"  # signature, initials, date, text
    page_number: int
    x_position: float
    y_position: float
    width: Optional[float] = None
    height: Optional[float] = None
    value: str  # Base64 for signature/initials, text for others


class RejectSignatureRequest(BaseModel):
    reason: str = Field(..., min_length=1)


class DelegateSignatureRequest(BaseModel):
    delegatee_user_id: Optional[UUID] = None
    delegatee_name: str = Field(..., max_length=200)
    delegatee_email: EmailStr
    reason: str = Field(..., min_length=1)


# Document Signature Response
class DocumentSignatureResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    signer_id: UUID
    certificate_id: Optional[UUID]
    signature_type: SignatureType
    field_type: str
    page_number: int
    x_position: float
    y_position: float
    width: Optional[float]
    height: Optional[float]
    signature_hash: Optional[str]
    is_valid: bool
    verified_at: Optional[datetime]
    signed_at: datetime
    ip_address: Optional[str]
    geo_location: Optional[Dict[str, Any]]


# Verification
class VerificationRequest(BaseModel):
    verification_type: str = "signature"  # signature, document, certificate
    verification_method: Optional[str] = "hash"


class VerificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    signature_id: Optional[UUID]
    document_id: Optional[UUID]
    verification_type: str
    verification_method: Optional[str]
    is_valid: bool
    verification_status: str
    verification_message: Optional[str]
    verification_details: Optional[Dict[str, Any]]
    verified_at: datetime


# Audit Log
class SignatureAuditLogResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    request_id: Optional[UUID]
    document_id: Optional[UUID]
    signer_id: Optional[UUID]
    action: str
    action_category: Optional[str]
    description: Optional[str]
    actor_id: Optional[UUID]
    actor_type: Optional[str]
    actor_name: Optional[str]
    actor_email: Optional[str]
    old_values: Optional[Dict[str, Any]]
    new_values: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    created_at: datetime


class SignatureAuditLogListResponse(BaseModel):
    items: List[SignatureAuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Metrics
class SignatureMetricsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    company_id: UUID
    metric_date: date
    requests_created: int
    requests_sent: int
    requests_completed: int
    requests_rejected: int
    requests_expired: int
    requests_cancelled: int
    documents_uploaded: int
    documents_signed: int
    total_pages_signed: int
    signatures_pending: int
    signatures_completed: int
    signatures_rejected: int
    avg_time_to_sign_hours: Optional[float]
    min_time_to_sign_hours: Optional[float]
    max_time_to_sign_hours: Optional[float]
    electronic_signatures: int
    digital_signatures: int
    aadhaar_signatures: int
    reminders_sent: int


class SignatureDashboardMetrics(BaseModel):
    pending_requests: int
    in_progress_requests: int
    completed_today: int
    expiring_soon: int
    total_active_requests: int
    completion_rate: float
    avg_time_to_sign_hours: float
    by_status: Dict[str, int]
    by_signature_type: Dict[str, int]
    recent_activity: List[Dict[str, Any]]


# List Responses
class SignatureProviderListResponse(BaseModel):
    items: List[SignatureProviderResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SignatureCertificateListResponse(BaseModel):
    items: List[SignatureCertificateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SignatureTemplateListResponse(BaseModel):
    items: List[SignatureTemplateResponse]
    total: int
    page: int
    page_size: int
    pages: int


class SignatureRequestListResponse(BaseModel):
    items: List[SignatureRequestResponse]
    total: int
    page: int
    page_size: int
    pages: int


# Signer Portal Schemas
class SignerAccessResponse(BaseModel):
    request_id: UUID
    request_number: str
    subject: str
    message: Optional[str]
    requester_name: str
    requester_email: str
    signer_id: UUID
    signer_name: str
    signing_order: int
    is_current: bool
    status: SignerStatus
    documents: List[DocumentResponse]
    allow_decline: bool
    allow_delegation: bool
    require_otp: bool
    require_aadhaar: bool
    expires_at: Optional[datetime]


class SendReminderRequest(BaseModel):
    signer_id: Optional[UUID] = None  # If None, send to all pending signers
    message: Optional[str] = None


class BulkSignatureAction(BaseModel):
    request_ids: List[UUID]


class BulkActionResult(BaseModel):
    success_count: int
    failure_count: int
    results: List[Dict[str, Any]]
