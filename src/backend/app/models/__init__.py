"""Database models."""
# Base
from app.models.base import BaseModel, TenantBaseModel

# User
from app.models.user import User, UserRole, UserSession, AuditLog

# Company
from app.models.company import CompanyProfile, CompanyStatutory, Department, Designation

# Employee
from app.models.employee import (
    Employee, EmploymentStatus, EmploymentType,
    EmployeeContact, EmployeeIdentity, EmployeeBank
)

# Payroll
from app.models.payroll import (
    PayrollRun, PayrollStatus, SalaryComponent, ComponentType,
    EmployeeSalary, EmployeeSalaryComponent, Payslip,
    PFMonthlyData, ESIMonthlyData, TDSMonthlyData, TaxDeclaration
)

# Leave
from app.models.leave import (
    LeaveType, LeaveTypeCode, LeavePolicy, LeaveBalance, LeaveRequest,
    LeaveStatus, DayType, Holiday, CompensatoryOff, LeaveEncashment,
    LeaveTransaction, AccrualFrequency, Gender
)

# Timesheet
from app.models.timesheet import (
    TimesheetPeriod, Timesheet, TimesheetEntry, TimesheetStatus,
    AttendanceStatus, AttendanceLog, OvertimeRequest, OvertimeStatus,
    ShiftSchedule, EmployeeShift, TimesheetProject, TimesheetTask,
    ProjectStatus as TimesheetProjectStatus, TaskStatus as TimesheetTaskStatus
)

# Document
from app.models.document import (
    Document, DocumentFolder, DocumentVersion, DocumentShare, DocumentAuditLog,
    DocumentCategory, DocumentStatus, DocumentType, EmployeeDocument
)

# Accounting
from app.models.accounting import (
    Account, AccountType, AccountSubType, FinancialYear, AccountingPeriod,
    JournalEntry, JournalLine, JournalType, JournalStatus, GeneralLedger,
    CostCenter, BudgetEntry
)

# Customer/Vendor
from app.models.customer import (
    Party, PartyType, PartyAddress, PartyContact,
    GSTRegistrationType, PaymentTerms
)

# Currency (MOD-19)
from app.models.currency import Currency, ExchangeRate, CompanyCurrency

# Invoice
from app.models.invoice import (
    Invoice, InvoiceItem, InvoicePayment, InvoiceType, InvoiceStatus,
    GSTTreatment, PlaceOfSupply
)

# Bill
from app.models.bill import (
    Bill, BillItem, BillPayment, BillType, BillStatus, TDSSection
)

# Payment
from app.models.payment import (
    Payment, PaymentAllocation, AdvancePayment, TDSPayment,
    PaymentType, PaymentMode, PaymentStatus, ChequeStatus
)

# Banking
from app.models.banking import (
    CompanyBankAccount, BankTransaction, BankReconciliation,
    BankReconciliationItem, ChequeRegister, BankStatementImport,
    BankAccountType, TransactionType, ReconciliationStatus,
    PaymentBatch, PaymentInstruction, PaymentBatchType,
    PaymentBatchStatus, PaymentInstructionStatus,
    PaymentMode as BankingPaymentMode
)

# CRM
from app.models.crm import (
    Lead, Contact, Customer, Opportunity, Activity, Note, Pipeline,
    LeadSource, LeadStatus, OpportunityStage, ActivityType, EntityType,
    GSTRegistrationType as CRMGSTRegistrationType,
    PaymentTerms as CRMPaymentTerms
)

# Project
from app.models.project import (
    Project, Milestone, Task, TimeEntry, ProjectTeam,
    ProjectStatus, ProjectType, TaskStatus, TaskPriority
)

# AI
from app.models.ai import (
    AIConversation, AIMessage, AIUsage, AIPromptTemplate,
    AIQuota, AIDocumentAnalysis, AIProvider, AIFeature
)

# Reports
from app.models.reports import (
    ReportTemplate, ReportSchedule, ReportExecution, SavedReport,
    ReportType, ReportCategory, ScheduleFrequency, ExecutionStatus
)

# GST
from app.models.gst import (
    GSTReturn, GSTR1, GSTR2A, GSTR3B, GSTReconciliation, HSNSummary,
    GSTLedger, ITCTracking, GSTReturnType, GSTReturnStatus,
    GSTR2AAction, ReconciliationStatus as GSTReconciliationStatus, GSTRate
)

# Settings
from app.models.settings import (
    CompanyBranch,
    PFSettings, ESISettings, PTSettings, TDSSettings, PaySchedule,
    WeekOffSetting,
    Shift, OvertimeRule, AttendanceConfig, GeoFenceLocation,
    EmailTemplate, Role,
    CalculationType, AttendanceMarkingMethod
)

# Onboarding
from app.models.onboarding import (
    OnboardingTemplate, OnboardingTemplateTask, OnboardingSession,
    OnboardingTask, OnboardingDocument, OnboardingStatus,
    TaskStatus as OnboardingTaskStatus, TaskPriority as OnboardingTaskPriority,
    TaskCategory as OnboardingTaskCategory
)

# Recruitment
from app.models.recruitment import (
    JobOpening, Candidate, JobApplication, Interview,
    JobStatus, JobType, CandidateStatus, ApplicationStage, CandidateSource
)

# Exit Management
from app.models.exit import (
    ExitCase, ClearanceTask, FinalSettlement,
    ExitType, ExitStatus, ClearanceStatus
)

# WBS (Work Breakdown Structure)
from app.models.wbs import (
    WBSPhase, WBSModule, WBSTask, WBSAgentContext,
    WBSExecutionLog, WBSQualityGate, WBSAgentConfig
)

# Subscription & Billing
from app.models.subscription import (
    SubscriptionPlan, PricingTier, Subscription, BillingCycle,
    SubscriptionInvoice, SubscriptionPayment, UsageMeter,
    Discount, SubscriptionDiscount, SubscriptionAuditLog,
    PlanType, BillingInterval, SubscriptionStatus, InvoiceStatus,
    PaymentStatus, PaymentMethod, UsageType, DiscountType
)

# Super Admin Portal
from app.models.superadmin import (
    SuperAdmin, SuperAdminSession, SuperAdminRole,
    TenantProfile, TenantStatus, TenantImpersonation,
    PlatformSettings, FeatureFlag, FeatureFlagStatus, TenantFeatureOverride,
    SystemAnnouncement, AnnouncementType, AnnouncementAudience, AnnouncementDismissal,
    SupportTicket, TicketResponse, TicketStatus, TicketPriority,
    SuperAdminAuditLog, PlatformMetricsDaily
)

# Legal
from app.models.legal import (
    LegalCase, LegalCounsel, LegalHearing, LegalDocument, LegalParty,
    LegalTask, LegalExpense, LegalContract, LegalNotice,
    CaseType, CaseStatus, CasePriority, PartyRole, CourtLevel,
    HearingType, HearingStatus, DocumentCategory as LegalDocumentCategory,
    TaskStatus as LegalTaskStatus
)

# Compliance
from app.models.compliance import (
    ComplianceMaster, ComplianceTask, ComplianceCalendar,
    ComplianceAudit, ComplianceRiskAssessment, CompliancePolicy, ComplianceTraining,
    ComplianceCategory, ComplianceFrequency, ComplianceStatus, RiskLevel
)

# Manufacturing
from app.models.manufacturing import (
    WorkCenter, BillOfMaterials, BOMLine, ProductionRouting, RoutingOperation,
    ProductionOrder, WorkOrder, WorkOrderTimeEntry,
    MaterialIssue, MaterialIssueLine, ProductionReceipt,
    WorkCenterDowntime, ProductionShift,
    WorkCenterType, WorkCenterStatus, BOMType, BOMStatus,
    RoutingStatus, ProductionOrderStatus, ProductionOrderPriority,
    WorkOrderStatus, ShiftType, DowntimeType
)

# Quality Control
from app.models.quality import (
    QualityParameter, InspectionPlan, InspectionPlanCharacteristic,
    QualityInspection, InspectionResult_ as InspectionResultRecord,
    NonConformanceReport, CAPA, CalibrationRecord,
    InspectionType, InspectionStatus, InspectionResult,
    NCRStatus, NCRSeverity, CAPAType, CAPAStatus
)

__all__ = [
    # Base
    "BaseModel", "TenantBaseModel",
    # User
    "User", "UserRole", "UserSession", "AuditLog",
    # Company
    "CompanyProfile", "CompanyStatutory", "Department", "Designation",
    # Employee
    "Employee", "EmploymentStatus", "EmploymentType",
    "EmployeeContact", "EmployeeIdentity", "EmployeeBank",
    # Payroll
    "PayrollRun", "PayrollStatus", "SalaryComponent", "ComponentType",
    "EmployeeSalary", "EmployeeSalaryComponent", "Payslip",
    "PFMonthlyData", "ESIMonthlyData", "TDSMonthlyData", "TaxDeclaration",
    # Leave
    "LeaveType", "LeaveTypeCode", "LeavePolicy", "LeaveBalance", "LeaveRequest",
    "LeaveStatus", "DayType", "Holiday", "CompensatoryOff", "LeaveEncashment",
    "LeaveTransaction", "AccrualFrequency", "Gender",
    # Timesheet
    "TimesheetPeriod", "Timesheet", "TimesheetEntry", "TimesheetStatus",
    "AttendanceStatus", "AttendanceLog", "OvertimeRequest", "OvertimeStatus",
    "ShiftSchedule", "EmployeeShift",
    # Document
    "Document", "DocumentFolder", "DocumentVersion",
    "DocumentCategory", "DocumentStatus",
    # Accounting
    "Account", "AccountType", "AccountSubType", "FinancialYear", "AccountingPeriod",
    "JournalEntry", "JournalLine", "JournalType", "JournalStatus", "GeneralLedger",
    "CostCenter", "BudgetEntry",
    # Customer/Vendor
    "Party", "PartyType", "PartyAddress", "PartyContact",
    "GSTRegistrationType", "PaymentTerms",
    # Currency (MOD-19)
    "Currency", "ExchangeRate", "CompanyCurrency",
    # Invoice
    "Invoice", "InvoiceItem", "InvoicePayment", "InvoiceType", "InvoiceStatus",
    "GSTTreatment", "PlaceOfSupply",
    # Bill
    "Bill", "BillItem", "BillPayment", "BillType", "BillStatus", "TDSSection",
    # Payment
    "Payment", "PaymentAllocation", "AdvancePayment", "TDSPayment",
    "PaymentType", "PaymentMode", "PaymentStatus", "ChequeStatus",
    # Banking
    "CompanyBankAccount", "BankTransaction", "BankReconciliation",
    "BankReconciliationItem", "ChequeRegister", "BankStatementImport",
    "BankAccountType", "TransactionType", "ReconciliationStatus",
    "PaymentBatch", "PaymentInstruction", "PaymentBatchType",
    "PaymentBatchStatus", "PaymentInstructionStatus", "BankingPaymentMode",
    # CRM
    "Lead", "Contact", "Customer", "Opportunity", "Activity", "Note", "Pipeline",
    "LeadSource", "LeadStatus", "OpportunityStage", "ActivityType", "EntityType",
    "CRMGSTRegistrationType", "CRMPaymentTerms",
    # Project
    "Project", "Milestone", "Task", "TimeEntry", "ProjectTeam",
    "ProjectStatus", "ProjectType", "TaskStatus", "TaskPriority",
    # AI
    "AIConversation", "AIMessage", "AIUsage", "AIPromptTemplate",
    "AIQuota", "AIDocumentAnalysis", "AIProvider", "AIFeature",
    # Reports
    "ReportTemplate", "ReportSchedule", "ReportExecution", "SavedReport",
    "ReportType", "ReportCategory", "ScheduleFrequency", "ExecutionStatus",
    # GST
    "GSTReturn", "GSTR1", "GSTR2A", "GSTR3B", "GSTReconciliation", "HSNSummary",
    "GSTLedger", "ITCTracking", "GSTReturnType", "GSTReturnStatus",
    "GSTR2AAction", "GSTReconciliationStatus", "GSTRate",
    # Settings
    "CompanyBranch",
    "PFSettings", "ESISettings", "PTSettings", "TDSSettings", "PaySchedule",
    "WeekOffSetting",
    "Shift", "OvertimeRule", "AttendanceConfig", "GeoFenceLocation",
    "EmailTemplate", "Role",
    "CalculationType", "AttendanceMarkingMethod",
    # Onboarding
    "OnboardingTemplate", "OnboardingTemplateTask", "OnboardingSession",
    "OnboardingTask", "OnboardingDocument", "OnboardingStatus",
    "OnboardingTaskStatus", "OnboardingTaskPriority", "OnboardingTaskCategory",
    # Recruitment
    "JobOpening", "Candidate", "JobApplication", "Interview",
    "JobStatus", "JobType", "CandidateStatus", "ApplicationStage", "CandidateSource",
    # Exit Management
    "ExitCase", "ClearanceTask", "FinalSettlement",
    "ExitType", "ExitStatus", "ClearanceStatus",
    # WBS
    "WBSPhase", "WBSModule", "WBSTask", "WBSAgentContext",
    "WBSExecutionLog", "WBSQualityGate", "WBSAgentConfig",
    # Subscription & Billing
    "SubscriptionPlan", "PricingTier", "Subscription", "BillingCycle",
    "SubscriptionInvoice", "SubscriptionPayment", "UsageMeter",
    "Discount", "SubscriptionDiscount", "SubscriptionAuditLog",
    "PlanType", "BillingInterval", "SubscriptionStatus", "InvoiceStatus",
    "PaymentStatus", "PaymentMethod", "UsageType", "DiscountType",
    # Super Admin Portal
    "SuperAdmin", "SuperAdminSession", "SuperAdminRole",
    "TenantProfile", "TenantStatus", "TenantImpersonation",
    "PlatformSettings", "FeatureFlag", "FeatureFlagStatus", "TenantFeatureOverride",
    "SystemAnnouncement", "AnnouncementType", "AnnouncementAudience", "AnnouncementDismissal",
    "SupportTicket", "TicketResponse", "TicketStatus", "TicketPriority",
    "SuperAdminAuditLog", "PlatformMetricsDaily",
    # Legal
    "LegalCase", "LegalCounsel", "LegalHearing", "LegalDocument", "LegalParty",
    "LegalTask", "LegalExpense", "LegalContract", "LegalNotice",
    "CaseType", "CaseStatus", "CasePriority", "PartyRole", "CourtLevel",
    "HearingType", "HearingStatus", "LegalDocumentCategory", "LegalTaskStatus",
    # Compliance
    "ComplianceMaster", "ComplianceTask", "ComplianceCalendar",
    "ComplianceAudit", "ComplianceRiskAssessment", "CompliancePolicy", "ComplianceTraining",
    "ComplianceCategory", "ComplianceFrequency", "ComplianceStatus", "RiskLevel",
    # Manufacturing
    "WorkCenter", "BillOfMaterials", "BOMLine", "ProductionRouting", "RoutingOperation",
    "ProductionOrder", "WorkOrder", "WorkOrderTimeEntry",
    "MaterialIssue", "MaterialIssueLine", "ProductionReceipt",
    "WorkCenterDowntime", "ProductionShift",
    "WorkCenterType", "WorkCenterStatus", "BOMType", "BOMStatus",
    "RoutingStatus", "ProductionOrderStatus", "ProductionOrderPriority",
    "WorkOrderStatus", "ShiftType", "DowntimeType",
    # Quality Control
    "QualityParameter", "InspectionPlan", "InspectionPlanCharacteristic",
    "QualityInspection", "InspectionResultRecord",
    "NonConformanceReport", "CAPA", "CalibrationRecord",
    "InspectionType", "InspectionStatus", "InspectionResult",
    "NCRStatus", "NCRSeverity", "CAPAType", "CAPAStatus",
]
