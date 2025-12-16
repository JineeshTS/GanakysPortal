"""
Employee document schemas.
WBS Reference: Task 3.3.1.1
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel

from app.models.employee_document import DocumentType


class EmployeeDocumentBase(BaseModel):
    """Base schema for employee documents."""

    document_type: DocumentType
    description: Optional[str] = None


class EmployeeDocumentCreate(EmployeeDocumentBase):
    """Schema for creating employee document record."""

    pass


class EmployeeDocumentResponse(EmployeeDocumentBase):
    """Schema for employee document response."""

    id: UUID
    employee_id: UUID
    file_name: str
    file_size: int
    mime_type: str
    is_verified: bool
    verified_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeDocumentListResponse(BaseModel):
    """Schema for list of employee documents."""

    items: List[EmployeeDocumentResponse]
    total: int


class DocumentVerifyRequest(BaseModel):
    """Schema for document verification request."""

    is_verified: bool = True
