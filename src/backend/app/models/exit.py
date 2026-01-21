"""
Exit Management Models - Employee offboarding, clearance, and final settlement
Integrates with Employee to update employment status
"""
import uuid
import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import Column, String, Boolean, DateTime, Date, Integer, ForeignKey, Text, Numeric
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.session import Base


class ExitType(str, enum.Enum):
    resignation = "resignation"
    termination = "termination"
    retirement = "retirement"
    end_of_contract = "end_of_contract"
    mutual_separation = "mutual_separation"
    absconding = "absconding"
    death = "death"


class ExitStatus(str, enum.Enum):
    initiated = "initiated"
    clearance_pending = "clearance_pending"
    clearance_completed = "clearance_completed"
    fnf_pending = "fnf_pending"
    fnf_processed = "fnf_processed"
    completed = "completed"
    cancelled = "cancelled"


class ClearanceStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    cleared = "cleared"
    not_applicable = "not_applicable"


class ExitCase(Base):
    """Exit/separation case for an employee."""
    __tablename__ = "exit_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    employee_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=False)
    exit_type = Column(String(50), default="resignation")
    resignation_date = Column(Date, nullable=True)  # Date resignation submitted
    last_working_day = Column(Date, nullable=True)  # LWD
    requested_lwd = Column(Date, nullable=True)  # LWD requested by employee
    approved_lwd = Column(Date, nullable=True)  # LWD approved by manager
    reason = Column(Text, nullable=True)  # Reason for leaving
    reason_category = Column(String(100), nullable=True)  # Better offer, personal, relocation, etc.
    status = Column(String(50), default="initiated")
    notice_period_days = Column(Integer, nullable=True)  # Employee's notice period
    notice_served_days = Column(Integer, default=0)  # Days actually served
    notice_buyout_days = Column(Integer, default=0)  # Days bought out
    notice_recovery_amount = Column(Numeric(15, 2), default=0)  # Amount to recover
    rehire_eligible = Column(Boolean, default=True)
    rehire_notes = Column(Text, nullable=True)
    exit_interview_date = Column(DateTime(timezone=True), nullable=True)
    exit_interview_conducted_by = Column(UUID(as_uuid=True), nullable=True)
    exit_interview_notes = Column(Text, nullable=True)
    manager_id = Column(UUID(as_uuid=True), ForeignKey("employees.id"), nullable=True)
    hr_owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    initiated_by = Column(UUID(as_uuid=True), nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_date = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    employee = relationship("Employee", foreign_keys=[employee_id], backref="exit_cases")
    manager = relationship("Employee", foreign_keys=[manager_id])
    clearance_tasks = relationship("ClearanceTask", back_populates="exit_case", cascade="all, delete-orphan")
    final_settlement = relationship("FinalSettlement", back_populates="exit_case", uselist=False)


class ClearanceTask(Base):
    """Clearance task for exit process - one per department/area."""
    __tablename__ = "clearance_tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exit_case_id = Column(UUID(as_uuid=True), ForeignKey("exit_cases.id"), nullable=False)
    department = Column(String(100), nullable=False)  # IT, HR, Finance, Admin, etc.
    task_name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_role = Column(String(100), nullable=True)  # IT Admin, HR, Finance, etc.
    status = Column(String(50), default="pending")
    due_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)
    completed_by = Column(UUID(as_uuid=True), nullable=True)
    recovery_amount = Column(Numeric(15, 2), default=0)  # Amount to recover (e.g., laptop damage)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exit_case = relationship("ExitCase", back_populates="clearance_tasks")


class FinalSettlement(Base):
    """Final & Full (F&F) settlement calculation."""
    __tablename__ = "final_settlements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exit_case_id = Column(UUID(as_uuid=True), ForeignKey("exit_cases.id"), nullable=False, unique=True)

    # Earnings
    basic_salary_dues = Column(Numeric(15, 2), default=0)
    leave_encashment = Column(Numeric(15, 2), default=0)
    bonus_dues = Column(Numeric(15, 2), default=0)
    gratuity = Column(Numeric(15, 2), default=0)
    reimbursements = Column(Numeric(15, 2), default=0)
    other_earnings = Column(Numeric(15, 2), default=0)
    total_earnings = Column(Numeric(15, 2), default=0)

    # Deductions
    notice_recovery = Column(Numeric(15, 2), default=0)
    asset_recovery = Column(Numeric(15, 2), default=0)
    loan_recovery = Column(Numeric(15, 2), default=0)
    advance_recovery = Column(Numeric(15, 2), default=0)
    tds = Column(Numeric(15, 2), default=0)
    pf_employee = Column(Numeric(15, 2), default=0)
    other_deductions = Column(Numeric(15, 2), default=0)
    total_deductions = Column(Numeric(15, 2), default=0)

    # Net
    net_payable = Column(Numeric(15, 2), default=0)

    # Status
    status = Column(String(50), default="draft")  # draft, pending_approval, approved, processed, paid
    calculation_date = Column(Date, nullable=True)
    approved_by = Column(UUID(as_uuid=True), nullable=True)
    approved_date = Column(DateTime(timezone=True), nullable=True)
    processed_date = Column(DateTime(timezone=True), nullable=True)
    payment_date = Column(Date, nullable=True)
    payment_reference = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    exit_case = relationship("ExitCase", back_populates="final_settlement")
