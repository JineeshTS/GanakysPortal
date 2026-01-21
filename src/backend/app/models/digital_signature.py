"""
Digital Signature Models
Handles digital signatures, certificates, and document signing workflows
"""
from datetime import datetime
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Float, DateTime, Date,
    ForeignKey, Index, Enum as SQLEnum, JSON, ARRAY, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base


# Enums
class SignatureProviderType(str, enum.Enum):
    """Types of digital signature providers"""
    internal = "internal"  # Internal PKI
    aadhaar_esign = "aadhaar_esign"  # Aadhaar-based eSign
    dsc = "dsc"  # Digital Signature Certificate (USB token)
    emudhra = "emudhra"  # eMudhra
    ncode = "ncode"  # nCode
    sify = "sify"  # Sify eSign
    docusign = "docusign"  # DocuSign
    adobe_sign = "adobe_sign"  # Adobe Sign


class CertificateType(str, enum.Enum):
    """Types of digital certificates"""
    class_1 = "class_1"  # Email verification only
    class_2 = "class_2"  # Identity verified remotely
    class_3 = "class_3"  # In-person identity verification
    aadhaar = "aadhaar"  # Aadhaar-based
    organizational = "organizational"  # Organizational certificate


class CertificateStatus(str, enum.Enum):
    """Certificate status"""
    pending = "pending"
    active = "active"
    expired = "expired"
    revoked = "revoked"
    suspended = "suspended"


class SignatureStatus(str, enum.Enum):
    """Signature request status"""
    draft = "draft"
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    rejected = "rejected"
    expired = "expired"
    cancelled = "cancelled"


class SignerStatus(str, enum.Enum):
    """Individual signer status"""
    pending = "pending"
    viewed = "viewed"
    signed = "signed"
    rejected = "rejected"
    delegated = "delegated"


class SignatureType(str, enum.Enum):
    """Type of signature"""
    electronic = "electronic"  # Simple e-signature
    digital = "digital"  # PKI-based digital signature
    aadhaar_esign = "aadhaar_esign"  # Aadhaar eSign
    dsc = "dsc"  # DSC-based signature


class DocumentType(str, enum.Enum):
    """Type of document for signing"""
    pdf = "pdf"
    contract = "contract"
    agreement = "agreement"
    invoice = "invoice"
    purchase_order = "purchase_order"
    hr_document = "hr_document"
    legal_document = "legal_document"
    compliance_document = "compliance_document"
    other = "other"


# Models
class SignatureProvider(Base):
    """Configuration for signature providers"""
    __tablename__ = "signature_providers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(100), nullable=False)
    provider_type = Column(SQLEnum(SignatureProviderType, name="signature_provider_type", create_type=False), nullable=False)
    description = Column(Text)

    # Provider configuration
    api_endpoint = Column(String(500))
    api_key_encrypted = Column(Text)  # Encrypted API key
    api_secret_encrypted = Column(Text)  # Encrypted API secret
    certificate_chain = Column(Text)  # Provider certificate chain

    # Settings
    config = Column(JSONB, default=dict)  # Provider-specific configuration
    supported_signature_types = Column(ARRAY(String), default=list)
    supported_document_types = Column(ARRAY(String), default=list)

    # Limits
    max_signers_per_document = Column(Integer, default=10)
    max_document_size_mb = Column(Integer, default=25)
    signature_validity_days = Column(Integer, default=30)

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    certificates = relationship("SignatureCertificate", back_populates="provider", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_signature_providers_company", "company_id"),
        Index("idx_signature_providers_type", "provider_type"),
    )


class SignatureCertificate(Base):
    """Digital certificates for signing"""
    __tablename__ = "signature_certificates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    provider_id = Column(UUID(as_uuid=True), ForeignKey("signature_providers.id", ondelete="SET NULL"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    # Certificate details
    certificate_number = Column(String(100), nullable=False)
    certificate_type = Column(SQLEnum(CertificateType, name="certificate_type", create_type=False), nullable=False)
    subject_name = Column(String(255), nullable=False)  # CN in certificate
    subject_email = Column(String(255))
    subject_organization = Column(String(255))

    # Certificate data
    certificate_data = Column(Text)  # Base64 encoded certificate
    public_key = Column(Text)  # Public key
    serial_number = Column(String(100))
    issuer = Column(String(255))

    # Validity
    valid_from = Column(DateTime, nullable=False)
    valid_to = Column(DateTime, nullable=False)
    status = Column(SQLEnum(CertificateStatus, name="certificate_status", create_type=False), default=CertificateStatus.pending)

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_at = Column(DateTime)
    verified_by = Column(UUID(as_uuid=True))
    verification_method = Column(String(50))  # manual, ocsp, crl

    # Usage tracking
    total_signatures = Column(Integer, default=0)
    last_used_at = Column(DateTime)

    # Revocation
    revoked_at = Column(DateTime)
    revoked_by = Column(UUID(as_uuid=True))
    revocation_reason = Column(String(255))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    provider = relationship("SignatureProvider", back_populates="certificates")

    __table_args__ = (
        Index("idx_signature_certificates_company", "company_id"),
        Index("idx_signature_certificates_user", "user_id"),
        Index("idx_signature_certificates_status", "status"),
        UniqueConstraint("company_id", "certificate_number", name="uq_certificate_number_per_company"),
    )


class SignatureTemplate(Base):
    """Templates for signature workflows"""
    __tablename__ = "signature_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)

    name = Column(String(200), nullable=False)
    description = Column(Text)
    template_code = Column(String(50), nullable=False)

    # Document settings
    document_type = Column(SQLEnum(DocumentType, name="signature_document_type", create_type=False), default=DocumentType.pdf)
    signature_type = Column(SQLEnum(SignatureType, name="signature_type", create_type=False), default=SignatureType.electronic)

    # Signer configuration
    signer_roles = Column(JSONB, default=list)  # Predefined signer roles with order
    signing_order = Column(String(20), default="sequential")  # sequential, parallel, any_order

    # Field placements
    signature_fields = Column(JSONB, default=list)  # Predefined signature field placements
    initials_fields = Column(JSONB, default=list)
    date_fields = Column(JSONB, default=list)
    text_fields = Column(JSONB, default=list)
    checkbox_fields = Column(JSONB, default=list)

    # Workflow settings
    expiry_days = Column(Integer, default=30)
    reminder_frequency_days = Column(Integer, default=3)
    allow_decline = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=False)
    require_reason_on_decline = Column(Boolean, default=True)

    # Authentication
    require_otp = Column(Boolean, default=False)
    require_aadhaar = Column(Boolean, default=False)
    require_pan = Column(Boolean, default=False)

    # Completion actions
    on_complete_webhook = Column(String(500))
    on_complete_email_template = Column(String(100))
    auto_archive = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)
    version = Column(Integer, default=1)

    # Timestamps
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    requests = relationship("SignatureRequest", back_populates="template")

    __table_args__ = (
        Index("idx_signature_templates_company", "company_id"),
        UniqueConstraint("company_id", "template_code", name="uq_template_code_per_company"),
    )


class SignatureRequest(Base):
    """Signature request/envelope"""
    __tablename__ = "signature_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    template_id = Column(UUID(as_uuid=True), ForeignKey("signature_templates.id", ondelete="SET NULL"))

    # Request identification
    request_number = Column(String(50), nullable=False)
    subject = Column(String(500), nullable=False)
    message = Column(Text)  # Message to signers

    # Requester
    requester_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requester_name = Column(String(200))
    requester_email = Column(String(255))

    # Document info
    document_type = Column(SQLEnum(DocumentType, name="signature_document_type", create_type=False))
    signature_type = Column(SQLEnum(SignatureType, name="signature_type", create_type=False))

    # Reference to source
    source_type = Column(String(50))  # approval_request, contract, invoice, etc.
    source_id = Column(UUID(as_uuid=True))
    source_reference = Column(String(100))

    # Status
    status = Column(SQLEnum(SignatureStatus, name="signature_status", create_type=False), default=SignatureStatus.draft)
    current_signer_order = Column(Integer, default=1)
    total_signers = Column(Integer, default=0)
    completed_signers = Column(Integer, default=0)

    # Workflow settings
    signing_order = Column(String(20), default="sequential")
    allow_decline = Column(Boolean, default=True)
    allow_delegation = Column(Boolean, default=False)

    # Dates
    sent_at = Column(DateTime)
    expires_at = Column(DateTime)
    completed_at = Column(DateTime)

    # Reminders
    reminder_frequency_days = Column(Integer, default=3)
    last_reminder_at = Column(DateTime)
    reminder_count = Column(Integer, default=0)

    # Completion
    completion_type = Column(String(50))  # all_signed, expired, cancelled, rejected

    # Metadata
    metadata_json = Column(JSONB, default=dict)
    tags = Column(ARRAY(String), default=list)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    template = relationship("SignatureTemplate", back_populates="requests")
    documents = relationship("SignatureDocument", back_populates="request", cascade="all, delete-orphan")
    signers = relationship("SignatureSigner", back_populates="request", cascade="all, delete-orphan")
    audit_logs = relationship("SignatureAuditLog", back_populates="request", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_signature_requests_company", "company_id"),
        Index("idx_signature_requests_requester", "requester_id"),
        Index("idx_signature_requests_status", "status"),
        Index("idx_signature_requests_source", "source_type", "source_id"),
        UniqueConstraint("company_id", "request_number", name="uq_signature_request_number"),
    )


class SignatureDocument(Base):
    """Documents within a signature request"""
    __tablename__ = "signature_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("signature_requests.id", ondelete="CASCADE"), nullable=False)

    # Document info
    document_name = Column(String(255), nullable=False)
    document_type = Column(String(50))  # pdf, docx, etc.
    document_size = Column(Integer)  # bytes
    page_count = Column(Integer, default=1)

    # Storage
    original_file_path = Column(String(500))
    signed_file_path = Column(String(500))
    storage_bucket = Column(String(100))

    # Hash for integrity
    original_hash = Column(String(128))  # SHA-512
    signed_hash = Column(String(128))

    # Field placements
    signature_fields = Column(JSONB, default=list)
    initials_fields = Column(JSONB, default=list)
    date_fields = Column(JSONB, default=list)
    text_fields = Column(JSONB, default=list)

    # Status
    is_signed = Column(Boolean, default=False)
    signed_at = Column(DateTime)

    # Order
    document_order = Column(Integer, default=1)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request = relationship("SignatureRequest", back_populates="documents")
    signatures = relationship("DocumentSignature", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_signature_documents_request", "request_id"),
    )


class SignatureSigner(Base):
    """Signers for a signature request"""
    __tablename__ = "signature_signers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("signature_requests.id", ondelete="CASCADE"), nullable=False)

    # Signer info
    signer_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    signer_name = Column(String(200), nullable=False)
    signer_email = Column(String(255), nullable=False)
    signer_phone = Column(String(20))
    signer_designation = Column(String(200))
    signer_role = Column(String(100))  # approver, witness, reviewer, etc.

    # Order
    signing_order = Column(Integer, default=1)
    is_current = Column(Boolean, default=False)

    # Status
    status = Column(SQLEnum(SignerStatus, name="signer_status", create_type=False), default=SignerStatus.pending)

    # Actions
    viewed_at = Column(DateTime)
    signed_at = Column(DateTime)
    rejected_at = Column(DateTime)
    rejection_reason = Column(Text)

    # Delegation
    delegated_to_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    delegated_to_name = Column(String(200))
    delegated_to_email = Column(String(255))
    delegated_at = Column(DateTime)
    delegation_reason = Column(Text)

    # Authentication
    auth_method = Column(String(50))  # email, otp, aadhaar
    otp_verified = Column(Boolean, default=False)
    aadhaar_verified = Column(Boolean, default=False)

    # Access
    access_token = Column(String(255))  # Unique token for signing link
    access_token_expires = Column(DateTime)
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Reminders
    reminder_count = Column(Integer, default=0)
    last_reminder_at = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    request = relationship("SignatureRequest", back_populates="signers")
    signatures = relationship("DocumentSignature", back_populates="signer", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_signature_signers_request", "request_id"),
        Index("idx_signature_signers_user", "signer_user_id"),
        Index("idx_signature_signers_status", "status"),
        Index("idx_signature_signers_token", "access_token"),
    )


class DocumentSignature(Base):
    """Individual signature on a document"""
    __tablename__ = "document_signatures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("signature_documents.id", ondelete="CASCADE"), nullable=False)
    signer_id = Column(UUID(as_uuid=True), ForeignKey("signature_signers.id", ondelete="CASCADE"), nullable=False)
    certificate_id = Column(UUID(as_uuid=True), ForeignKey("signature_certificates.id"))

    # Signature type
    signature_type = Column(SQLEnum(SignatureType, name="signature_type", create_type=False), nullable=False)
    field_type = Column(String(50), default="signature")  # signature, initials, date, text

    # Position on document
    page_number = Column(Integer, nullable=False)
    x_position = Column(Float, nullable=False)
    y_position = Column(Float, nullable=False)
    width = Column(Float)
    height = Column(Float)

    # Signature data
    signature_data = Column(Text)  # Base64 signature image or digital signature
    signature_hash = Column(String(128))  # Hash of the signature

    # For digital signatures
    digital_signature = Column(Text)  # PKCS#7/CMS signature
    certificate_chain = Column(Text)  # Certificate chain used
    timestamp_token = Column(Text)  # RFC 3161 timestamp token

    # Verification
    is_valid = Column(Boolean, default=True)
    verified_at = Column(DateTime)
    verification_result = Column(JSONB)

    # Metadata
    signed_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    geo_location = Column(JSONB)  # lat, long, city, country

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("SignatureDocument", back_populates="signatures")
    signer = relationship("SignatureSigner", back_populates="signatures")

    __table_args__ = (
        Index("idx_document_signatures_document", "document_id"),
        Index("idx_document_signatures_signer", "signer_id"),
    )


class SignatureAuditLog(Base):
    """Audit log for signature activities"""
    __tablename__ = "signature_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    request_id = Column(UUID(as_uuid=True), ForeignKey("signature_requests.id", ondelete="CASCADE"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("signature_documents.id", ondelete="SET NULL"))
    signer_id = Column(UUID(as_uuid=True), ForeignKey("signature_signers.id", ondelete="SET NULL"))

    # Action details
    action = Column(String(100), nullable=False)  # created, sent, viewed, signed, rejected, etc.
    action_category = Column(String(50))  # request, document, signer, system
    description = Column(Text)

    # Actor
    actor_id = Column(UUID(as_uuid=True))
    actor_type = Column(String(20))  # user, signer, system
    actor_name = Column(String(200))
    actor_email = Column(String(255))

    # Change tracking
    old_values = Column(JSONB)
    new_values = Column(JSONB)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    geo_location = Column(JSONB)
    session_id = Column(String(100))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    request = relationship("SignatureRequest", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_signature_audit_company", "company_id"),
        Index("idx_signature_audit_request", "request_id"),
        Index("idx_signature_audit_action", "action"),
        Index("idx_signature_audit_created", "created_at"),
    )


class SignatureReminder(Base):
    """Scheduled reminders for pending signatures"""
    __tablename__ = "signature_reminders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    request_id = Column(UUID(as_uuid=True), ForeignKey("signature_requests.id", ondelete="CASCADE"), nullable=False)
    signer_id = Column(UUID(as_uuid=True), ForeignKey("signature_signers.id", ondelete="CASCADE"), nullable=False)

    # Reminder details
    reminder_type = Column(String(50), default="pending")  # pending, expiring, overdue
    scheduled_at = Column(DateTime, nullable=False)
    sent_at = Column(DateTime)

    # Status
    is_sent = Column(Boolean, default=False)
    is_cancelled = Column(Boolean, default=False)

    # Delivery
    delivery_channel = Column(String(20), default="email")  # email, sms, push
    delivery_status = Column(String(20))  # pending, sent, delivered, failed
    delivery_error = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_signature_reminders_request", "request_id"),
        Index("idx_signature_reminders_signer", "signer_id"),
        Index("idx_signature_reminders_scheduled", "scheduled_at", "is_sent"),
    )


class SignatureVerification(Base):
    """Signature verification records"""
    __tablename__ = "signature_verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    signature_id = Column(UUID(as_uuid=True), ForeignKey("document_signatures.id", ondelete="SET NULL"))
    document_id = Column(UUID(as_uuid=True), ForeignKey("signature_documents.id", ondelete="SET NULL"))

    # Verification details
    verification_type = Column(String(50), nullable=False)  # signature, document, certificate
    verification_method = Column(String(50))  # hash, ocsp, crl, timestamp

    # Results
    is_valid = Column(Boolean)
    verification_status = Column(String(50))  # valid, invalid, revoked, expired, unknown
    verification_message = Column(Text)
    verification_details = Column(JSONB)

    # Verifier
    verified_by = Column(UUID(as_uuid=True))
    verified_at = Column(DateTime, default=datetime.utcnow)

    # Context
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("idx_signature_verifications_company", "company_id"),
        Index("idx_signature_verifications_signature", "signature_id"),
        Index("idx_signature_verifications_document", "document_id"),
    )


class SignatureMetrics(Base):
    """Daily metrics for signature activity"""
    __tablename__ = "signature_metrics"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    metric_date = Column(Date, nullable=False)

    # Request metrics
    requests_created = Column(Integer, default=0)
    requests_sent = Column(Integer, default=0)
    requests_completed = Column(Integer, default=0)
    requests_rejected = Column(Integer, default=0)
    requests_expired = Column(Integer, default=0)
    requests_cancelled = Column(Integer, default=0)

    # Document metrics
    documents_uploaded = Column(Integer, default=0)
    documents_signed = Column(Integer, default=0)
    total_pages_signed = Column(Integer, default=0)

    # Signer metrics
    signatures_pending = Column(Integer, default=0)
    signatures_completed = Column(Integer, default=0)
    signatures_rejected = Column(Integer, default=0)

    # Time metrics
    avg_time_to_sign_hours = Column(Float)
    min_time_to_sign_hours = Column(Float)
    max_time_to_sign_hours = Column(Float)

    # By signature type
    electronic_signatures = Column(Integer, default=0)
    digital_signatures = Column(Integer, default=0)
    aadhaar_signatures = Column(Integer, default=0)

    # Reminders
    reminders_sent = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("idx_signature_metrics_company_date", "company_id", "metric_date"),
        UniqueConstraint("company_id", "metric_date", name="uq_signature_metrics_company_date"),
    )
