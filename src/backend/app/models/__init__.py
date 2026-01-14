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
    Document, DocumentTemplate, DocumentShare, DocumentAuditLog,
    EmployeeDocument, DocumentCategory, DocumentType, DocumentStatus, Folder
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
    GSTRegistrationType, PaymentTerms, Currency, ExchangeRate
)

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
    "Document", "DocumentTemplate", "DocumentShare", "DocumentAuditLog",
    "EmployeeDocument", "DocumentCategory", "DocumentType", "DocumentStatus", "Folder",
    # Accounting
    "Account", "AccountType", "AccountSubType", "FinancialYear", "AccountingPeriod",
    "JournalEntry", "JournalLine", "JournalType", "JournalStatus", "GeneralLedger",
    "CostCenter", "BudgetEntry",
    # Customer/Vendor
    "Party", "PartyType", "PartyAddress", "PartyContact",
    "GSTRegistrationType", "PaymentTerms", "Currency", "ExchangeRate",
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
]
