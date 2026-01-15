"""
Legal Case Management Schemas
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field
from enum import Enum


class CaseType(str, Enum):
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


class CaseStatus(str, Enum):
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


class CasePriority(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class PartyRole(str, Enum):
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


class CourtLevel(str, Enum):
    district_court = "district_court"
    sessions_court = "sessions_court"
    high_court = "high_court"
    supreme_court = "supreme_court"
    tribunal = "tribunal"
    consumer_forum = "consumer_forum"
    labor_court = "labor_court"
    arbitration_center = "arbitration_center"
    nclt = "nclt"
    nclat = "nclat"
    itat = "itat"
    cestat = "cestat"
    other = "other"


class HearingType(str, Enum):
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


class HearingStatus(str, Enum):
    scheduled = "scheduled"
    completed = "completed"
    adjourned = "adjourned"
    cancelled = "cancelled"
    reserved = "reserved"


class DocumentCategory(str, Enum):
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


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    overdue = "overdue"
    cancelled = "cancelled"


# Legal Counsel Schemas
class LegalCounselBase(BaseModel):
    name: str
    firm_name: Optional[str] = None
    counsel_type: str
    specialization: Optional[List[str]] = None
    bar_council_number: Optional[str] = None
    enrollment_date: Optional[date] = None
    practicing_courts: Optional[List[str]] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    retainer_amount: Optional[Decimal] = None
    billing_frequency: Optional[str] = None
    payment_terms: Optional[int] = None
    gst_number: Optional[str] = None
    pan_number: Optional[str] = None
    bank_details: Optional[Dict[str, Any]] = None


class LegalCounselCreate(LegalCounselBase):
    pass


class LegalCounselUpdate(BaseModel):
    name: Optional[str] = None
    firm_name: Optional[str] = None
    counsel_type: Optional[str] = None
    specialization: Optional[List[str]] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    mobile: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    hourly_rate: Optional[Decimal] = None
    retainer_amount: Optional[Decimal] = None
    is_active: Optional[bool] = None
    is_empanelled: Optional[bool] = None
    empanelment_date: Optional[date] = None
    empanelment_expiry: Optional[date] = None
    rating: Optional[int] = None
    performance_notes: Optional[str] = None


class LegalCounselInDB(LegalCounselBase):
    id: UUID
    company_id: UUID
    counsel_code: str
    is_active: bool
    is_empanelled: bool
    rating: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LegalCounselList(BaseModel):
    items: List[LegalCounselInDB]
    total: int
    page: int
    size: int


# Legal Case Schemas
class LegalCaseBase(BaseModel):
    case_title: str
    case_type: CaseType
    our_role: PartyRole
    priority: Optional[CasePriority] = CasePriority.medium
    court_level: Optional[CourtLevel] = None
    court_name: Optional[str] = None
    court_location: Optional[str] = None
    court_case_number: Optional[str] = None
    bench: Optional[str] = None
    description: Optional[str] = None
    opposing_party: Optional[str] = None
    subject_matter: Optional[str] = None
    relief_sought: Optional[str] = None
    filing_date: Optional[date] = None
    limitation_date: Optional[date] = None
    claim_amount: Optional[Decimal] = None
    counter_claim_amount: Optional[Decimal] = None
    legal_fees_estimated: Optional[Decimal] = None
    external_counsel_id: Optional[UUID] = None
    internal_counsel_id: Optional[UUID] = None
    department_id: Optional[UUID] = None
    risk_level: Optional[str] = None
    probability_of_success: Optional[int] = None
    potential_liability: Optional[Decimal] = None
    risk_notes: Optional[str] = None
    related_contract_id: Optional[UUID] = None
    related_project_id: Optional[UUID] = None
    related_employee_id: Optional[UUID] = None
    tags: Optional[List[str]] = None
    internal_notes: Optional[str] = None


class LegalCaseCreate(LegalCaseBase):
    pass


class LegalCaseUpdate(BaseModel):
    case_title: Optional[str] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    priority: Optional[CasePriority] = None
    court_level: Optional[CourtLevel] = None
    court_name: Optional[str] = None
    court_location: Optional[str] = None
    court_case_number: Optional[str] = None
    bench: Optional[str] = None
    description: Optional[str] = None
    our_role: Optional[PartyRole] = None
    opposing_party: Optional[str] = None
    subject_matter: Optional[str] = None
    relief_sought: Optional[str] = None
    filing_date: Optional[date] = None
    first_hearing_date: Optional[date] = None
    next_hearing_date: Optional[date] = None
    judgment_date: Optional[date] = None
    closure_date: Optional[date] = None
    claim_amount: Optional[Decimal] = None
    counter_claim_amount: Optional[Decimal] = None
    settlement_amount: Optional[Decimal] = None
    legal_fees_estimated: Optional[Decimal] = None
    legal_fees_actual: Optional[Decimal] = None
    court_fees: Optional[Decimal] = None
    external_counsel_id: Optional[UUID] = None
    internal_counsel_id: Optional[UUID] = None
    risk_level: Optional[str] = None
    probability_of_success: Optional[int] = None
    potential_liability: Optional[Decimal] = None
    risk_notes: Optional[str] = None
    outcome: Optional[str] = None
    outcome_summary: Optional[str] = None
    judgment_summary: Optional[str] = None
    appeal_deadline: Optional[date] = None
    is_appealed: Optional[bool] = None
    tags: Optional[List[str]] = None
    internal_notes: Optional[str] = None


class LegalCaseInDB(LegalCaseBase):
    id: UUID
    company_id: UUID
    case_number: str
    status: CaseStatus
    first_hearing_date: Optional[date] = None
    next_hearing_date: Optional[date] = None
    judgment_date: Optional[date] = None
    closure_date: Optional[date] = None
    settlement_amount: Optional[Decimal] = None
    legal_fees_actual: Optional[Decimal] = None
    court_fees: Optional[Decimal] = None
    outcome: Optional[str] = None
    outcome_summary: Optional[str] = None
    judgment_summary: Optional[str] = None
    appeal_deadline: Optional[date] = None
    is_appealed: bool
    parent_case_id: Optional[UUID] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LegalCaseList(BaseModel):
    items: List[LegalCaseInDB]
    total: int
    page: int
    size: int


# Legal Hearing Schemas
class LegalHearingBase(BaseModel):
    hearing_type: HearingType
    scheduled_date: date
    scheduled_time: Optional[str] = None
    court_room: Optional[str] = None
    bench: Optional[str] = None
    purpose: Optional[str] = None


class LegalHearingCreate(LegalHearingBase):
    case_id: UUID


class LegalHearingUpdate(BaseModel):
    hearing_type: Optional[HearingType] = None
    status: Optional[HearingStatus] = None
    scheduled_date: Optional[date] = None
    scheduled_time: Optional[str] = None
    actual_date: Optional[date] = None
    court_room: Optional[str] = None
    bench: Optional[str] = None
    purpose: Optional[str] = None
    proceedings_summary: Optional[str] = None
    order_passed: Optional[str] = None
    next_date: Optional[date] = None
    next_purpose: Optional[str] = None
    counsel_attended: Optional[UUID] = None
    internal_attendee_id: Optional[UUID] = None
    attendance_notes: Optional[str] = None
    documents_filed: Optional[List[str]] = None
    documents_received: Optional[List[str]] = None
    adjournment_reason: Optional[str] = None
    adjournment_requested_by: Optional[str] = None


class LegalHearingInDB(LegalHearingBase):
    id: UUID
    company_id: UUID
    case_id: UUID
    hearing_number: int
    status: HearingStatus
    actual_date: Optional[date] = None
    proceedings_summary: Optional[str] = None
    order_passed: Optional[str] = None
    next_date: Optional[date] = None
    next_purpose: Optional[str] = None
    counsel_attended: Optional[UUID] = None
    adjournment_reason: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LegalHearingList(BaseModel):
    items: List[LegalHearingInDB]
    total: int
    page: int
    size: int


# Legal Document Schemas
class LegalDocumentBase(BaseModel):
    title: str
    category: DocumentCategory
    description: Optional[str] = None
    file_name: str
    file_path: str
    file_type: str
    file_size: Optional[int] = None
    filed_date: Optional[date] = None
    filed_by: Optional[str] = None
    received_date: Optional[date] = None
    received_from: Optional[str] = None
    is_confidential: Optional[bool] = False
    is_original: Optional[bool] = False
    is_certified: Optional[bool] = False
    hearing_id: Optional[UUID] = None
    tags: Optional[List[str]] = None


class LegalDocumentCreate(LegalDocumentBase):
    case_id: UUID


class LegalDocumentUpdate(BaseModel):
    title: Optional[str] = None
    category: Optional[DocumentCategory] = None
    description: Optional[str] = None
    filed_date: Optional[date] = None
    filed_by: Optional[str] = None
    is_confidential: Optional[bool] = None
    is_original: Optional[bool] = None
    is_certified: Optional[bool] = None
    tags: Optional[List[str]] = None


class LegalDocumentInDB(LegalDocumentBase):
    id: UUID
    company_id: UUID
    case_id: UUID
    document_number: str
    version: int
    uploaded_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LegalDocumentList(BaseModel):
    items: List[LegalDocumentInDB]
    total: int
    page: int
    size: int


# Legal Party Schemas
class LegalPartyBase(BaseModel):
    party_name: str
    party_type: str
    role: PartyRole
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    counsel_name: Optional[str] = None
    counsel_firm: Optional[str] = None
    counsel_contact: Optional[str] = None
    pan_number: Optional[str] = None
    cin_number: Optional[str] = None
    notes: Optional[str] = None


class LegalPartyCreate(LegalPartyBase):
    case_id: UUID


class LegalPartyUpdate(BaseModel):
    party_name: Optional[str] = None
    party_type: Optional[str] = None
    role: Optional[PartyRole] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    counsel_name: Optional[str] = None
    counsel_firm: Optional[str] = None
    counsel_contact: Optional[str] = None
    notes: Optional[str] = None


class LegalPartyInDB(LegalPartyBase):
    id: UUID
    company_id: UUID
    case_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Legal Task Schemas
class LegalTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    task_type: str
    priority: Optional[CasePriority] = CasePriority.medium
    due_date: date
    reminder_date: Optional[date] = None
    assigned_to: UUID
    hearing_id: Optional[UUID] = None


class LegalTaskCreate(LegalTaskBase):
    case_id: UUID


class LegalTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    task_type: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[CasePriority] = None
    due_date: Optional[date] = None
    reminder_date: Optional[date] = None
    completed_date: Optional[date] = None
    assigned_to: Optional[UUID] = None
    completion_notes: Optional[str] = None


class LegalTaskInDB(LegalTaskBase):
    id: UUID
    company_id: UUID
    case_id: UUID
    task_number: str
    status: TaskStatus
    completed_date: Optional[date] = None
    assigned_by: UUID
    completion_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class LegalTaskList(BaseModel):
    items: List[LegalTaskInDB]
    total: int
    page: int
    size: int


# Legal Expense Schemas
class LegalExpenseBase(BaseModel):
    expense_type: str
    description: str
    amount: Decimal
    currency: Optional[str] = "INR"
    gst_amount: Optional[Decimal] = None
    expense_date: date
    payee_name: str
    payee_type: str
    counsel_id: Optional[UUID] = None
    invoice_number: Optional[str] = None
    invoice_date: Optional[date] = None
    hearing_id: Optional[UUID] = None
    notes: Optional[str] = None


class LegalExpenseCreate(LegalExpenseBase):
    case_id: UUID


class LegalExpenseUpdate(BaseModel):
    expense_type: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    gst_amount: Optional[Decimal] = None
    expense_date: Optional[date] = None
    payment_status: Optional[str] = None
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    notes: Optional[str] = None


class LegalExpenseInDB(LegalExpenseBase):
    id: UUID
    company_id: UUID
    case_id: UUID
    expense_number: str
    total_amount: Decimal
    payment_status: str
    payment_date: Optional[date] = None
    payment_reference: Optional[str] = None
    approved_by: Optional[UUID] = None
    approved_date: Optional[date] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LegalExpenseList(BaseModel):
    items: List[LegalExpenseInDB]
    total: int
    page: int
    size: int


# Legal Contract Schemas
class LegalContractBase(BaseModel):
    title: str
    contract_type: str
    party_name: str
    party_type: str
    party_contact: Optional[str] = None
    party_email: Optional[str] = None
    description: Optional[str] = None
    scope_of_work: Optional[str] = None
    key_terms: Optional[str] = None
    effective_date: date
    expiry_date: Optional[date] = None
    notice_period_days: Optional[int] = None
    contract_value: Optional[Decimal] = None
    currency: Optional[str] = "INR"
    payment_terms: Optional[str] = None
    is_auto_renewal: Optional[bool] = False
    renewal_terms: Optional[str] = None
    document_path: Optional[str] = None
    department_id: Optional[UUID] = None
    reviewer_id: Optional[UUID] = None
    risk_level: Optional[str] = None
    risk_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LegalContractCreate(LegalContractBase):
    pass


class LegalContractUpdate(BaseModel):
    title: Optional[str] = None
    contract_type: Optional[str] = None
    status: Optional[str] = None
    party_name: Optional[str] = None
    party_type: Optional[str] = None
    party_contact: Optional[str] = None
    party_email: Optional[str] = None
    description: Optional[str] = None
    scope_of_work: Optional[str] = None
    key_terms: Optional[str] = None
    effective_date: Optional[date] = None
    expiry_date: Optional[date] = None
    renewal_date: Optional[date] = None
    termination_date: Optional[date] = None
    notice_period_days: Optional[int] = None
    contract_value: Optional[Decimal] = None
    payment_terms: Optional[str] = None
    is_auto_renewal: Optional[bool] = None
    renewal_terms: Optional[str] = None
    document_path: Optional[str] = None
    signed_copy_path: Optional[str] = None
    risk_level: Optional[str] = None
    risk_notes: Optional[str] = None
    tags: Optional[List[str]] = None


class LegalContractInDB(LegalContractBase):
    id: UUID
    company_id: UUID
    contract_number: str
    status: str
    renewal_date: Optional[date] = None
    termination_date: Optional[date] = None
    signed_copy_path: Optional[str] = None
    owner_id: UUID
    approved_by: Optional[UUID] = None
    approved_date: Optional[date] = None
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LegalContractList(BaseModel):
    items: List[LegalContractInDB]
    total: int
    page: int
    size: int


# Legal Notice Schemas
class LegalNoticeBase(BaseModel):
    notice_type: str
    direction: str
    from_party: str
    to_party: str
    through_counsel: Optional[str] = None
    subject: str
    summary: Optional[str] = None
    content: Optional[str] = None
    relief_demanded: Optional[str] = None
    notice_date: date
    response_due_date: Optional[date] = None
    delivery_mode: Optional[str] = None
    case_id: Optional[UUID] = None
    document_path: Optional[str] = None
    counsel_id: Optional[UUID] = None
    internal_notes: Optional[str] = None


class LegalNoticeCreate(LegalNoticeBase):
    pass


class LegalNoticeUpdate(BaseModel):
    notice_type: Optional[str] = None
    status: Optional[str] = None
    from_party: Optional[str] = None
    to_party: Optional[str] = None
    through_counsel: Optional[str] = None
    subject: Optional[str] = None
    summary: Optional[str] = None
    content: Optional[str] = None
    relief_demanded: Optional[str] = None
    received_date: Optional[date] = None
    response_due_date: Optional[date] = None
    response_date: Optional[date] = None
    delivery_mode: Optional[str] = None
    tracking_number: Optional[str] = None
    delivery_status: Optional[str] = None
    delivery_date: Optional[date] = None
    led_to_case: Optional[bool] = None
    reply_document_path: Optional[str] = None
    internal_notes: Optional[str] = None


class LegalNoticeInDB(LegalNoticeBase):
    id: UUID
    company_id: UUID
    notice_number: str
    status: str
    received_date: Optional[date] = None
    response_date: Optional[date] = None
    tracking_number: Optional[str] = None
    delivery_status: Optional[str] = None
    delivery_date: Optional[date] = None
    led_to_case: bool
    reply_document_path: Optional[str] = None
    handled_by: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class LegalNoticeList(BaseModel):
    items: List[LegalNoticeInDB]
    total: int
    page: int
    size: int


# Dashboard Schemas
class LegalDashboardStats(BaseModel):
    total_cases: int
    active_cases: int
    closed_cases: int
    pending_hearings: int
    overdue_tasks: int
    total_claim_amount: Decimal
    total_expenses: Decimal
    total_contracts: int
    expiring_contracts: int
    pending_notices: int


class LegalDashboardSummary(BaseModel):
    stats: LegalDashboardStats
    cases_by_type: Dict[str, int]
    cases_by_status: Dict[str, int]
    upcoming_hearings: List[Dict[str, Any]]
    overdue_tasks: List[Dict[str, Any]]
    recent_cases: List[Dict[str, Any]]
    expiring_contracts: List[Dict[str, Any]]
