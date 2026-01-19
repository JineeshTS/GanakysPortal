"""
Quality Control Models
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
from app.models.base import Base, TimestampMixin, SoftDeleteMixin
import enum


class InspectionType(str, enum.Enum):
    INCOMING = "incoming"
    IN_PROCESS = "in_process"
    FINAL = "final"
    PERIODIC = "periodic"
    CUSTOMER_COMPLAINT = "customer_complaint"


class InspectionStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class InspectionResult(str, enum.Enum):
    PASS = "pass"
    FAIL = "fail"
    CONDITIONAL = "conditional"
    PENDING = "pending"


class NCRStatus(str, enum.Enum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    CORRECTIVE_ACTION = "corrective_action"
    VERIFICATION = "verification"
    CLOSED = "closed"


class NCRSeverity(str, enum.Enum):
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class CAPAType(str, enum.Enum):
    CORRECTIVE = "corrective"
    PREVENTIVE = "preventive"


class CAPAStatus(str, enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    VERIFICATION = "verification"
    CLOSED = "closed"


class QualityParameter(Base, TimestampMixin, SoftDeleteMixin):
    """Quality parameter / characteristic definition"""
    __tablename__ = "quality_parameters"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    code: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    parameter_type: Mapped[str] = mapped_column(String(50))  # numeric, text, boolean
    uom: Mapped[Optional[str]] = mapped_column(String(20))

    # Specification limits (for numeric)
    target_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    upper_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    lower_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    upper_warning: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    lower_warning: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))

    # For text/list parameters
    acceptable_values: Mapped[Optional[List[str]]] = mapped_column(ARRAY(String))

    is_critical: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class InspectionPlan(Base, TimestampMixin, SoftDeleteMixin):
    """Inspection plan / control plan"""
    __tablename__ = "quality_inspection_plans"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    plan_number: Mapped[str] = mapped_column(String(50), unique=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[Optional[str]] = mapped_column(Text)

    product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))
    product_category_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("product_categories.id"))

    inspection_type: Mapped[InspectionType] = mapped_column(SQLEnum(InspectionType))

    # Sampling
    sample_size: Mapped[int] = mapped_column(Integer, default=1)
    sampling_method: Mapped[Optional[str]] = mapped_column(String(100))

    version: Mapped[int] = mapped_column(Integer, default=1)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    effective_from: Mapped[Optional[date]] = mapped_column(Date)
    effective_to: Mapped[Optional[date]] = mapped_column(Date)

    # Relationships
    characteristics: Mapped[List["InspectionPlanCharacteristic"]] = relationship(
        back_populates="plan", cascade="all, delete-orphan"
    )


class InspectionPlanCharacteristic(Base, TimestampMixin):
    """Inspection plan characteristic / check point"""
    __tablename__ = "quality_inspection_plan_characteristics"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    plan_id: Mapped[UUID] = mapped_column(ForeignKey("quality_inspection_plans.id"))
    parameter_id: Mapped[UUID] = mapped_column(ForeignKey("quality_parameters.id"))

    sequence: Mapped[int] = mapped_column(Integer)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)

    # Override limits from parameter
    target_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    upper_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    lower_limit: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))

    inspection_method: Mapped[Optional[str]] = mapped_column(String(200))
    equipment_required: Mapped[Optional[str]] = mapped_column(String(200))

    # Relationships
    plan: Mapped["InspectionPlan"] = relationship(back_populates="characteristics")


class QualityInspection(Base, TimestampMixin, SoftDeleteMixin):
    """Quality inspection record"""
    __tablename__ = "quality_inspections"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    inspection_number: Mapped[str] = mapped_column(String(50), unique=True)
    inspection_type: Mapped[InspectionType] = mapped_column(SQLEnum(InspectionType))
    status: Mapped[InspectionStatus] = mapped_column(
        SQLEnum(InspectionStatus), default=InspectionStatus.PENDING
    )
    result: Mapped[InspectionResult] = mapped_column(
        SQLEnum(InspectionResult), default=InspectionResult.PENDING
    )

    # Reference
    plan_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("quality_inspection_plans.id"))
    product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))
    batch_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("stock_batches.id"))
    production_order_id: Mapped[Optional[UUID]] = mapped_column(
        ForeignKey("manufacturing_production_orders.id")
    )
    purchase_order_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("purchase_orders.id"))
    vendor_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("vendors.id"))

    # Lot/Sample info
    lot_number: Mapped[Optional[str]] = mapped_column(String(100))
    lot_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    sample_size: Mapped[int] = mapped_column(Integer, default=1)

    # Dates
    inspection_date: Mapped[date] = mapped_column(Date)
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Inspector
    inspector_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("employees.id"))
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    reviewed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Disposition
    accepted_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    rejected_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    rework_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    results: Mapped[List["InspectionResult_"]] = relationship(
        back_populates="inspection", cascade="all, delete-orphan"
    )


class InspectionResult_(Base, TimestampMixin):
    """Individual inspection measurement/result"""
    __tablename__ = "quality_inspection_results"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    inspection_id: Mapped[UUID] = mapped_column(ForeignKey("quality_inspections.id"))
    parameter_id: Mapped[UUID] = mapped_column(ForeignKey("quality_parameters.id"))

    sample_number: Mapped[int] = mapped_column(Integer, default=1)

    # Measured value (numeric or text)
    numeric_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))
    text_value: Mapped[Optional[str]] = mapped_column(String(500))
    boolean_value: Mapped[Optional[bool]] = mapped_column(Boolean)

    # Result
    is_pass: Mapped[bool] = mapped_column(Boolean, default=True)
    deviation: Mapped[Optional[Decimal]] = mapped_column(Numeric(15, 4))

    notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    inspection: Mapped["QualityInspection"] = relationship(back_populates="results")


class NonConformanceReport(Base, TimestampMixin, SoftDeleteMixin):
    """NCR - Non-Conformance Report"""
    __tablename__ = "quality_ncrs"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    ncr_number: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)

    status: Mapped[NCRStatus] = mapped_column(SQLEnum(NCRStatus), default=NCRStatus.OPEN)
    severity: Mapped[NCRSeverity] = mapped_column(SQLEnum(NCRSeverity), default=NCRSeverity.MINOR)

    # Source
    source: Mapped[str] = mapped_column(String(100))  # inspection, customer, internal, audit
    inspection_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("quality_inspections.id"))

    # Product/Process reference
    product_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("products.id"))
    batch_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("stock_batches.id"))
    process_area: Mapped[Optional[str]] = mapped_column(String(200))

    # Quantities
    affected_quantity: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)
    uom: Mapped[Optional[str]] = mapped_column(String(20))

    # Root cause
    root_cause: Mapped[Optional[str]] = mapped_column(Text)
    root_cause_category: Mapped[Optional[str]] = mapped_column(String(100))

    # Containment
    containment_action: Mapped[Optional[str]] = mapped_column(Text)
    containment_date: Mapped[Optional[date]] = mapped_column(Date)

    # Disposition
    disposition: Mapped[Optional[str]] = mapped_column(String(100))  # use_as_is, rework, scrap, return
    disposition_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Cost
    cost_of_nonconformance: Mapped[Decimal] = mapped_column(Numeric(15, 4), default=0)

    # Dates
    detected_date: Mapped[date] = mapped_column(Date)
    target_closure_date: Mapped[Optional[date]] = mapped_column(Date)
    closed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # People
    raised_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))
    closed_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    capas: Mapped[List["CAPA"]] = relationship(back_populates="ncr")


class CAPA(Base, TimestampMixin, SoftDeleteMixin):
    """CAPA - Corrective and Preventive Action"""
    __tablename__ = "quality_capas"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    capa_number: Mapped[str] = mapped_column(String(50), unique=True)
    title: Mapped[str] = mapped_column(String(300))
    description: Mapped[str] = mapped_column(Text)

    capa_type: Mapped[CAPAType] = mapped_column(SQLEnum(CAPAType))
    status: Mapped[CAPAStatus] = mapped_column(SQLEnum(CAPAStatus), default=CAPAStatus.OPEN)

    # Source
    ncr_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("quality_ncrs.id"))
    audit_finding_id: Mapped[Optional[UUID]] = mapped_column(String(50))
    customer_complaint_id: Mapped[Optional[str]] = mapped_column(String(50))

    # Root cause analysis
    root_cause_analysis: Mapped[Optional[str]] = mapped_column(Text)
    root_cause_method: Mapped[Optional[str]] = mapped_column(String(100))  # 5-why, fishbone, etc.

    # Action plan
    action_plan: Mapped[str] = mapped_column(Text)
    expected_outcome: Mapped[Optional[str]] = mapped_column(Text)

    # Verification
    verification_method: Mapped[Optional[str]] = mapped_column(Text)
    verification_result: Mapped[Optional[str]] = mapped_column(Text)
    effectiveness_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Dates
    identified_date: Mapped[date] = mapped_column(Date)
    target_date: Mapped[date] = mapped_column(Date)
    completed_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    verification_date: Mapped[Optional[date]] = mapped_column(Date)

    # People
    raised_by: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    assigned_to: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    verified_by: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    ncr: Mapped[Optional["NonConformanceReport"]] = relationship(back_populates="capas")


class CalibrationRecord(Base, TimestampMixin):
    """Calibration record for measuring equipment"""
    __tablename__ = "quality_calibrations"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    company_id: Mapped[UUID] = mapped_column(ForeignKey("companies.id"))

    equipment_id: Mapped[str] = mapped_column(String(100))
    equipment_name: Mapped[str] = mapped_column(String(200))
    serial_number: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(200))

    calibration_date: Mapped[date] = mapped_column(Date)
    next_calibration_date: Mapped[date] = mapped_column(Date)
    calibration_interval_days: Mapped[int] = mapped_column(Integer)

    calibrated_by: Mapped[str] = mapped_column(String(200))
    certificate_number: Mapped[Optional[str]] = mapped_column(String(100))

    result: Mapped[str] = mapped_column(String(50))  # pass, fail, adjusted
    notes: Mapped[Optional[str]] = mapped_column(Text)
