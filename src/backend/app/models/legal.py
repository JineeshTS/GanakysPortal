"""
Legal Case Management Models
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from uuid import UUID
from sqlalchemy import (
    String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, Numeric, Enum as SQLEnum, ARRAY, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
import enum

from app.models.base import Base


class CaseType(str, enum.Enum):
    """Types of legal cases"""
    civil = "civil"
    criminal = "criminal"
    labor = "labor"
    tax = "tax"
    intellectual_property = "intellectual_property"
    contract = "contract"
    arbitration = "arbitration"
    consumer = "consumer"
    environmental = "environmental"
    regulatory = "regulatory"
    corporate = "corporate"
    real_estate = "real_estate"
    employment = "employment"
    compliance = "compliance"
    other = "other"


class CaseStatus(str, enum.Enum):
    """Status of legal case"""
    draft = "draft"
    filed = "filed"
    pending = "pending"
    in_progress = "in_progress"
    hearing_scheduled = "hearing_scheduled"
    under_review = "under_review"
    awaiting_judgment = "awaiting_judgment"
    judgment_received = "judgment_received"
    appeal_filed = "appeal_filed"
    settled = "settled"
    closed = "closed"
    dismissed = "dismissed"
    withdrawn = "withdrawn"


class CasePriority(str, enum.Enum):
    """Priority of legal case"""
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class PartyRole(str, enum.Enum):
    """Role of party in case"""
    plaintiff = "plaintiff"
    defendant = "defendant"
    petitioner = "petitioner"
    respondent = "respondent"
    appellant = "appellant"
    appellee = "appellee"
    complainant = "complainant"
    accused = "accused"
    witness = "witness"
    third_party = "third_party"


class CourtLevel(str, enum.Enum):
    """Level of court"""
    district_court = "district_court"
    sessions_court = "sessions_court"
    high_court = "high_court"
    supreme_court = "supreme_court"
    tribunal = "tribunal"
    consumer_forum = "consumer_forum"
    labor_court = "labor_court"
    arbitration_center = "arbitration_center"
    nclt = "nclt"  # National Company Law Tribunal
    nclat = "nclat"  # National Company Law Appellate Tribunal
    itat = "itat"  # Income Tax Appellate Tribunal
    cestat = "cestat"  # Customs Excise Service Tax Appellate Tribunal
    other = "other"


class HearingType(str, enum.Enum):
    """Type of hearing"""
    first_hearing = "first_hearing"
    regular_hearing = "regular_hearing"
    arguments = "arguments"
    evidence = "evidence"
    cross_examination = "cross_examination"
    final_hearing = "final_hearing"
    judgment = "judgment"
    interim_order = "interim_order"
    stay_application = "stay_application"
    miscellaneous = "miscellaneous"


class HearingStatus(str, enum.Enum):
    """Status of hearing"""
    scheduled = "scheduled"
    completed = "completed"
    adjourned = "adjourned"
    cancelled = "cancelled"
    reserved = "reserved"


class DocumentCategory(str, enum.Enum):
    """Category of legal document"""
    petition = "petition"
    complaint = "complaint"
    written_statement = "written_statement"
    affidavit = "affidavit"
    evidence = "evidence"
    order = "order"
    judgment = "judgment"
    notice = "notice"
    agreement = "agreement"
    contract = "contract"
    correspondence = "correspondence"
    memo = "memo"
    opinion = "opinion"
    other = "other"


class TaskStatus(str, enum.Enum):
    """Status of legal task"""
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    cancelled = "cancelled"


class LegalCase(Base):
    """Legal case/matter model"""
    __tablename__ = "legal_cases"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Case identification
    case_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    case_title: Mapped[str] = mapped_column(String(500))
    case_type: Mapped[CaseType] = mapped_column(SQLEnum(CaseType))
    status: Mapped[CaseStatus] = mapped_column(SQLEnum(CaseStatus), default=CaseStatus.draft)
    priority: Mapped[CasePriority] = mapped_column(SQLEnum(CasePriority), default=CasePriority.medium)

    # Court details
    court_level: Mapped[Optional[CourtLevel]] = mapped_column(SQLEnum(CourtLevel), nullable=True)
    court_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    court_location: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    court_case_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    bench: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Case details
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    our_role: Mapped[PartyRole] = mapped_column(SQLEnum(PartyRole))
    opposing_party: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    subject_matter: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relief_sought: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    filing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    first_hearing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_hearing_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    judgment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    closure_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    limitation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Financial
    claim_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    counter_claim_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    settlement_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    legal_fees_estimated: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    legal_fees_actual: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    court_fees: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)

    # Assignment
    internal_counsel_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    external_counsel_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_counsels.id"), nullable=True)
    department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Risk assessment
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    probability_of_success: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    potential_liability: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Outcome
    outcome: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    outcome_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    judgment_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    appeal_deadline: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_appealed: Mapped[bool] = mapped_column(Boolean, default=False)
    parent_case_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), nullable=True)

    # Related entities
    related_contract_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    related_project_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    related_employee_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Tags and notes
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    hearings: Mapped[List["LegalHearing"]] = relationship("LegalHearing", back_populates="case")
    documents: Mapped[List["LegalDocument"]] = relationship("LegalDocument", back_populates="case")
    tasks: Mapped[List["LegalTask"]] = relationship("LegalTask", back_populates="case")
    parties: Mapped[List["LegalParty"]] = relationship("LegalParty", back_populates="case")
    expenses: Mapped[List["LegalExpense"]] = relationship("LegalExpense", back_populates="case")
    external_counsel: Mapped[Optional["LegalCounsel"]] = relationship("LegalCounsel", back_populates="cases")


class LegalCounsel(Base):
    """External legal counsel/law firm"""
    __tablename__ = "legal_counsels"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Counsel details
    counsel_code: Mapped[str] = mapped_column(String(20), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    firm_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    counsel_type: Mapped[str] = mapped_column(String(50))  # individual, firm

    # Specialization
    specialization: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    bar_council_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    enrollment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    practicing_courts: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Contact
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    mobile: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Billing
    hourly_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    retainer_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    billing_frequency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    payment_terms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    gst_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    pan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    bank_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Rating
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    performance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_empanelled: Mapped[bool] = mapped_column(Boolean, default=False)
    empanelment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    empanelment_expiry: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    cases: Mapped[List["LegalCase"]] = relationship("LegalCase", back_populates="external_counsel")


class LegalHearing(Base):
    """Court hearing/appearance"""
    __tablename__ = "legal_hearings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), index=True)

    # Hearing details
    hearing_number: Mapped[int] = mapped_column(Integer)
    hearing_type: Mapped[HearingType] = mapped_column(SQLEnum(HearingType))
    status: Mapped[HearingStatus] = mapped_column(SQLEnum(HearingStatus), default=HearingStatus.scheduled)

    # Schedule
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    scheduled_time: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    actual_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Location
    court_room: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    bench: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Purpose and outcome
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    proceedings_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    order_passed: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    next_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_purpose: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Attendance
    counsel_attended: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    internal_attendee_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    attendance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documents
    documents_filed: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)
    documents_received: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Adjournment
    adjournment_reason: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    adjournment_requested_by: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    case: Mapped["LegalCase"] = relationship("LegalCase", back_populates="hearings")


class LegalDocument(Base):
    """Legal case documents"""
    __tablename__ = "legal_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), index=True)

    # Document details
    document_number: Mapped[str] = mapped_column(String(50))
    title: Mapped[str] = mapped_column(String(300))
    category: Mapped[DocumentCategory] = mapped_column(SQLEnum(DocumentCategory))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # File details
    file_name: Mapped[str] = mapped_column(String(300))
    file_path: Mapped[str] = mapped_column(String(500))
    file_type: Mapped[str] = mapped_column(String(50))
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1)
    parent_document_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Filing details
    filed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    filed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    received_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    received_from: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Status
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False)
    is_original: Mapped[bool] = mapped_column(Boolean, default=False)
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Related hearing
    hearing_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_hearings.id"), nullable=True)

    # Tags
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Audit
    uploaded_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    case: Mapped["LegalCase"] = relationship("LegalCase", back_populates="documents")


class LegalParty(Base):
    """Parties involved in legal case"""
    __tablename__ = "legal_parties"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), index=True)

    # Party details
    party_name: Mapped[str] = mapped_column(String(300))
    party_type: Mapped[str] = mapped_column(String(50))  # individual, company, government
    role: Mapped[PartyRole] = mapped_column(SQLEnum(PartyRole))

    # Contact details
    contact_person: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Legal representation
    counsel_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    counsel_firm: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    counsel_contact: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Identification
    pan_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    cin_number: Mapped[Optional[str]] = mapped_column(String(30), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    case: Mapped["LegalCase"] = relationship("LegalCase", back_populates="parties")


class LegalTask(Base):
    """Tasks related to legal case"""
    __tablename__ = "legal_tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), index=True)

    # Task details
    task_number: Mapped[str] = mapped_column(String(20))
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50))  # filing, review, drafting, research, meeting
    status: Mapped[TaskStatus] = mapped_column(SQLEnum(TaskStatus), default=TaskStatus.pending)
    priority: Mapped[CasePriority] = mapped_column(SQLEnum(CasePriority), default=CasePriority.medium)

    # Schedule
    due_date: Mapped[date] = mapped_column(Date, index=True)
    reminder_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Assignment
    assigned_to: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    assigned_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))

    # Related hearing
    hearing_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_hearings.id"), nullable=True)

    # Notes
    completion_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    case: Mapped["LegalCase"] = relationship("LegalCase", back_populates="tasks")


class LegalExpense(Base):
    """Legal case expenses"""
    __tablename__ = "legal_expenses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)
    case_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), index=True)

    # Expense details
    expense_number: Mapped[str] = mapped_column(String(20))
    expense_type: Mapped[str] = mapped_column(String(50))  # counsel_fee, court_fee, filing_fee, travel, other
    description: Mapped[str] = mapped_column(String(300))

    # Amount
    amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    gst_amount: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2))

    # Payment
    expense_date: Mapped[date] = mapped_column(Date)
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")  # pending, approved, paid, rejected
    payment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    payment_reference: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Vendor/Counsel
    payee_name: Mapped[str] = mapped_column(String(200))
    payee_type: Mapped[str] = mapped_column(String(50))  # counsel, court, vendor
    counsel_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_counsels.id"), nullable=True)

    # Invoice
    invoice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Approval
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    approved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Related hearing
    hearing_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_hearings.id"), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    case: Mapped["LegalCase"] = relationship("LegalCase", back_populates="expenses")


class LegalContract(Base):
    """Legal contracts and agreements"""
    __tablename__ = "legal_contracts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Contract identification
    contract_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(300))
    contract_type: Mapped[str] = mapped_column(String(50))  # service, supply, employment, nda, lease, license
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, review, approved, active, expired, terminated

    # Parties
    party_name: Mapped[str] = mapped_column(String(300))
    party_type: Mapped[str] = mapped_column(String(50))  # vendor, customer, employee, partner
    party_contact: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    party_email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Contract terms
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scope_of_work: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    key_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    effective_date: Mapped[date] = mapped_column(Date)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renewal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    termination_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    notice_period_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Financial
    contract_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(18, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    payment_terms: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Auto-renewal
    is_auto_renewal: Mapped[bool] = mapped_column(Boolean, default=False)
    renewal_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documents
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    signed_copy_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Assignment
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    department_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    reviewer_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Approval
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    approved_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Risk
    risk_level: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    risk_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Tags
    tags: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String), nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)


class LegalNotice(Base):
    """Legal notices sent/received"""
    __tablename__ = "legal_notices"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True)
    company_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("companies.id"), index=True)

    # Notice identification
    notice_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    notice_type: Mapped[str] = mapped_column(String(50))  # legal_notice, show_cause, demand, reply, cease_desist
    direction: Mapped[str] = mapped_column(String(10))  # sent, received
    status: Mapped[str] = mapped_column(String(20), default="draft")  # draft, sent, delivered, replied, closed

    # Parties
    from_party: Mapped[str] = mapped_column(String(300))
    to_party: Mapped[str] = mapped_column(String(300))
    through_counsel: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Details
    subject: Mapped[str] = mapped_column(String(500))
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    relief_demanded: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Dates
    notice_date: Mapped[date] = mapped_column(Date)
    received_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    response_due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    response_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Delivery
    delivery_mode: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # courier, rpad, email, hand
    tracking_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    delivery_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    delivery_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Related case
    case_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_cases.id"), nullable=True)
    led_to_case: Mapped[bool] = mapped_column(Boolean, default=False)

    # Documents
    document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    reply_document_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Assignment
    handled_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    counsel_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("legal_counsels.id"), nullable=True)

    # Notes
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Audit
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
