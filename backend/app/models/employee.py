"""
Employee models with all related tables.
WBS Reference: Tasks 3.2.1.1.1 - 3.2.1.1.5
"""
import enum
from datetime import date
from typing import TYPE_CHECKING, Optional, List
import uuid

from sqlalchemy import (
    Boolean,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    DateTime,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.types import EncryptedString
from app.models.base import BaseModel

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.department import Department, Designation
    from app.models.employee_document import EmployeeDocument


class Gender(str, enum.Enum):
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class BloodGroup(str, enum.Enum):
    A_POSITIVE = "A+"
    A_NEGATIVE = "A-"
    B_POSITIVE = "B+"
    B_NEGATIVE = "B-"
    AB_POSITIVE = "AB+"
    AB_NEGATIVE = "AB-"
    O_POSITIVE = "O+"
    O_NEGATIVE = "O-"


class MaritalStatus(str, enum.Enum):
    SINGLE = "single"
    MARRIED = "married"
    DIVORCED = "divorced"
    WIDOWED = "widowed"


class OnboardingStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    APPROVED = "approved"


class EmploymentType(str, enum.Enum):
    FULL_TIME = "full_time"
    PART_TIME = "part_time"
    CONTRACT = "contract"
    INTERN = "intern"
    CONSULTANT = "consultant"


class EmploymentStatus(str, enum.Enum):
    ACTIVE = "active"
    ON_NOTICE = "on_notice"
    RELIEVED = "relieved"
    TERMINATED = "terminated"
    ABSCONDING = "absconding"


class Employee(BaseModel):
    """
    Employee master data model.

    WBS Reference: Task 3.2.1.1.1
    """

    __tablename__ = "employees"

    # Link to user
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Employee code (auto-generated: GCA-YYYY-XXXX)
    employee_code: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )

    # Personal information
    first_name: Mapped[str] = mapped_column(String(100), nullable=False)
    middle_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    last_name: Mapped[str] = mapped_column(String(100), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gender: Mapped[Optional[Gender]] = mapped_column(Enum(Gender), nullable=True)
    blood_group: Mapped[Optional[BloodGroup]] = mapped_column(
        Enum(BloodGroup), nullable=True
    )
    marital_status: Mapped[Optional[MaritalStatus]] = mapped_column(
        Enum(MaritalStatus), nullable=True
    )
    nationality: Mapped[str] = mapped_column(
        String(50), default="Indian", nullable=False
    )
    profile_photo_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Onboarding
    onboarding_status: Mapped[OnboardingStatus] = mapped_column(
        Enum(OnboardingStatus),
        default=OnboardingStatus.PENDING,
        nullable=False,
    )
    onboarding_completed_at: Mapped[Optional[date]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="employee")
    contact: Mapped[Optional["EmployeeContact"]] = relationship(
        "EmployeeContact",
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )
    identity: Mapped[Optional["EmployeeIdentity"]] = relationship(
        "EmployeeIdentity",
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )
    bank_accounts: Mapped[List["EmployeeBank"]] = relationship(
        "EmployeeBank",
        back_populates="employee",
        cascade="all, delete-orphan",
    )
    employment: Mapped[Optional["EmployeeEmployment"]] = relationship(
        "EmployeeEmployment",
        back_populates="employee",
        uselist=False,
        cascade="all, delete-orphan",
    )
    documents: Mapped[List["EmployeeDocument"]] = relationship(
        "EmployeeDocument",
        back_populates="employee",
        cascade="all, delete-orphan",
    )

    @property
    def full_name(self) -> str:
        """Get full name of employee."""
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)

    def __repr__(self) -> str:
        return f"<Employee(id={self.id}, code={self.employee_code}, name={self.full_name})>"


class EmployeeContact(BaseModel):
    """
    Employee contact information.

    WBS Reference: Task 3.2.1.1.2
    """

    __tablename__ = "employee_contacts"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Contact details
    personal_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    personal_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Emergency contact
    emergency_contact_name: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    emergency_contact_phone: Mapped[Optional[str]] = mapped_column(
        String(20), nullable=True
    )
    emergency_contact_relation: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )

    # Address - Current
    current_address_line1: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    current_address_line2: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    current_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    current_pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    current_country: Mapped[str] = mapped_column(
        String(100), default="India", nullable=False
    )

    # Address - Permanent
    is_permanent_same_as_current: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )
    permanent_address_line1: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    permanent_address_line2: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    permanent_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permanent_state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    permanent_pincode: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    permanent_country: Mapped[str] = mapped_column(
        String(100), default="India", nullable=False
    )

    # Relationship
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="contact"
    )


class EmployeeIdentity(BaseModel):
    """
    Employee identity documents (encrypted sensitive data).

    WBS Reference: Task 3.2.1.1.3
    """

    __tablename__ = "employee_identities"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Identity documents (stored encrypted)
    pan_number: Mapped[Optional[str]] = mapped_column(
        EncryptedString(500), nullable=True
    )
    aadhaar_number: Mapped[Optional[str]] = mapped_column(
        EncryptedString(500), nullable=True
    )
    passport_number: Mapped[Optional[str]] = mapped_column(
        EncryptedString(500), nullable=True
    )
    passport_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    driving_license: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    voter_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # UAN for PF
    uan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    # ESI number
    esi_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Relationship
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="identity"
    )


class EmployeeBank(BaseModel):
    """
    Employee bank account details (encrypted sensitive data).

    WBS Reference: Task 3.2.1.1.4
    """

    __tablename__ = "employee_bank_accounts"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Bank details
    bank_name: Mapped[str] = mapped_column(String(100), nullable=False)
    branch_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    account_number: Mapped[str] = mapped_column(
        EncryptedString(500), nullable=False
    )
    ifsc_code: Mapped[str] = mapped_column(String(20), nullable=False)
    account_type: Mapped[str] = mapped_column(
        String(20), default="savings", nullable=False
    )
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationship
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="bank_accounts"
    )


class EmployeeEmployment(BaseModel):
    """
    Employee employment details.

    WBS Reference: Task 3.2.1.1.5
    """

    __tablename__ = "employee_employments"

    employee_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # Department and designation
    department_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
    )
    designation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("designations.id", ondelete="SET NULL"),
        nullable=True,
    )
    reporting_manager_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Employment details
    employment_type: Mapped[EmploymentType] = mapped_column(
        Enum(EmploymentType),
        default=EmploymentType.FULL_TIME,
        nullable=False,
    )
    date_of_joining: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    probation_end_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    confirmation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Exit details
    date_of_exit: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    exit_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notice_period_days: Mapped[int] = mapped_column(Integer, default=30, nullable=False)

    # Current status
    current_status: Mapped[EmploymentStatus] = mapped_column(
        Enum(EmploymentStatus),
        default=EmploymentStatus.ACTIVE,
        nullable=False,
    )

    # Work location
    work_location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    employee: Mapped["Employee"] = relationship(
        "Employee", back_populates="employment"
    )
    department: Mapped[Optional["Department"]] = relationship(
        "Department", back_populates="employees"
    )
    designation: Mapped[Optional["Designation"]] = relationship(
        "Designation", back_populates="employees"
    )
