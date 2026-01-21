"""
Document Management Schemas - BE-006
Pydantic models for document and folder management
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


# Enums
class DocumentCategory(str, Enum):
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


class DocumentType(str, Enum):
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


class DocumentStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
    EXPIRED = "expired"


class AccessLevel(str, Enum):
    PUBLIC = "public"
    COMPANY = "company"
    DEPARTMENT = "department"
    PRIVATE = "private"


# Folder Schemas
class FolderCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_private: bool = False
    allowed_users: Optional[List[UUID]] = None
    allowed_roles: Optional[List[str]] = None
    allowed_departments: Optional[List[UUID]] = None
    max_file_size_mb: Optional[int] = None
    allowed_file_types: Optional[List[str]] = None


class FolderUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    is_private: Optional[bool] = None
    allowed_users: Optional[List[UUID]] = None
    allowed_roles: Optional[List[str]] = None
    allowed_departments: Optional[List[UUID]] = None
    is_archived: Optional[bool] = None


class FolderResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    parent_id: Optional[UUID]
    path: Optional[str]
    level: int
    color: Optional[str]
    icon: Optional[str]
    is_private: bool
    is_system: bool
    is_archived: bool
    document_count: int = 0
    subfolder_count: int = 0
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FolderTreeResponse(BaseModel):
    id: UUID
    name: str
    path: Optional[str]
    level: int
    children: List["FolderTreeResponse"] = []
    document_count: int = 0

    model_config = ConfigDict(from_attributes=True)


# Document Schemas
class DocumentUpload(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: DocumentCategory
    document_type: DocumentType
    folder_id: Optional[UUID] = None
    reference_type: Optional[str] = None
    reference_id: Optional[UUID] = None
    is_confidential: bool = False
    access_level: AccessLevel = AccessLevel.COMPANY
    allowed_users: Optional[List[UUID]] = None
    allowed_roles: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None
    reminder_days_before: Optional[int] = None
    tags: Optional[List[str]] = None


class DocumentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[DocumentCategory] = None
    document_type: Optional[DocumentType] = None
    folder_id: Optional[UUID] = None
    is_confidential: Optional[bool] = None
    access_level: Optional[AccessLevel] = None
    allowed_users: Optional[List[UUID]] = None
    allowed_roles: Optional[List[str]] = None
    expiry_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    status: Optional[DocumentStatus] = None


class DocumentResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    category: DocumentCategory
    document_type: DocumentType
    folder_id: Optional[UUID]
    folder_name: Optional[str] = None
    file_name: str
    file_size: Optional[int]
    mime_type: Optional[str]
    file_extension: Optional[str]
    version: int
    is_latest: bool
    is_confidential: bool
    access_level: str
    status: DocumentStatus
    tags: Optional[List[str]] = None
    expiry_date: Optional[datetime]
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentVersionResponse(BaseModel):
    id: UUID
    version: int
    file_name: str
    file_size: Optional[int]
    created_by: UUID
    created_at: datetime
    is_latest: bool

    model_config = ConfigDict(from_attributes=True)


class DocumentListResponse(BaseModel):
    success: bool = True
    data: List[DocumentResponse]
    meta: dict


# Share Schemas
class DocumentShareCreate(BaseModel):
    share_type: str = Field(..., pattern="^(user|email|link)$")
    shared_with_user: Optional[UUID] = None
    shared_with_email: Optional[str] = None
    can_view: bool = True
    can_download: bool = True
    can_edit: bool = False
    expires_at: Optional[datetime] = None
    max_downloads: Optional[int] = None
    is_password_protected: bool = False
    password: Optional[str] = None


class DocumentShareResponse(BaseModel):
    id: UUID
    document_id: UUID
    share_type: str
    shared_with_user: Optional[UUID]
    shared_with_email: Optional[str]
    share_link: Optional[str]
    can_view: bool
    can_download: bool
    can_edit: bool
    expires_at: Optional[datetime]
    download_count: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Audit Log Schema
class DocumentAuditLogResponse(BaseModel):
    id: UUID
    document_id: UUID
    action: str
    action_details: Optional[dict]
    user_id: Optional[UUID]
    ip_address: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Bulk Operations
class BulkMoveRequest(BaseModel):
    document_ids: List[UUID]
    target_folder_id: Optional[UUID]


class BulkDeleteRequest(BaseModel):
    document_ids: List[UUID]
    permanent: bool = False


class BulkShareRequest(BaseModel):
    document_ids: List[UUID]
    share_config: DocumentShareCreate
