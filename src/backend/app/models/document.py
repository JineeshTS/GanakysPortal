"""
Document Management Models
"""
from datetime import datetime, date
from typing import Optional, List, TYPE_CHECKING
from uuid import UUID
from sqlalchemy import String, Text, Boolean, Integer, Date, DateTime, ForeignKey, Enum as SQLEnum, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum

if TYPE_CHECKING:
    from app.models.employee import Employee


class DocumentCategory(str, enum.Enum):
    POLICY = "policy"
    PROCEDURE = "procedure"
    WORK_INSTRUCTION = "work_instruction"
    FORM = "form"
    TEMPLATE = "template"
    CONTRACT = "contract"
    REPORT = "report"
    CERTIFICATE = "certificate"
    DRAWING = "drawing"
    SPECIFICATION = "specification"
    OTHER = "other"


class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    PUBLISHED = "published"
    OBSOLETE = "obsolete"
    ARCHIVED = "archived"


class DocumentFolder(Base, TimestampMixin, SoftDeleteMixin):
    """Document folder structure"""
    __tablename__ = "document_folders"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))
    parent_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("document_folders.id"))

    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)
    path: Mapped[str] = mapped_column(String(1000))

    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    owner_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    documents: Mapped[List["Document"]] = relationship(back_populates="folder")


class Document(Base, TimestampMixin, SoftDeleteMixin):
    """Document master"""
    __tablename__ = "documents"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))
    folder_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("document_folders.id"))

    document_number: Mapped[str] = mapped_column(String(100), unique=True)
    title: Mapped[str] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)

    category: Mapped[DocumentCategory] = mapped_column(SQLEnum(DocumentCategory))
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus), default=DocumentStatus.DRAFT)

    version: Mapped[int] = mapped_column(Integer, default=1)
    revision: Mapped[str] = mapped_column(String(20), default="A")

    file_name: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    file_type: Mapped[str] = mapped_column(String(100))
    mime_type: Mapped[str] = mapped_column(String(200))

    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    review_date: Mapped[Optional[date]] = mapped_column(Date)

    requires_acknowledgment: Mapped[bool] = mapped_column(Boolean, default=False)
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)
    access_level: Mapped[str] = mapped_column(String(50), default="internal")

    created_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    approved_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    approved_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    folder: Mapped[Optional["DocumentFolder"]] = relationship(back_populates="documents")
    versions: Mapped[List["DocumentVersion"]] = relationship(back_populates="document")


class DocumentVersion(Base, TimestampMixin):
    """Document version history"""
    __tablename__ = "document_versions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"))

    version: Mapped[int] = mapped_column(Integer)
    revision: Mapped[str] = mapped_column(String(20))

    file_name: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size: Mapped[int] = mapped_column(Integer)

    change_notes: Mapped[Optional[str]] = mapped_column(Text)
    uploaded_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))

    # Relationships
    document: Mapped["Document"] = relationship(back_populates="versions")


class DocumentType(str, enum.Enum):
    """Document type enumeration"""
    PDF = "pdf"
    DOC = "doc"
    DOCX = "docx"
    XLS = "xls"
    XLSX = "xlsx"
    PPT = "ppt"
    PPTX = "pptx"
    TXT = "txt"
    CSV = "csv"
    IMAGE = "image"
    OTHER = "other"


class DocumentShare(Base, TimestampMixin):
    """Document sharing records"""
    __tablename__ = "document_shares"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"))

    share_token: Mapped[str] = mapped_column(String(255), unique=True)
    shared_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    shared_with_email: Mapped[Optional[str]] = mapped_column(String(255))
    shared_with_user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))

    permission: Mapped[str] = mapped_column(String(50), default="view")  # view, download, edit
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    access_count: Mapped[int] = mapped_column(Integer, default=0)
    max_access_count: Mapped[Optional[int]] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))


class DocumentAuditLog(Base, TimestampMixin):
    """Document audit trail"""
    __tablename__ = "document_audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    document_id: Mapped[UUID] = mapped_column(ForeignKey("documents.id"))

    action: Mapped[str] = mapped_column(String(50))  # created, viewed, downloaded, updated, shared, deleted
    action_details: Mapped[Optional[str]] = mapped_column(Text)

    performed_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    ip_address: Mapped[Optional[str]] = mapped_column(String(50))
    user_agent: Mapped[Optional[str]] = mapped_column(String(500))


class EmployeeDocument(Base, TimestampMixin):
    """Employee-specific documents"""
    __tablename__ = "employee_documents"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    employee_id: Mapped[UUID] = mapped_column(ForeignKey("employees.id"))
    document_type: Mapped[str] = mapped_column(String(100))  # resume, id_proof, address_proof, etc.
    document_name: Mapped[str] = mapped_column(String(500))
    file_path: Mapped[str] = mapped_column(String(1000))
    file_size: Mapped[int] = mapped_column(Integer, default=0)
    mime_type: Mapped[Optional[str]] = mapped_column(String(200))
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date)
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    employee: Mapped["Employee"] = relationship(back_populates="documents")
