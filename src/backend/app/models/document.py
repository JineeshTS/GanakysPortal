"""
Document Management Models - BE-006 & BE-009
Folder and document management with version control
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Integer, Boolean, DateTime,
    ForeignKey, Enum, Text, BigInteger, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class Folder(Base):
    """Folder structure for organizing documents."""
    __tablename__ = "folders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)

    # Folder info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    color = Column(String(20))
    icon = Column(String(50))

    # Hierarchy
    parent_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), index=True)
    path = Column(String(1000))  # Materialized path: /root/hr/policies
    level = Column(Integer, default=0)

    # Permissions
    is_private = Column(Boolean, default=False)
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    allowed_users = Column(Text)  # JSON array of user IDs
    allowed_roles = Column(Text)  # JSON array of roles
    allowed_departments = Column(Text)  # JSON array of department IDs
    inherit_permissions = Column(Boolean, default=True)

    # Settings
    allow_subfolders = Column(Boolean, default=True)
    max_file_size_mb = Column(Integer)
    allowed_file_types = Column(Text)  # JSON array

    # Status
    is_system = Column(Boolean, default=False)
    is_archived = Column(Boolean, default=False)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent = relationship("Folder", remote_side=[id], backref="children")
    documents = relationship("Document", back_populates="folder")

    __table_args__ = (
        Index('ix_folders_company_path', 'company_id', 'path'),
        Index('ix_folders_company_parent', 'company_id', 'parent_id'),
    )


class DocumentCategory(str, PyEnum):
    """Document category."""
    HR = "hr"
    FINANCE = "finance"
    LEGAL = "legal"
    COMPLIANCE = "compliance"
    PROJECT = "project"
    GENERAL = "general"
    EMPLOYEE = "employee"
    PAYROLL = "payroll"
    INVOICE = "invoice"
    CONTRACT = "contract"


class DocumentType(str, PyEnum):
    """Document types."""
    # HR Documents
    OFFER_LETTER = "offer_letter"
    APPOINTMENT_LETTER = "appointment_letter"
    EXPERIENCE_LETTER = "experience_letter"
    RELIEVING_LETTER = "relieving_letter"
    SALARY_SLIP = "salary_slip"
    FORM_16 = "form_16"
    BONUS_LETTER = "bonus_letter"
    INCREMENT_LETTER = "increment_letter"
    WARNING_LETTER = "warning_letter"
    TERMINATION_LETTER = "termination_letter"

    # Employee Documents
    RESUME = "resume"
    PHOTO = "photo"
    ID_PROOF = "id_proof"
    ADDRESS_PROOF = "address_proof"
    PAN_CARD = "pan_card"
    AADHAAR = "aadhaar"
    PASSPORT = "passport"
    EDUCATIONAL_CERT = "educational_cert"
    EXPERIENCE_CERT = "experience_cert"
    BANK_DETAILS = "bank_details"

    # Finance Documents
    INVOICE = "invoice"
    RECEIPT = "receipt"
    PURCHASE_ORDER = "purchase_order"
    QUOTATION = "quotation"
    CREDIT_NOTE = "credit_note"
    DEBIT_NOTE = "debit_note"
    BANK_STATEMENT = "bank_statement"
    CHALLAN = "challan"

    # Compliance
    GST_RETURN = "gst_return"
    TDS_RETURN = "tds_return"
    PF_CHALLAN = "pf_challan"
    ESI_CHALLAN = "esi_challan"
    PT_CHALLAN = "pt_challan"
    ROC_FILING = "roc_filing"

    # Legal
    AGREEMENT = "agreement"
    CONTRACT = "contract"
    NDA = "nda"
    MOU = "mou"
    POWER_OF_ATTORNEY = "power_of_attorney"

    # Others
    REPORT = "report"
    PRESENTATION = "presentation"
    SPREADSHEET = "spreadsheet"
    OTHER = "other"


class DocumentStatus(str, PyEnum):
    """Document status."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    EXPIRED = "expired"


class Document(Base):
    """Document storage and management."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False, index=True)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("folders.id"), index=True)

    # Document info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(50), nullable=True)  # Changed from Enum for DB compatibility
    document_type = Column(String(50), nullable=True)  # Changed from Enum for DB compatibility

    # File details
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(BigInteger)  # Size in bytes
    mime_type = Column(String(100))
    file_extension = Column(String(20))

    # Storage
    storage_type = Column(String(20), default="local")  # local, s3, azure, gcs
    storage_bucket = Column(String(255))
    storage_key = Column(String(500))

    # Version control
    version = Column(Integer, default=1)
    parent_document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"))
    is_latest = Column(Boolean, default=True)

    # Reference
    reference_type = Column(String(50))  # employee, invoice, project, etc.
    reference_id = Column(UUID(as_uuid=True))

    # Access control
    is_confidential = Column(Boolean, default=False)
    access_level = Column(String(20), default="company")  # public, company, department, private
    allowed_users = Column(Text)  # JSON array of user IDs
    allowed_roles = Column(Text)  # JSON array of role names

    # Expiry
    expiry_date = Column(DateTime)
    reminder_days_before = Column(Integer)
    reminder_sent = Column(Boolean, default=False)

    # Status
    status = Column(String(20), default="active")  # Changed from Enum for DB compatibility

    # Metadata
    tags = Column(Text)  # JSON array of tags
    custom_fields = Column(Text)  # JSON object

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_document = relationship("Document", remote_side=[id], back_populates="versions")
    versions = relationship("Document", foreign_keys=[parent_document_id], back_populates="parent_document")
    folder = relationship("Folder", back_populates="documents")


class DocumentTemplate(Base):
    """Document templates for generation."""
    __tablename__ = "document_templates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("companies.id"), nullable=False)

    # Template info
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(Enum(DocumentCategory), nullable=False)
    document_type = Column(Enum(DocumentType), nullable=False)

    # Template content
    template_format = Column(String(20), nullable=False)  # html, docx, pdf
    template_path = Column(String(500))
    template_content = Column(Text)  # HTML content for simple templates

    # Variables
    variables = Column(Text)  # JSON schema of available variables

    # Header/Footer
    header_content = Column(Text)
    footer_content = Column(Text)
    include_letterhead = Column(Boolean, default=True)

    # Status
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    updated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DocumentShare(Base):
    """Document sharing records."""
    __tablename__ = "document_shares"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Sharing method
    share_type = Column(String(20), nullable=False)  # user, email, link

    # For user sharing
    shared_with_user = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # For email sharing
    shared_with_email = Column(String(255))

    # For link sharing
    share_token = Column(String(100), unique=True)
    share_link = Column(String(500))

    # Permissions
    can_view = Column(Boolean, default=True)
    can_download = Column(Boolean, default=True)
    can_edit = Column(Boolean, default=False)

    # Expiry
    expires_at = Column(DateTime)
    max_downloads = Column(Integer)
    download_count = Column(Integer, default=0)

    # Password protection
    is_password_protected = Column(Boolean, default=False)
    password_hash = Column(String(255))

    # Status
    is_active = Column(Boolean, default=True)
    revoked_at = Column(DateTime)
    revoked_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    # Audit
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document")


class DocumentAuditLog(Base):
    """Document access and action audit log."""
    __tablename__ = "document_audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Action details
    action = Column(String(50), nullable=False)  # view, download, edit, share, delete
    action_details = Column(Text)  # JSON with additional details

    # Actor
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    ip_address = Column(String(45))
    user_agent = Column(String(500))

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document")


class EmployeeDocument(Base):
    """Link table for employee documents with additional metadata."""
    __tablename__ = "employee_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=False)

    # Document metadata
    document_type = Column(Enum(DocumentType), nullable=False)
    document_number = Column(String(100))  # PAN number, Aadhaar number, etc.

    # Validity
    issue_date = Column(DateTime)
    expiry_date = Column(DateTime)
    issuing_authority = Column(String(255))

    # Verification
    is_verified = Column(Boolean, default=False)
    verified_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    verified_at = Column(DateTime)
    verification_remarks = Column(Text)

    # Status
    is_active = Column(Boolean, default=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="documents")
    document = relationship("Document")
