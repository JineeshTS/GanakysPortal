"""
Quality Control Schemas
"""
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel
from enum import Enum


class InspectionType(str, Enum):
    INCOMING = "incoming"
    IN_PROCESS = "in_process"
    FINAL = "final"
    PERIODIC = "periodic"
    CUSTOMER_COMPLAINT = "customer_complaint"


class InspectionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InspectionResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    PENDING = "pending"


class NCRStatus(str, Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    CORRECTIVE_ACTION = "corrective_action"
    VERIFICATION = "verification"
    CLOSED = "closed"


class NCRSeverity(str, Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class CAPAType(str, Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"


class CAPAStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFICATION = "verification"
    CLOSED = "closed"


# Parameter Schemas
class ParameterBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parameter_type: str
    uom: Optional[str] = None
    target_value: Optional[Decimal] = None
    upper_limit: Optional[Decimal] = None
    lower_limit: Optional[Decimal] = None
    is_critical: bool = False


class ParameterCreate(ParameterBase):
    pass


class ParameterResponse(ParameterBase):
    id: UUID
    company_id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Inspection Plan Schemas
class InspectionPlanCharacteristicBase(BaseModel):
    parameter_id: UUID
    sequence: int
    is_mandatory: bool = True
    target_value: Optional[Decimal] = None
    upper_limit: Optional[Decimal] = None
    lower_limit: Optional[Decimal] = None
    inspection_method: Optional[str] = None
    equipment_required: Optional[str] = None


class InspectionPlanCharacteristicCreate(InspectionPlanCharacteristicBase):
    pass


class InspectionPlanCharacteristicResponse(InspectionPlanCharacteristicBase):
    id: UUID
    plan_id: UUID
    parameter_name: Optional[str] = None

    class Config:
        from_attributes = True


class InspectionPlanBase(BaseModel):
    name: str
    description: Optional[str] = None
    product_id: Optional[UUID] = None
    inspection_type: InspectionType
    sample_size: int = 1
    sampling_method: Optional[str] = None


class InspectionPlanCreate(InspectionPlanBase):
    characteristics: List[InspectionPlanCharacteristicCreate] = []


class InspectionPlanResponse(InspectionPlanBase):
    id: UUID
    company_id: UUID
    plan_number: str
    version: int
    is_active: bool
    characteristics: List[InspectionPlanCharacteristicResponse] = []
    created_at: datetime

    class Config:
        from_attributes = True


# Inspection Schemas
class InspectionResultBase(BaseModel):
    parameter_id: UUID
    sample_number: int = 1
    numeric_value: Optional[Decimal] = None
    text_value: Optional[str] = None
    boolean_value: Optional[bool] = None
    is_pass: bool = True
    notes: Optional[str] = None


class InspectionResultCreate(InspectionResultBase):
    pass


class InspectionResultResponse(InspectionResultBase):
    id: UUID
    inspection_id: UUID
    deviation: Optional[Decimal] = None
    parameter_name: Optional[str] = None

    class Config:
        from_attributes = True


class InspectionBase(BaseModel):
    inspection_type: InspectionType
    plan_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    production_order_id: Optional[UUID] = None
    purchase_order_id: Optional[UUID] = None
    vendor_id: Optional[UUID] = None
    lot_number: Optional[str] = None
    lot_quantity: Decimal = Decimal("0")
    sample_size: int = 1
    inspection_date: date
    inspector_id: Optional[UUID] = None
    notes: Optional[str] = None


class InspectionCreate(InspectionBase):
    results: List[InspectionResultCreate] = []


class InspectionUpdate(BaseModel):
    status: Optional[InspectionStatus] = None
    result: Optional[InspectionResult] = None
    accepted_quantity: Optional[Decimal] = None
    rejected_quantity: Optional[Decimal] = None
    rework_quantity: Optional[Decimal] = None
    notes: Optional[str] = None


class InspectionResponse(InspectionBase):
    id: UUID
    company_id: UUID
    inspection_number: str
    status: InspectionStatus
    result: InspectionResult
    completed_date: Optional[datetime] = None
    accepted_quantity: Decimal
    rejected_quantity: Decimal
    rework_quantity: Decimal
    results: List[InspectionResultResponse] = []
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# NCR Schemas
class NCRBase(BaseModel):
    title: str
    description: str
    severity: NCRSeverity = NCRSeverity.MINOR
    source: str
    inspection_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    batch_id: Optional[UUID] = None
    process_area: Optional[str] = None
    affected_quantity: Decimal = Decimal("0")
    uom: Optional[str] = None
    detected_date: date
    target_closure_date: Optional[date] = None
    assigned_to: Optional[UUID] = None


class NCRCreate(NCRBase):
    pass


class NCRUpdate(BaseModel):
    status: Optional[NCRStatus] = None
    severity: Optional[NCRSeverity] = None
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = None
    containment_action: Optional[str] = None
    containment_date: Optional[date] = None
    disposition: Optional[str] = None
    disposition_notes: Optional[str] = None
    cost_of_nonconformance: Optional[Decimal] = None


class NCRResponse(NCRBase):
    id: UUID
    company_id: UUID
    ncr_number: str
    status: NCRStatus
    root_cause: Optional[str] = None
    root_cause_category: Optional[str] = None
    containment_action: Optional[str] = None
    containment_date: Optional[date] = None
    disposition: Optional[str] = None
    cost_of_nonconformance: Decimal
    closed_date: Optional[datetime] = None
    raised_by: UUID
    product_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# CAPA Schemas
class CAPABase(BaseModel):
    title: str
    description: str
    capa_type: CAPAType
    ncr_id: Optional[UUID] = None
    action_plan: str
    expected_outcome: Optional[str] = None
    identified_date: date
    target_date: date
    assigned_to: UUID


class CAPACreate(CAPABase):
    pass


class CAPAUpdate(BaseModel):
    status: Optional[CAPAStatus] = None
    root_cause_analysis: Optional[str] = None
    root_cause_method: Optional[str] = None
    action_plan: Optional[str] = None
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    effectiveness_verified: Optional[bool] = None


class CAPAResponse(CAPABase):
    id: UUID
    company_id: UUID
    capa_number: str
    status: CAPAStatus
    root_cause_analysis: Optional[str] = None
    root_cause_method: Optional[str] = None
    verification_method: Optional[str] = None
    verification_result: Optional[str] = None
    effectiveness_verified: bool
    completed_date: Optional[datetime] = None
    verification_date: Optional[date] = None
    raised_by: UUID
    verified_by: Optional[UUID] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Calibration Schemas
class CalibrationBase(BaseModel):
    equipment_id: str
    equipment_name: str
    serial_number: Optional[str] = None
    location: Optional[str] = None
    calibration_date: date
    next_calibration_date: date
    calibration_interval_days: int
    calibrated_by: str
    certificate_number: Optional[str] = None
    result: str
    notes: Optional[str] = None


class CalibrationCreate(CalibrationBase):
    pass


class CalibrationResponse(CalibrationBase):
    id: UUID
    company_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


# Dashboard
class QualityDashboard(BaseModel):
    total_inspections: int
    passed_inspections: int
    failed_inspections: int
    pending_inspections: int
    pass_rate: Decimal
    open_ncrs: int
    critical_ncrs: int
    open_capas: int
    overdue_capas: int
    calibrations_due: int
    recent_inspections: List[InspectionResponse]
    recent_ncrs: List[NCRResponse]


# List Responses
class InspectionListResponse(BaseModel):
    items: List[InspectionResponse]
    total: int
    page: int
    page_size: int


class NCRListResponse(BaseModel):
    items: List[NCRResponse]
    total: int
    page: int
    page_size: int


class CAPAListResponse(BaseModel):
    items: List[CAPAResponse]
    total: int
    page: int
    page_size: int
