"""
Employee Documents model.
WBS Reference: Task 3.3.1.1.1
"""
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Optional
import uuid

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.employee import Employee
    from app.models.user import User


class DocumentType(str, enum.Enum):
    """Types of employee documents."""

    # Personal
    PROFILE_PHOTO = "profile_photo"
    RESUME_CV = "resume_cv"

    # Identity
    PAN_CARD = "pan_card"
    AADHAAR_CARD = "aadhaar_card"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    VOTER_ID = "voter_id"

    # Address Proof
    ADDRESS_PROOF = "address_proof"

    # Education
    SSC_CERTIFICATE = "ssc_certificate"
    HSC_CERTIFICATE = "hsc_certificate"
    DEGREE_CERTIFICATE = "degree_certificate"
    PG_CERTIFICATE = "pg_certificate"
    OTHER_CERTIFICATE = "other_certificate"

    # Previous Employment
    EXPERIENCE_LETTER = "experience_letter"
    RELIEVING_LETTER = "relieving_letter"
    PAYSLIP = "payslip"
    FORM_16 = "form_16"

    # Current Employment
    OFFER_LETTER = "offer_letter"
    APPOINTMENT_LETTER = "appointment_letter"
    NDA = "nda"
    POLICY_ACKNOWLEDGEMENT = "policy_acknowledgement"

    # Others
    OTHER = "other"


class EmployeeDocument(BaseModel):
    """
    Employee document storage model.

    WBS Reference: Task 3.3.1.1.1
    """

    __tablename__ = "employee_documents"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Document classification
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType),
        nullable=False,
    )

    # File information
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)  # bytes
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)

    # Metadata
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Upload tracking
    uploaded_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Verification
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    verified_by: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    verified_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee",
        back_populates="documents",
    )

    def __repr__(self) -> str:
        return f"<EmployeeDocument(id={self.id}, type={self.document_type}, file={self.file_name})>"
