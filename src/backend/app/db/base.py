"""
Database Base - Re-export Base and all models
This file imports Base and all models so that SQLAlchemy can discover them.
"""
from app.db.session import Base

# Import all models to register them with Base.metadata
# User and Auth
from app.models.user import User, UserSession, AuditLog

# Company and Organization
from app.models.company import CompanyProfile, CompanyStatutory, Department, Designation

# Employee
from app.models.employee import Employee, EmployeeContact, EmployeeIdentity, EmployeeBank

# Settings
from app.models.settings import (
    CompanyBranch, PFSettings, ESISettings, PTSettings, TDSSettings,
    PaySchedule, WeekOffSetting, Shift, OvertimeRule, AttendanceConfig,
    GeoFenceLocation, EmailTemplate, Role
)

# Leave
from app.models.leave import (
    LeaveType, LeaveRequest, LeaveBalance, LeavePolicy,
    Holiday, CompensatoryOff, LeaveEncashment, LeaveTransaction
)

# Payroll
from app.models.payroll import (
    SalaryComponent, EmployeeSalary, EmployeeSalaryComponent,
    PayrollRun, Payslip, PFMonthlyData, ESIMonthlyData, TDSMonthlyData, TaxDeclaration
)

# Document
from app.models.document import (
    Document, Folder, DocumentTemplate, DocumentShare, DocumentAuditLog, EmployeeDocument
)

# Accounting
from app.models.accounting import (
    Account, FinancialYear, AccountingPeriod, JournalEntry, JournalLine,
    GeneralLedger, CostCenter, BudgetEntry
)

# Invoice and Bill
from app.models.invoice import Invoice, InvoiceItem, InvoicePayment
from app.models.bill import Bill, BillItem, BillPayment

# Payment
from app.models.payment import Payment, PaymentAllocation, AdvancePayment, TDSPayment

# Customer/Vendor (Party)
from app.models.customer import Party, PartyAddress, PartyContact, Currency, ExchangeRate

# GST
from app.models.gst import (
    GSTReturn, GSTR1, GSTR2A, GSTR3B, GSTReconciliation,
    HSNSummary, GSTLedger, ITCTracking
)

# Banking
from app.models.banking import (
    CompanyBankAccount, BankTransaction, BankReconciliation, BankReconciliationItem,
    ChequeRegister, BankStatementImport, PaymentBatch, PaymentInstruction
)

# CRM
from app.models.crm import Lead, Contact, Customer, Opportunity, Activity, Note, Pipeline

# Project
from app.models.project import Project, Milestone, Task, TimeEntry, ProjectTeam

# Timesheet
from app.models.timesheet import (
    TimesheetPeriod, TimesheetProject, TimesheetTask, Timesheet, TimesheetEntry,
    AttendanceLog, OvertimeRequest, ShiftSchedule, EmployeeShift
)

# Reports
from app.models.reports import ReportTemplate, ReportSchedule, ReportExecution, SavedReport

# AI
from app.models.ai import AIConversation, AIMessage, AIUsage, AIPromptTemplate, AIQuota, AIDocumentAnalysis

# Re-export Base for imports
__all__ = ['Base']
