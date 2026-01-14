"""
Employee Models - BE-005
Complete employee management with contact, identity, bank details
"""
import uuid
import enum
from datetime import datetime, date
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Enum, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class EmploymentStatus(str, enum.Enum):
    active = "active"
    on_notice = "on_notice"
    terminated = "terminated"
    resigned = "resigned"
    absconded = "absconded"


class EmploymentType(str, enum.Enum):
    full_time = "full_time"
    part_time = "part_time"
    contract = "contract"
    intern = "intern"
    consultant = "consultant"


class Employee(Base):
    """Employee master data."""
    __tablename__ = "employees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_code = Column(String(50), nullable=False)  # GCA-YYYY-XXXX
    first_name = Column(String(100), nullable=False)
    middle_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    marital_status = Column(String(20), nullable=True)
    nationality = Column(String(50), default="Indian")
    blood_group = Column(String(10), nullable=True)
    profile_photo_url = Column(String(500), nullable=True)
    department_id = Column(UUID(as_uuid=True), ForeignKey("departments.id"), nullable=True)
    designation_id = Column(UUID(as_uuid=True), ForeignKey("designations.id"), nullable=True)
    reporting_to = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    employment_status = Column(String(50), default="active")  # Changed from Enum to String for DB compatibility
    employment_type = Column(String(50), default="full_time")  # Changed from Enum to String for DB compatibility
    date_of_joining = Column(Date, nullable=False)
    date_of_leaving = Column(Date, nullable=True)
    probation_end_date = Column(Date, nullable=True)
    confirmation_date = Column(Date, nullable=True)
    notice_period_days = Column(Integer, default=30)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)
    updated_by = Column(UUID(as_uuid=True), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)  # Link to user account

    # Relationships
    department = relationship("Department", back_populates="employees")
    designation = relationship("Designation", back_populates="employees")
    manager = relationship("Employee", remote_side=[id])
    contact = relationship("EmployeeContact", back_populates="employee", uselist=False)
    identity = relationship("EmployeeIdentity", back_populates="employee", uselist=False)
    bank = relationship("EmployeeBank", back_populates="employee", uselist=False)
    salary = relationship("EmployeeSalary", back_populates="employee", uselist=False)
    documents = relationship("EmployeeDocument", back_populates="employee")

    @property
    def full_name(self) -> str:
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return " ".join(parts)


class EmployeeContact(Base):
    """Employee contact information."""
    __tablename__ = "employee_contact"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    personal_email = Column(String(255), nullable=True)
    work_email = Column(String(255), nullable=True)
    personal_phone = Column(String(20), nullable=True)
    work_phone = Column(String(20), nullable=True)
    emergency_contact_name = Column(String(100), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    emergency_contact_relation = Column(String(50), nullable=True)
    current_address_line1 = Column(String(255), nullable=True)
    current_address_line2 = Column(String(255), nullable=True)
    current_city = Column(String(100), nullable=True)
    current_state = Column(String(100), nullable=True)
    current_pincode = Column(String(10), nullable=True)
    permanent_address_line1 = Column(String(255), nullable=True)
    permanent_address_line2 = Column(String(255), nullable=True)
    permanent_city = Column(String(100), nullable=True)
    permanent_state = Column(String(100), nullable=True)
    permanent_pincode = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="contact")


class EmployeeIdentity(Base):
    """Employee identity documents."""
    __tablename__ = "employee_identity"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    pan = Column(String(20), nullable=True)
    aadhaar = Column(String(20), nullable=True)  # Stored encrypted
    passport_number = Column(String(50), nullable=True)
    passport_expiry = Column(Date, nullable=True)
    uan = Column(String(20), nullable=True)  # Universal Account Number for PF
    pf_number = Column(String(50), nullable=True)
    esi_number = Column(String(50), nullable=True)
    voter_id = Column(String(50), nullable=True)
    driving_license = Column(String(50), nullable=True)
    driving_license_expiry = Column(Date, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="identity")


class EmployeeBank(Base):
    """Employee bank account details."""
    __tablename__ = "employee_bank"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    bank_name = Column(String(100), nullable=False)
    branch_name = Column(String(100), nullable=True)
    account_number = Column(String(50), nullable=False)  # Stored encrypted
    ifsc_code = Column(String(20), nullable=False)
    account_type = Column(String(20), default="savings")
    is_primary = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", back_populates="bank")


# EmployeeDocument moved to document.py to avoid duplication
# Use app.models.document.EmployeeDocument instead
