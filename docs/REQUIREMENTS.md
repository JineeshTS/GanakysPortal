# GANAPORTAL - FINAL CONSOLIDATED REQUIREMENTS
## AI-First ERP for Ganakys Codilla Apps

**Version:** 3.0 FINAL
**Date:** January 2026
**Author:** Claude (CTO) + Jineesh (Founder)
**Status:** APPROVED FOR AUTONOMOUS BUILD

---

# SECTION 1: PROJECT OVERVIEW

## 1.1 Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | GanaPortal |
| **Type** | AI-First ERP System |
| **Client** | Ganakys Codilla Apps (OPC) Private Limited |
| **Domain** | IT Services & SaaS Company |
| **URL** | portal.ganakys.com |
| **Target Scale** | 5 employees (2026) → 15 employees (2027) |

## 1.2 Vision Statement

GanaPortal is an **AI-First ERP** where artificial intelligence powers EVERY module - not just accounting. The AI extracts, categorizes, predicts, suggests, and automates across the entire system, reducing manual work by 95%.

## 1.3 Build Statistics

| Metric | Value |
|--------|-------|
| **Total Tasks** | 899 |
| **Total Estimated Hours** | 3,588 |
| **Modules** | 23 |
| **Database Tables** | ~120 |
| **API Endpoints** | ~250 |
| **Frontend Screens** | ~60 |

---

# SECTION 2: TECHNOLOGY STACK (LOCKED)

## 2.1 Core Stack

| Layer | Technology | Version | Notes |
|-------|------------|---------|-------|
| **Frontend** | Next.js | 14.x | App Router, TypeScript |
| **UI Library** | shadcn/ui | Latest | Tailwind CSS based |
| **Styling** | Tailwind CSS | 3.x | Utility-first |
| **State** | TanStack Query | 5.x | Server state management |
| **Forms** | React Hook Form + Zod | Latest | Validation |
| **Tables** | TanStack Table | 8.x | Complex data grids |
| **Charts** | Recharts | 2.x | Data visualization |
| **Backend** | FastAPI | 0.109+ | Python 3.11+ |
| **ORM** | SQLAlchemy | 2.0 | Async support |
| **Validation** | Pydantic | 2.x | Schema validation |
| **Migrations** | Alembic | 1.13+ | Database migrations |
| **Database** | PostgreSQL | 16 | Primary data store |
| **Cache** | Redis | 7 | Sessions, caching, queues |
| **Task Queue** | Celery | 5.x | Background jobs |
| **File Storage** | Local FS | - | /var/data/ganaportal/ |

## 2.2 AI Stack (Fallback Chain)

| Priority | Provider | Model | Use Case |
|----------|----------|-------|----------|
| **PRIMARY** | Claude API | claude-3-5-sonnet-20241022 | All AI features |
| **FALLBACK 1** | Gemini API | gemini-1.5-pro | If Claude fails |
| **FALLBACK 2** | OpenAI API | gpt-4-turbo | If Gemini fails |
| **FALLBACK 3** | Together AI | meta-llama/Llama-3-70b | If all others fail |

## 2.3 Infrastructure

| Component | Technology | Notes |
|-----------|------------|-------|
| **Hosting** | Hostinger VPS | Ubuntu 22.04 LTS |
| **Web Server** | Nginx | Reverse proxy |
| **SSL** | Let's Encrypt | Auto-renewal |
| **Containers** | Docker + Compose | Production deployment |
| **CI/CD** | GitHub Actions | Auto-deploy on push |
| **Backups** | pg_dump + rsync | Daily at 2 AM IST |

## 2.4 Third-Party Integrations

| Service | Provider | Purpose |
|---------|----------|---------|
| **Email** | AWS SES / SendGrid | Transactional emails |
| **SMS** | MSG91 | DLT compliant for India |
| **Exchange Rates** | RBI API | Daily forex rates |

---

# SECTION 3: AI-FIRST ARCHITECTURE

## 3.1 AI Brain Layer

Every module in GanaPortal is powered by AI:

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AI BRAIN LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │  DOCUMENT   │  │   PATTERN   │  │   QUERY     │  │ PREDICTION │ │
│  │  PROCESSOR  │  │   MATCHER   │  │   ENGINE    │  │   ENGINE   │ │
│  │             │  │             │  │             │  │            │ │
│  │ • OCR/Vision│  │ • Vendor ID │  │ • NL to SQL │  │ • Forecast │ │
│  │ • Extract   │  │ • Category  │  │ • Chat UI   │  │ • Anomaly  │ │
│  │ • Classify  │  │ • Recurring │  │ • Actions   │  │ • Suggest  │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                                      │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │
│  │ CONFIDENCE  │  │  LEARNING   │  │   ACTION    │  │  FALLBACK  │ │
│  │   SCORER    │  │   ENGINE    │  │  EXECUTOR   │  │   CHAIN    │ │
│  │             │  │             │  │             │  │            │ │
│  │ • 0-100%    │  │ • From      │  │ • Auto-post │  │ • Claude   │ │
│  │ • Threshold │  │   corrections│ │ • Create    │  │ • Gemini   │ │
│  │ • Explain   │  │ • Improve   │  │ • Update    │  │ • OpenAI   │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └────────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## 3.2 AI Confidence Thresholds

| Confidence Level | Action | Human Involvement |
|------------------|--------|-------------------|
| **≥95%** | Auto-execute | None |
| **70-94%** | Queue for review | Quick approve/reject |
| **<70%** | Flag for manual | Full human input |

## 3.3 AI Features by Module

| Module | AI Capabilities |
|--------|-----------------|
| **HRMS** | Extract data from ID cards, resumes, certificates; auto-fill forms |
| **EDMS** | Auto-categorize, tag, summarize documents; smart search |
| **Onboarding** | Guide employees, validate documents, suggest missing items |
| **Leave** | Suggest optimal dates, predict team conflicts, auto-approve routine |
| **Timesheet** | Auto-fill from calendar, suggest task allocation, flag anomalies |
| **Payroll** | Validate calculations, flag anomalies, suggest corrections |
| **Accounting** | 95% auto-bookkeeping, categorize transactions, reconcile |
| **AR (Invoicing)** | Generate from NL, suggest HSN/SAC, predict payment dates |
| **AP (Bills)** | Extract vendor, amount, GST from images; match to PO |
| **Banking** | Auto-reconcile, categorize transactions, detect fraud |
| **GST** | Auto-prepare GSTR-1/3B, validate, suggest corrections |
| **TDS** | Auto-calculate, track thresholds, prepare returns |
| **CRM** | Score leads, draft emails, suggest follow-ups, predict close |
| **Projects** | Estimate tasks, predict delays, suggest resources, track health |
| **Reports** | Generate insights, answer NL queries, explain variances |
| **Compliance** | Remind deadlines, prepare filing data, track status |
| **Quotes** | Generate from brief, suggest pricing, predict acceptance |
| **Assets** | Track depreciation, predict maintenance, optimize licenses |

---

# SECTION 4: USER ROLES & PERMISSIONS

| Role | Code | Access Level |
|------|------|--------------|
| **Admin (Employer)** | `admin` | Full system access |
| **HR Manager** | `hr` | HRMS, EDMS, Payroll, Leave |
| **Accountant** | `accountant` | Accounting, AR/AP, GST, Reports |
| **Employee** | `employee` | Self-service only |
| **External CA** | `external_ca` | Verification access |

---

# SECTION 5: ALL 23 MODULES

## MODULE 1: Infrastructure
- Docker Compose (dev + prod)
- PostgreSQL 16 + Redis 7
- Nginx reverse proxy + SSL
- GitHub Actions CI/CD
- Backup system

## MODULE 2: Authentication & Users
- JWT (access 15min, refresh 7 days)
- Role-based authorization
- Password reset flow
- Session management
- Audit logging

## MODULE 3: Employee Management (HRMS)
- Employee master data
- Profile photo upload
- **AI:** Extract from ID uploads

## MODULE 4: Enterprise Document Management (EDMS)
- Folder hierarchy
- Document versioning
- Full-text search
- **AI:** Auto-categorize, tag

## MODULE 5: Employee Onboarding
- 8-step wizard
- Document checklist
- **AI:** Guide, validate

## MODULE 6: Leave Management
- Leave types (CL, SL, EL, ML, etc.)
- Holiday calendar
- Balance with carry forward
- **AI:** Suggest dates

## MODULE 7: Timesheet Management
- Weekly grid
- Project allocation
- **AI:** Auto-fill suggestions

## MODULE 8: Payroll System
- Salary components
- CTC calculator
- Tax declarations
- Payslip PDF, Form 16
- **AI:** Validate, flag anomalies

## MODULE 9: Statutory Compliance
- PF ECR generation
- ESI return generation
- TDS 24Q generation
- **AI:** Prepare filing data

## MODULE 10: Chart of Accounts & GL
- Account hierarchy
- Journal entries
- Period closing
- **AI:** Suggest accounts

## MODULE 11: Multi-Currency
- Currency management
- RBI exchange rates
- Forex gain/loss

## MODULE 12: Customer Invoicing (AR)
- Customer master
- Invoice types
- GST calculation
- **AI:** Generate from NL

## MODULE 13: Vendor Bills (AP)
- Vendor master
- Bill with TDS
- **AI:** Extract from images

## MODULE 14: Banking & Reconciliation
- Bank accounts
- AI reconciliation
- **AI:** Auto-match

## MODULE 15: GST Compliance
- GSTR-1/3B generation
- HSN/SAC master
- **AI:** Validate

## MODULE 16: TDS Compliance
- Section tracking
- 26Q generation
- **AI:** Calculate thresholds

## MODULE 17: Financial Reports
- Trial Balance, P&L, Balance Sheet
- **AI:** Generate insights

## MODULE 18: CRM
- Lead management
- Pipeline (Kanban)
- **AI:** Score, draft emails

## MODULE 19: AI ERP Assistant
- Natural language queries
- Action execution
- Daily briefing

## MODULE 20: Project Management
- Projects, Milestones, Tasks
- Resource allocation
- T&M and Fixed Price billing
- **10-Phase Framework template**
- **AI:** Estimate, predict

## MODULE 21: CA Verification Portal
- External CA role
- Verification queue
- Correction interface

## MODULE 22: Compliance Tracker
- ROC, GST, TDS, PF calendars
- **AI:** Remind, prepare

## MODULE 23: Quotes & Assets
- Quote creation → Project/Invoice
- Asset registry
- Depreciation
- **AI:** Generate, track

---

# SECTION 6: INDIA COMPLIANCE (EXACT FORMULAS)

## 6.1 Provident Fund (PF)

### PF Wage Definition
```
PF_WAGE = BASIC + DEARNESS_ALLOWANCE (DA)
```

### Employee Contribution
```
EMPLOYEE_PF = PF_WAGE × 12%
```

### Employer Contribution
```
TOTAL_EMPLOYER = PF_WAGE × 12%

EPS (Employee Pension Scheme):
  IF PF_WAGE ≤ 15,000:
    EPS = PF_WAGE × 8.33%
  ELSE:
    EPS = 1,250 (CAPPED)

EPF (Employee Provident Fund):
  EPF = TOTAL_EMPLOYER - EPS
```

### Example Calculations
| PF Wage | Employee PF | Employer EPS | Employer EPF | Total Employer |
|---------|-------------|--------------|--------------|----------------|
| ₹12,000 | ₹1,440 | ₹1,000 | ₹440 | ₹1,440 |
| ₹15,000 | ₹1,800 | ₹1,250 | ₹550 | ₹1,800 |
| ₹25,000 | ₹3,000 | ₹1,250 | ₹1,750 | ₹3,000 |
| ₹50,000 | ₹6,000 | ₹1,250 | ₹4,750 | ₹6,000 |

### Filing
- **Form:** ECR (Electronic Challan cum Return)
- **Due Date:** 15th of following month
- **Portal:** EPFO Unified Portal

---

## 6.2 Employee State Insurance (ESI)

### Applicability
```
IF GROSS_SALARY ≤ 21,000:
  ESI_APPLICABLE = TRUE
ELSE:
  ESI_APPLICABLE = FALSE
```

### Contributions
```
EMPLOYEE_ESI = GROSS_SALARY × 0.75%
EMPLOYER_ESI = GROSS_SALARY × 3.25%
TOTAL_ESI = GROSS_SALARY × 4%
```

### Example Calculations
| Gross Salary | Applicable | Employee ESI | Employer ESI | Total |
|--------------|------------|--------------|--------------|-------|
| ₹15,000 | Yes | ₹113 | ₹488 | ₹600 |
| ₹21,000 | Yes | ₹158 | ₹683 | ₹840 |
| ₹25,000 | No | ₹0 | ₹0 | ₹0 |

### Filing
- **Due Date:** 15th of following month
- **Portal:** ESIC Portal

---

## 6.3 Professional Tax (Karnataka)

### Monthly Slabs
| Gross Salary | Monthly PT |
|--------------|------------|
| ≤ ₹15,000 | ₹0 |
| > ₹15,000 | ₹200 |

### February Adjustment
```
FEBRUARY_PT = ₹300 (includes annual adjustment)
ANNUAL_PT = (11 × 200) + 300 = ₹2,500
```

---

## 6.4 TDS (Tax Deducted at Source)

### New Tax Regime (Default from FY 2024-25)
| Income Slab | Tax Rate |
|-------------|----------|
| Up to ₹3,00,000 | 0% |
| ₹3,00,001 - ₹7,00,000 | 5% |
| ₹7,00,001 - ₹10,00,000 | 10% |
| ₹10,00,001 - ₹12,00,000 | 15% |
| ₹12,00,001 - ₹15,00,000 | 20% |
| Above ₹15,00,000 | 30% |

**Standard Deduction:** ₹75,000
**Health & Education Cess:** 4% on tax

### Old Tax Regime (Optional)
| Income Slab | Tax Rate |
|-------------|----------|
| Up to ₹2,50,000 | 0% |
| ₹2,50,001 - ₹5,00,000 | 5% |
| ₹5,00,001 - ₹10,00,000 | 20% |
| Above ₹10,00,000 | 30% |

### Calculation Formula
```
1. ANNUAL_INCOME = MONTHLY_GROSS × 12
2. TAXABLE_INCOME = ANNUAL_INCOME - STANDARD_DEDUCTION (if new regime)
3. TAX = Apply slab rates
4. TOTAL_TAX = TAX + (TAX × 4%)  // Add cess
5. MONTHLY_TDS = TOTAL_TAX ÷ 12
```

---

## 6.5 TDS on Vendor Payments

| Section | Type | Rate | Threshold |
|---------|------|------|-----------|
| 194C | Contractors (Individual/HUF) | 1% | ₹30,000 single / ₹1,00,000 annual |
| 194C | Contractors (Others) | 2% | ₹30,000 single / ₹1,00,000 annual |
| 194J | Professional/Technical | 10% | ₹30,000 annual |
| 194H | Commission/Brokerage | 5% | ₹15,000 annual |
| 194I | Rent (Machinery) | 2% | ₹2,40,000 annual |
| 194I | Rent (Property) | 10% | ₹2,40,000 annual |

---

## 6.6 GST (Goods and Services Tax)

### Tax Rates
```
SAME STATE (Intra-state):
  CGST = 9%
  SGST = 9%
  TOTAL = 18%

DIFFERENT STATE (Inter-state):
  IGST = 18%
```

### IT Services SAC Codes
| SAC Code | Description |
|----------|-------------|
| 998311 | Management consulting |
| 998312 | Business consulting |
| 998313 | IT consulting |
| 998314 | IT design and development |
| 998315 | IT infrastructure management |
| 998316 | IT technical support |
| 998319 | Other IT services |

### GSTR-1 (Outward Supplies)
- **Due Date:** 11th of following month
- **Sections:** B2B, B2CL, B2CS, Exports, Credit/Debit Notes, HSN Summary

### GSTR-3B (Summary Return)
- **Due Date:** 20th of following month
- **Sections:** Outward supplies, Inter-state supplies, ITC, Exempt supplies, Tax payment

---

# SECTION 7: DATABASE SCHEMA (~120 TABLES)

## By Module

### Auth (3 tables)
- users
- user_sessions
- user_audit_log

### Organization (6 tables)
- company_profile
- company_statutory
- company_bank_accounts
- authorized_signatories
- departments
- designations

### Employees (9 tables)
- employees
- employee_contact
- employee_identity
- employee_bank
- employee_employment
- employee_documents
- employee_education
- employee_previous_employment
- onboarding_progress

### EDMS (4 tables)
- folders
- folder_permissions
- documents
- document_versions

### Leave (4 tables)
- leave_types
- holidays
- leave_balances
- leave_requests

### Timesheet (2 tables)
- timesheets
- timesheet_entries

### Payroll (12 tables)
- salary_components
- employee_salary
- employee_salary_components
- tax_declarations
- tax_declaration_items
- payroll_runs
- payslips
- payslip_components
- pf_monthly_data
- esi_monthly_data
- tds_monthly_data
- pt_data

### Statutory (5 tables)
- statutory_settings
- pf_ecr_files
- esi_return_files
- tds_24q_files
- form16_data

### Accounting (10 tables)
- account_groups
- accounts
- accounting_periods
- currencies
- exchange_rates
- journal_entries
- journal_entry_lines
- recurring_entries
- fiscal_years
- period_close_status

### AR (6 tables)
- customers
- invoices
- invoice_line_items
- receipts
- receipt_allocations
- lut_records

### AP (6 tables)
- vendors
- bills
- bill_line_items
- payments
- payment_allocations
- tds_payments

### Banking (5 tables)
- bank_accounts
- bank_transactions
- bank_statements
- bank_statement_lines
- petty_cash_entries

### GST (4 tables)
- hsn_sac_codes
- gst_returns
- gstr1_data
- gstr3b_data

### TDS (3 tables)
- tds_sections
- tds_entries
- tds_certificates

### CRM (3 tables)
- leads
- lead_activities
- lead_scores

### Projects (7 tables)
- projects
- milestones
- tasks
- task_assignments
- resource_allocations
- project_billings
- wbs_templates

### AI (6 tables)
- ai_providers
- ai_requests
- ai_corrections
- ai_confidence_rules
- transaction_patterns
- ai_processing_queue

### CA Portal (2 tables)
- ca_firms
- verification_queue

### Compliance (3 tables)
- compliance_categories
- compliance_items
- compliance_tracker

### Quotes & Assets (6 tables)
- quotes
- quote_line_items
- quote_versions
- assets
- asset_assignments
- asset_depreciation

---

# SECTION 8: API ENDPOINTS (~250)

## Authentication (7)
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh
- POST /api/v1/auth/logout
- GET /api/v1/auth/me
- POST /api/v1/auth/change-password
- POST /api/v1/auth/forgot-password
- POST /api/v1/auth/reset-password

## Users (5)
- GET /api/v1/users
- POST /api/v1/users
- GET /api/v1/users/{id}
- PUT /api/v1/users/{id}
- DELETE /api/v1/users/{id}

## Employees (12)
- GET /api/v1/employees
- POST /api/v1/employees
- GET /api/v1/employees/{id}
- PUT /api/v1/employees/{id}
- GET /api/v1/employees/{id}/documents
- POST /api/v1/employees/{id}/documents
- GET /api/v1/employees/{id}/salary
- PUT /api/v1/employees/{id}/salary
- GET /api/v1/employees/{id}/payslips
- GET /api/v1/employees/{id}/leave-balance
- GET /api/v1/employees/{id}/tax-declaration
- PUT /api/v1/employees/{id}/tax-declaration

## Departments & Designations (8)
- CRUD for departments (4)
- CRUD for designations (4)

## Documents (8)
- Folders CRUD (4)
- Documents CRUD (4)

## Leave (10)
- Leave types CRUD (4)
- Holidays CRUD (4)
- POST /api/v1/leave/request
- PUT /api/v1/leave/request/{id}/approve

## Timesheet (6)
- GET /api/v1/timesheets
- POST /api/v1/timesheets
- GET /api/v1/timesheets/{id}
- PUT /api/v1/timesheets/{id}
- POST /api/v1/timesheets/{id}/submit
- PUT /api/v1/timesheets/{id}/approve

## Payroll (15)
- Salary components CRUD (4)
- POST /api/v1/payroll/run
- GET /api/v1/payroll/runs
- GET /api/v1/payroll/runs/{id}
- POST /api/v1/payroll/runs/{id}/finalize
- GET /api/v1/payslips
- GET /api/v1/payslips/{id}
- GET /api/v1/payslips/{id}/pdf
- GET /api/v1/payroll/pf-breakdown/{employee_id}/{month}/{year}
- GET /api/v1/payroll/esi-breakdown/{employee_id}/{month}/{year}
- GET /api/v1/payroll/tds-breakdown/{employee_id}/{month}/{year}

## Statutory (8)
- GET /api/v1/statutory/pf/ecr/{month}/{year}
- POST /api/v1/statutory/pf/ecr/generate
- GET /api/v1/statutory/esi/return/{month}/{year}
- POST /api/v1/statutory/esi/return/generate
- GET /api/v1/statutory/tds/24q/{quarter}/{year}
- POST /api/v1/statutory/tds/24q/generate
- GET /api/v1/statutory/form16/{employee_id}/{year}
- POST /api/v1/statutory/form16/generate

## Accounting (20)
- Account groups CRUD (4)
- Accounts CRUD (4)
- Journal entries CRUD (4)
- GET /api/v1/accounting/trial-balance
- GET /api/v1/accounting/profit-loss
- GET /api/v1/accounting/balance-sheet
- POST /api/v1/accounting/period/close
- GET /api/v1/accounting/ledger/{account_id}

## Customers & Invoices (15)
- Customers CRUD (4)
- Invoices CRUD (4)
- GET /api/v1/invoices/{id}/pdf
- POST /api/v1/invoices/{id}/send
- Receipts CRUD (4)
- POST /api/v1/receipts/{id}/allocate

## Vendors & Bills (15)
- Vendors CRUD (4)
- Bills CRUD (4)
- POST /api/v1/bills/extract (AI)
- Payments CRUD (4)
- POST /api/v1/payments/{id}/allocate
- GET /api/v1/vendors/{id}/tds-summary

## Banking (12)
- Bank accounts CRUD (4)
- GET /api/v1/banking/transactions
- POST /api/v1/banking/transactions
- POST /api/v1/banking/statement/upload
- GET /api/v1/banking/reconciliation
- POST /api/v1/banking/reconciliation/match
- POST /api/v1/banking/reconciliation/auto (AI)
- GET /api/v1/banking/petty-cash

## GST (10)
- HSN/SAC codes CRUD (4)
- GET /api/v1/gst/gstr1/{month}/{year}
- POST /api/v1/gst/gstr1/generate
- GET /api/v1/gst/gstr3b/{month}/{year}
- POST /api/v1/gst/gstr3b/generate
- GET /api/v1/gst/summary/{month}/{year}
- POST /api/v1/gst/validate

## TDS (8)
- TDS sections CRUD (4)
- GET /api/v1/tds/entries
- POST /api/v1/tds/entries
- GET /api/v1/tds/26q/{quarter}/{year}
- POST /api/v1/tds/certificates/generate

## CRM (10)
- Leads CRUD (4)
- GET /api/v1/crm/pipeline
- POST /api/v1/crm/leads/{id}/activities
- GET /api/v1/crm/leads/{id}/score (AI)
- POST /api/v1/crm/leads/{id}/email/draft (AI)
- PUT /api/v1/crm/leads/{id}/stage
- GET /api/v1/crm/analytics

## Projects (15)
- Projects CRUD (4)
- Milestones CRUD (4)
- Tasks CRUD (4)
- POST /api/v1/projects/{id}/estimate (AI)
- GET /api/v1/projects/{id}/health
- POST /api/v1/projects/template/10-phase

## AI Assistant (8)
- POST /api/v1/ai/query
- POST /api/v1/ai/extract
- POST /api/v1/ai/categorize
- GET /api/v1/ai/queue
- PUT /api/v1/ai/queue/{id}/approve
- PUT /api/v1/ai/queue/{id}/reject
- GET /api/v1/ai/briefing
- POST /api/v1/ai/action

## Quotes & Assets (12)
- Quotes CRUD (4)
- POST /api/v1/quotes/{id}/convert
- Assets CRUD (4)
- GET /api/v1/assets/{id}/depreciation
- POST /api/v1/assets/{id}/assign
- GET /api/v1/assets/report

## Reports (10)
- GET /api/v1/reports/dashboard
- GET /api/v1/reports/trial-balance
- GET /api/v1/reports/profit-loss
- GET /api/v1/reports/balance-sheet
- GET /api/v1/reports/cash-flow
- GET /api/v1/reports/gst-summary
- GET /api/v1/reports/tds-summary
- GET /api/v1/reports/payroll-summary
- GET /api/v1/reports/employee-cost
- POST /api/v1/reports/custom (AI)

## Compliance (6)
- GET /api/v1/compliance/calendar
- GET /api/v1/compliance/upcoming
- POST /api/v1/compliance/mark-complete
- GET /api/v1/compliance/status
- POST /api/v1/compliance/remind
- GET /api/v1/compliance/history

---

# SECTION 9: FRONTEND SCREENS (~60)

## Authentication (3)
- Login page
- Forgot password
- Reset password

## Dashboard (5)
- Admin dashboard
- HR dashboard
- Accountant dashboard
- Employee dashboard
- CA dashboard

## Employees (8)
- Employee list
- Employee detail
- Employee create/edit form
- Document upload
- Onboarding wizard
- Profile view (self)
- Tax declaration form
- Salary structure

## Leave (5)
- Leave dashboard
- Leave calendar
- Leave request form
- Leave approval queue
- Leave balance view

## Timesheet (3)
- Timesheet grid
- Timesheet approval
- Time reports

## Payroll (6)
- Payroll dashboard
- Run payroll
- Payslip list
- Payslip detail/PDF
- Salary components config
- Form 16 download

## Statutory (4)
- PF ECR generation
- ESI returns
- TDS returns
- Compliance calendar

## Accounting (6)
- Chart of accounts
- Journal entry form
- Journal list
- Trial balance
- P&L statement
- Balance sheet

## AR - Invoicing (5)
- Customer list
- Customer form
- Invoice list
- Invoice form
- Receipt form

## AP - Bills (5)
- Vendor list
- Vendor form
- Bill list
- Bill form (with AI extract)
- Payment form

## Banking (4)
- Bank accounts
- Transactions list
- Reconciliation screen
- Statement upload

## GST (3)
- GSTR-1 view
- GSTR-3B view
- HSN/SAC master

## CRM (4)
- Lead pipeline (Kanban)
- Lead detail
- Lead form
- CRM reports

## Projects (5)
- Project list
- Project detail
- Task board (Kanban)
- Resource allocation
- Project billing

## Settings (4)
- Company settings
- User management
- Statutory settings
- System preferences

---

# SECTION 10: 10-PHASE FRAMEWORK TEMPLATE

Available as project template in Project Management module:

## Phase 1: Discovery & Planning
- Stakeholder analysis
- Requirements gathering
- Scope definition
- Risk assessment
- **Gate G1:** Requirements approved

## Phase 2: Design
- System architecture
- Database design
- API contracts
- UI/UX wireframes
- **Gate G2:** Design approved

## Phase 3: Infrastructure Setup
- Development environment
- CI/CD pipeline
- Database setup
- Monitoring setup
- **Gate G3:** Environment ready

## Phase 4: Backend Development
- Core APIs
- Business logic
- Database models
- Unit tests
- **Gate G4:** Backend complete

## Phase 5: Frontend Development
- UI components
- Page layouts
- API integration
- Unit tests
- **Gate G5:** Frontend complete

## Phase 6: Integration & Testing
- Integration tests
- E2E tests
- Performance tests
- Bug fixes
- **Gate G6:** Testing complete

## Phase 7: Security & Compliance
- Security audit
- Vulnerability fixes
- Compliance verification
- Documentation
- **Gate G7:** Security approved

## Phase 8: Deployment & Launch
- Production deployment
- DNS configuration
- SSL setup
- Go-live
- **Gate G8:** Live and stable

## Phase 9: Operations & Maintenance
- Monitoring
- Bug fixes
- Updates
- Support

## Phase 10: Value Realization
- KPI tracking
- User feedback
- Continuous improvement
- Feature requests

---

# SECTION 11: TASK EXECUTION ORDER

```
PHASE 1: Infrastructure (Tasks 1-50)
  └── Docker, PostgreSQL, Redis, Nginx, CI/CD

PHASE 2: Authentication & Users (Tasks 51-100)
  └── JWT, RBAC, User CRUD

PHASE 3: Employee & HRMS (Tasks 101-180)
  └── Employee CRUD, Documents, Onboarding

PHASE 4: Leave & Timesheet (Tasks 181-250)
  └── Leave types, Requests, Approvals, Timesheets

PHASE 5: Payroll & Statutory (Tasks 251-400)
  └── Salary, PF, ESI, TDS, PT, Payslips, ECR, Form 16

PHASE 6: Accounting Core (Tasks 401-500)
  └── COA, GL, Journal Entries, Currencies

PHASE 7: AR & AP (Tasks 501-600)
  └── Customers, Invoices, Vendors, Bills, Payments

PHASE 8: Banking & Reconciliation (Tasks 601-680)
  └── Bank Accounts, Transactions, Auto-Reconciliation

PHASE 9: GST & TDS Compliance (Tasks 681-750)
  └── GSTR-1, GSTR-3B, TDS Returns

PHASE 10: CRM & Projects (Tasks 751-820)
  └── Leads, Pipeline, Projects, Tasks

PHASE 11: AI Integration (Tasks 821-870)
  └── Document Processing, Categorization, NL Queries

PHASE 12: Frontend (Tasks 871-920)
  └── All 60 screens

PHASE 13: Testing & QA (Tasks 921-970)
  └── Unit, Integration, E2E, Compliance Tests

PHASE 14: Security & Deployment (Tasks 971-899)
  └── Security Audit, Production Deploy, Go-Live
```

---

# SECTION 12: ACCEPTANCE CRITERIA

## Individual Task Done
- [ ] Code written and functional
- [ ] Unit tests passing
- [ ] No linting errors
- [ ] API documentation updated
- [ ] PROGRESS.md updated

## Module Complete
- [ ] All tasks in module done
- [ ] Integration tests passing
- [ ] UI connected to backend
- [ ] Edge cases handled

## Project Complete
- [ ] All 899 tasks completed
- [ ] All 250 endpoints working
- [ ] All 60 screens functional
- [ ] All AI features operational
- [ ] Test coverage ≥80% backend, ≥60% frontend
- [ ] Performance: API <500ms
- [ ] Security audit passed
- [ ] India compliance verified
- [ ] portal.ganakys.com accessible

---

# SECTION 13: QUALITY GATES

| Gate | Phase | Criteria |
|------|-------|----------|
| G1 | Requirements | All 23 modules analyzed, compliance formulas extracted |
| G2 | WBS | All tasks 4-8 hours, dependencies mapped |
| G3 | Architecture | ~120 tables designed, ~250 endpoints specified |
| G4 | Infrastructure | Docker running, DB connected, CI/CD working |
| G5 | Backend | All APIs responding, test coverage ≥80% |
| G6 | Frontend | All ~60 screens working, responsive |
| G7 | AI | AI service operational, fallback chain working |
| G8 | Testing | No critical bugs, all compliance tests pass |
| G9 | Security | No vulnerabilities, India compliance verified |
| G10 | Deployment | portal.ganakys.com accessible, health checks pass |

---

*END OF FINAL CONSOLIDATED REQUIREMENTS v3.0*
