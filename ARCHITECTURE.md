# Ganakys Codilla Apps - Architecture Document
## AI-First ERP for Indian Start-ups

---

# PART 1: AS-IS ARCHITECTURE ANALYSIS

## Executive Summary

GanaPortal is currently a comprehensive, monolithic ERP system built with modern technologies. It has strong foundations for Indian compliance and AI integration, but requires architectural enhancements to become a true multi-tenant SaaS platform.

---

## 1. Current Technology Stack

### Backend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | FastAPI | 0.109.2 |
| Language | Python | 3.11+ |
| Database | PostgreSQL | 14+ |
| ORM | SQLAlchemy (Async) | 2.0.25 |
| Cache/Queue | Redis | 5.0+ |
| Task Queue | Celery | 5.3.6 |
| Server | Uvicorn/Gunicorn | 0.27.1 |

### Frontend
| Component | Technology | Version |
|-----------|------------|---------|
| Framework | Next.js (App Router) | 14.1.0 |
| Language | TypeScript | 5.3.3 |
| UI Library | Radix UI + Tailwind | Latest |
| State | Zustand + React Query | 4.5.0 / 5.17.19 |
| Forms | React Hook Form + Zod | 7.49.3 |

### AI Integration
| Provider | Model | Priority |
|----------|-------|----------|
| Anthropic | Claude 3.5 Sonnet | Primary |
| Google | Gemini 1.5 Pro | Fallback 1 |
| OpenAI | GPT-4 Turbo | Fallback 2 |
| Together AI | Llama 3 70B | Fallback 3 |

---

## 2. Current Module Inventory

### Fully Implemented (Production Ready)
- [x] Employee Management (27+ fields, full lifecycle)
- [x] Payroll Processing (Indian statutory compliance)
- [x] Leave Management (8 leave types, policies)
- [x] Attendance Tracking (Geo-fencing, biometric)
- [x] PF/ESI/PT/TDS Compliance (Full Indian compliance)
- [x] GST Compliance (GSTR-1, GSTR-2A, GSTR-3B)
- [x] Invoicing & Billing (AR/AP)
- [x] Chart of Accounts (Double-entry)
- [x] Bank Reconciliation
- [x] CRM (Leads, Opportunities, Customers)
- [x] Document Management
- [x] AI Assistant (Multi-provider fallback)
- [x] AI Org Builder (Department/Designation generation)
- [x] User Management (RBAC with 8 roles)
- [x] Audit Logging (Complete trail)

### Partially Implemented
- [ ] Project Management (Basic)
- [ ] Recruitment (Job posting only)
- [ ] Onboarding (Templates exist)
- [ ] Exit Management (Basic)
- [ ] Performance Management (Placeholder)
- [ ] Training (Placeholder)

### Not Implemented
- [ ] Inventory/Stock Management
- [ ] Purchase Orders & Procurement
- [ ] Fixed Assets & Depreciation
- [ ] Multi-Currency Accounting
- [ ] Expense Management
- [ ] Subscription & Billing (for SaaS)
- [ ] Super Admin Portal (Ganakys management)
- [ ] Tenant Provisioning (Auto onboarding)
- [ ] Usage Analytics & Metering
- [ ] White-labeling

---

## 3. Current Database Schema

### Statistics
| Metric | Value |
|--------|-------|
| Total Tables | 154 |
| Multi-tenant Tables | 95+ |
| Tenant Key | company_id (UUID) |
| Soft Delete | deleted_at column |
| Audit Fields | created_by, updated_by |

### Table Categories
```
Company & Org:       3 tables
Employee & HR:      20+ tables
Payroll:            15+ tables
Leave & Attendance: 12 tables
Accounting:         18+ tables
Tax Compliance:     25+ tables
CRM:                15+ tables
Projects:           10 tables
Documents:           6 tables
AI/Automation:       5 tables
```

---

## 4. Current Architecture Strengths

1. **Modern Async Stack**: Full async/await with asyncpg
2. **Strong Type Safety**: MyPy strict mode, TypeScript strict
3. **India Compliance Built-in**: PF, ESI, PT, TDS, GST
4. **AI-First Foundation**: Multi-provider with fallback chain
5. **Multi-tenancy Base**: company_id isolation exists
6. **Comprehensive Security**: JWT, RBAC, encryption, audit
7. **Good Test Coverage**: Unit, integration, E2E tests

---

## 5. Current Architecture Weaknesses

### Critical for SaaS
1. **No Subscription Management**: No billing, plans, or metering
2. **No Super Admin Portal**: Ganakys cannot manage tenants
3. **No Self-Service Onboarding**: Manual tenant creation
4. **Single Database**: No database-per-tenant option
5. **No Usage Tracking**: Cannot meter AI or API usage

### Technical Debt
1. **Monolithic Architecture**: All modules in single codebase
2. **In-Memory Rate Limiting**: Lost on restart
3. **Token Blacklist In-Memory**: Not distributed
4. **No Caching Strategy**: Missing Redis caching layer
5. **Custom Encryption**: Should use standard library
6. **No API Versioning Strategy**: Only v1 exists

### Missing Features
1. **No Inventory Management**: Critical for product startups
2. **No Purchase Order Workflow**: Only bills exist
3. **No Fixed Assets**: Depreciation not tracked
4. **No Expense Management**: Employee expenses
5. **No Multi-Currency**: Only INR supported
6. **No Workflow Engine**: Ad-hoc approvals only

---

# PART 2: TO-BE ARCHITECTURE

## Vision

**Ganakys Codilla Apps** will be India's first AI-First ERP SaaS platform, purpose-built for startups across all industries. The platform will enable:

1. **Zero-Touch Onboarding**: Companies sign up and start using immediately
2. **AI-Powered Everything**: From data entry to insights to automation
3. **Complete Compliance**: PF, ESI, PT, TDS, GST, MCA out of the box
4. **Industry Agnostic**: Works for SaaS, FinTech, EdTech, D2C, Manufacturing
5. **Ganakys Control**: Full visibility and management of all tenants

---

## 1. Target Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           GANAKYS CONTROL PLANE                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Super Admin  │  │  Billing &   │  │   Tenant     │  │  Analytics   │    │
│  │   Portal     │  │ Subscription │  │ Provisioning │  │  Dashboard   │    │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                              ┌───────┴───────┐
                              │   API Gateway │
                              │  (Kong/AWS)   │
                              └───────┬───────┘
                                      │
        ┌─────────────────────────────┼─────────────────────────────┐
        │                             │                             │
┌───────┴───────┐           ┌────────┴────────┐           ┌────────┴────────┐
│   CORE ERP    │           │   AI SERVICES   │           │  COMPLIANCE     │
│   Services    │           │   (Dedicated)   │           │   Services      │
├───────────────┤           ├─────────────────┤           ├─────────────────┤
│ • Auth        │           │ • AI Gateway    │           │ • PF Service    │
│ • Employee    │           │ • Doc Processor │           │ • ESI Service   │
│ • Payroll     │           │ • Chat Engine   │           │ • GST Service   │
│ • Leave       │           │ • Org Builder   │           │ • TDS Service   │
│ • Attendance  │           │ • Report Gen    │           │ • MCA Service   │
│ • Accounting  │           │ • Anomaly Det   │           │ • ROC Service   │
│ • Invoicing   │           └─────────────────┘           └─────────────────┘
│ • CRM         │
│ • Projects    │
│ • Inventory   │  ←── NEW
│ • Procurement │  ←── NEW
│ • Assets      │  ←── NEW
│ • Expenses    │  ←── NEW
└───────────────┘
        │
┌───────┴───────────────────────────────────────────────────────────┐
│                         DATA LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  PostgreSQL  │  │    Redis     │  │ Elasticsearch│            │
│  │  (Primary)   │  │   (Cache)    │  │  (Search)    │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │     S3       │  │   ClickHouse │  │   TimescaleDB│            │
│  │  (Documents) │  │  (Analytics) │  │  (Timeseries)│            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└───────────────────────────────────────────────────────────────────┘
```

---

## 2. Multi-Tenancy Architecture

### Shared Infrastructure Model

All tenants share the same infrastructure with logical isolation. This keeps costs low and enables the generous free tier for startups.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TENANT ISOLATION STRATEGY                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ALL TENANTS (Monthly & Annual Plans)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                                                          │   │
│  │  DATABASE ISOLATION                                      │   │
│  │  • Shared PostgreSQL instance                            │   │
│  │  • Row-level isolation via company_id                    │   │
│  │  • All queries filtered by tenant                        │   │
│  │  • Connection pooling per tenant                         │   │
│  │                                                          │   │
│  │  CACHE ISOLATION                                         │   │
│  │  • Shared Redis cluster                                  │   │
│  │  • Namespace prefixing: tenant:{company_id}:*            │   │
│  │  • Separate rate limit buckets per tenant                │   │
│  │                                                          │   │
│  │  STORAGE ISOLATION                                       │   │
│  │  • Shared S3 bucket                                      │   │
│  │  • Folder isolation: /companies/{company_id}/*           │   │
│  │  • Pre-signed URLs with tenant validation                │   │
│  │                                                          │   │
│  │  AI/API LIMITS (Based on Employee Count)                 │   │
│  │  • Monthly: 1,000 AI queries per employee                │   │
│  │  • Annual: 1,500 AI queries per employee (50% bonus)     │   │
│  │  • Storage: 2-3 GB per employee                          │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  FUTURE: ENTERPRISE ADD-ONS (Optional paid features)            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Dedicated database instance (+₹10,000/month)          │   │
│  │  • Custom domain/white-label (+₹5,000/month)             │   │
│  │  • SSO/SAML integration (+₹5,000/month)                  │   │
│  │  • SLA guarantee (+₹10,000/month)                        │   │
│  │  • Priority support (+₹5,000/month)                      │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Tenant Resource Scaling

| Employee Count | AI Queries/Month | Storage | API Rate Limit |
|----------------|------------------|---------|----------------|
| 1-10 | 10,000-15,000 | 20-30 GB | 100 req/min |
| 11-50 | 50,000-75,000 | 100-150 GB | 500 req/min |
| 51-100 | 100,000-150,000 | 200-300 GB | 1,000 req/min |
| 100+ | Scales linearly | Scales linearly | 2,000 req/min |

---

## 3. Subscription & Billing System

### Plan Structure

Ganakys Codilla Apps uses a simple, employee-based pricing model designed to support Indian startups from day one.

```yaml
plans:
  monthly:
    name: "Monthly Plan"
    billing_cycle: monthly
    pricing:
      first_year:
        free_employees: 10           # First 10 employees FREE for 1 year
        additional_employee: 1000    # ₹1,000/employee/month from 11th employee
      after_first_year:
        per_employee: 1000           # ₹1,000/employee/month for ALL employees
    features:
      - all_modules_included         # Full access to all ERP modules
      - unlimited_users              # No user seat limits
      - ai_queries: 1000/employee/month
      - storage_gb: 2/employee
      - api_access: true
      - support: email_chat

  annual:
    name: "Annual Plan"
    billing_cycle: annual
    pricing:
      first_year:
        free_employees: 10           # First 10 employees FREE for 1 year
        additional_employee: 10000   # ₹10,000/employee/year from 11th employee
      after_first_year:
        per_employee: 10000          # ₹10,000/employee/year for ALL employees
    discount: 2000/employee/year     # Save ₹2,000/employee vs monthly
    features:
      - all_modules_included
      - unlimited_users
      - ai_queries: 1500/employee/month  # 50% more AI queries
      - storage_gb: 3/employee           # 50% more storage
      - api_access: true
      - priority_support: true
      - dedicated_account_manager: 50+ employees
```

### Pricing Examples

| Scenario | Monthly Plan | Annual Plan | Annual Savings |
|----------|--------------|-------------|----------------|
| 5 employees, Year 1 | FREE | FREE | - |
| 10 employees, Year 1 | FREE | FREE | - |
| 15 employees, Year 1 | ₹5,000/mo (5 × ₹1,000) | ₹50,000/yr | ₹10,000 |
| 25 employees, Year 1 | ₹15,000/mo (15 × ₹1,000) | ₹1,50,000/yr | ₹30,000 |
| 10 employees, Year 2+ | ₹10,000/mo | ₹1,00,000/yr | ₹20,000 |
| 50 employees, Year 2+ | ₹50,000/mo | ₹5,00,000/yr | ₹1,00,000 |

### Free Trial Logic

```
┌─────────────────────────────────────────────────────────────────┐
│                    SUBSCRIPTION FLOW                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  NEW COMPANY SIGNUP                                              │
│  • Automatically starts on Monthly Plan                          │
│  • First 10 employees FREE for 1 year                           │
│  • No credit card required initially                            │
└─────────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                                   ▼
┌───────────────────────┐           ┌───────────────────────┐
│  STAYS ≤10 EMPLOYEES  │           │  ADDS 11TH EMPLOYEE   │
│  • FREE for 1 year    │           │  • Payment required   │
│  • Full features      │           │  • ₹1,000/mo per      │
│  • After Year 1:      │           │    employee above 10  │
│    ₹10,000/mo total   │           │  • Can switch to      │
│                       │           │    Annual for savings │
└───────────────────────┘           └───────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  YEAR 1 ANNIVERSARY                                              │
│  • All employees become billable                                 │
│  • ₹1,000/employee/month (Monthly) or                           │
│  • ₹10,000/employee/year (Annual)                               │
│  • 30-day grace period with reminders                           │
└─────────────────────────────────────────────────────────────────┘
```

### Billing Database Schema

```sql
-- Simplified subscription management for employee-based pricing
CREATE TABLE company_subscriptions (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id) UNIQUE,
    billing_cycle VARCHAR(10) NOT NULL, -- 'monthly' or 'annual'
    status VARCHAR(20) DEFAULT 'active', -- active, suspended, cancelled
    signup_date DATE NOT NULL,           -- When company signed up (for Year 1 calculation)
    free_period_ends DATE,               -- signup_date + 1 year
    is_in_free_period BOOLEAN GENERATED ALWAYS AS (CURRENT_DATE < free_period_ends) STORED,
    current_period_start DATE,
    current_period_end DATE,
    next_billing_date DATE,
    cancelled_at TIMESTAMP,
    cancel_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Track billable employee count history
CREATE TABLE employee_count_snapshots (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    snapshot_date DATE NOT NULL,
    total_employees INT NOT NULL,        -- Total active employees
    billable_employees INT NOT NULL,     -- Employees above free tier (if in Year 1) or all (after Year 1)
    employee_breakdown JSONB,            -- {"permanent": 10, "contract": 5, "temporary": 2, ...}
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, snapshot_date)
);

CREATE TABLE subscription_invoices (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    invoice_number VARCHAR(50) UNIQUE,
    billing_period_start DATE,
    billing_period_end DATE,
    employee_count INT,                  -- Billable employees for this period
    rate_per_employee DECIMAL(10,2),     -- ₹1,000 (monthly) or ₹10,000 (annual)
    subtotal DECIMAL(10,2),
    gst_rate DECIMAL(5,2) DEFAULT 18.00,
    gst_amount DECIMAL(10,2),
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending', -- pending, paid, failed, refunded
    due_date DATE,
    paid_at TIMESTAMP,
    payment_method VARCHAR(50),
    razorpay_payment_id VARCHAR(100),
    razorpay_order_id VARCHAR(100),
    invoice_pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE payment_methods (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    provider VARCHAR(20) DEFAULT 'razorpay',
    razorpay_customer_id VARCHAR(100),
    razorpay_token_id VARCHAR(100),      -- For recurring payments
    card_last_four VARCHAR(4),
    card_brand VARCHAR(20),
    card_expiry VARCHAR(7),              -- MM/YYYY
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Usage tracking for AI and storage limits
CREATE TABLE usage_metrics (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    metric_type VARCHAR(50), -- ai_queries, storage_bytes, api_calls
    metric_date DATE,
    metric_value BIGINT,
    limit_value BIGINT,                  -- Based on employee count
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, metric_type, metric_date)
);

-- Billing calculation function
-- Monthly: billable_employees × ₹1,000
-- Annual: billable_employees × ₹10,000
-- Year 1: Only employees > 10 are billable
-- After Year 1: All employees are billable
```

---

## 4. Employee & Staff Type Management

The ERP must support diverse workforce compositions common in Indian startups. All staff types are treated as "employees" for billing purposes.

### Staff Types Supported

```yaml
staff_types:
  permanent:
    code: "PERM"
    name: "Permanent Employee"
    description: "Full-time employees on company payroll"
    statutory_compliance:
      pf: required          # If salary > ₹15,000 threshold
      esi: required         # If salary ≤ ₹21,000
      pt: required          # Based on state
      tds: required
      gratuity: eligible    # After 5 years
    leave_eligible: true
    payroll_processed: true
    benefits_eligible: true

  probation:
    code: "PROB"
    name: "Probationary Employee"
    description: "New hires under probation period (typically 3-6 months)"
    statutory_compliance:
      pf: required
      esi: required
      pt: required
      tds: required
      gratuity: not_eligible  # Until confirmed
    leave_eligible: true      # Prorated
    payroll_processed: true
    benefits_eligible: partial
    auto_convert_to: permanent  # After probation period

  contract:
    code: "CONT"
    name: "Contract Employee"
    description: "Fixed-term contract employees"
    statutory_compliance:
      pf: optional          # Based on contract terms
      esi: optional
      pt: required
      tds: required
      gratuity: not_eligible
    contract_details:
      - start_date
      - end_date
      - renewal_terms
      - notice_period
    leave_eligible: as_per_contract
    payroll_processed: true
    benefits_eligible: as_per_contract

  temporary:
    code: "TEMP"
    name: "Temporary Staff"
    description: "Short-term hires for specific projects or peak periods"
    statutory_compliance:
      pf: not_required
      esi: not_required
      pt: required
      tds: required
    max_duration: 240_days   # Before conversion required
    leave_eligible: false
    payroll_processed: true
    benefits_eligible: false

  consultant:
    code: "CONS"
    name: "Consultant/Freelancer"
    description: "Independent contractors providing specialized services"
    statutory_compliance:
      pf: not_applicable
      esi: not_applicable
      pt: not_applicable
      tds: required          # Section 194J (10%)
    payment_type: invoice_based
    leave_eligible: false
    payroll_processed: false  # Paid via vendor/consultant bills
    benefits_eligible: false

  intern:
    code: "INTN"
    name: "Intern/Trainee"
    description: "Students or fresh graduates on internship"
    statutory_compliance:
      pf: not_required       # Stipend-based
      esi: not_required
      pt: not_required
      tds: conditional       # If stipend > tax threshold
    stipend_based: true
    max_duration: 6_months
    leave_eligible: limited
    payroll_processed: true
    benefits_eligible: false
    certificate_on_completion: true

  apprentice:
    code: "APPR"
    name: "Apprentice"
    description: "Under Apprenticeship Act training"
    statutory_compliance:
      pf: not_required
      esi: not_required
      pt: not_required
      tds: not_required      # Stipend exempt
    governed_by: "Apprenticeship Act 1961"
    leave_eligible: as_per_act
    payroll_processed: true
    benefits_eligible: false
```

### Work Arrangement Types

```yaml
work_arrangements:
  onsite:
    code: "ONS"
    name: "On-Site/Office"
    description: "Works from company office premises"
    attendance_tracking: biometric_or_manual
    location_tracking: false
    equipment_provided: office_equipment

  remote:
    code: "REM"
    name: "Remote/Work From Home"
    description: "Works entirely from home or remote location"
    attendance_tracking: login_based
    location_tracking: optional
    equipment_provided: laptop_internet_allowance
    policies:
      - remote_work_agreement
      - data_security_policy
      - communication_guidelines

  hybrid:
    code: "HYB"
    name: "Hybrid"
    description: "Mix of office and remote work"
    attendance_tracking: mixed
    hybrid_schedule:
      - fixed_days        # e.g., Mon-Wed office, Thu-Fri remote
      - flexible_days     # X days in office per week/month
      - team_sync_days    # Specific team days
    location_tracking: when_remote

  field:
    code: "FLD"
    name: "Field/Outdoor"
    description: "Works primarily in field (sales, service, delivery)"
    attendance_tracking: geo_fencing
    location_tracking: required
    expense_claims: frequent
    travel_allowance: applicable

  client_site:
    code: "CLI"
    name: "Client Site/Deputation"
    description: "Deployed at client location"
    attendance_tracking: client_system_or_self
    client_details:
      - client_name
      - deployment_start
      - deployment_end
      - billing_rate
    expense_claims: as_per_policy
```

### Database Schema for Staff Types

```sql
-- Employment types master
CREATE TABLE employment_types (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    is_system_defined BOOLEAN DEFAULT FALSE,  -- TRUE for default types
    pf_applicable BOOLEAN DEFAULT TRUE,
    esi_applicable BOOLEAN DEFAULT TRUE,
    pt_applicable BOOLEAN DEFAULT TRUE,
    gratuity_eligible BOOLEAN DEFAULT TRUE,
    leave_eligible BOOLEAN DEFAULT TRUE,
    payroll_processed BOOLEAN DEFAULT TRUE,   -- FALSE for consultants
    is_billable BOOLEAN DEFAULT TRUE,         -- Counts for subscription billing
    max_duration_days INT,                    -- NULL for permanent
    auto_convert_to_type_id UUID,             -- For probation → permanent
    statutory_rules JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, code)
);

-- Work arrangements master
CREATE TABLE work_arrangements (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    attendance_method VARCHAR(20),  -- biometric, login, geo_fence, manual
    location_tracking BOOLEAN DEFAULT FALSE,
    hybrid_config JSONB,            -- For hybrid arrangements
    policies JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, code)
);

-- Employee assignment (extends existing employees table)
ALTER TABLE employees ADD COLUMN IF NOT EXISTS employment_type_id UUID REFERENCES employment_types(id);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS work_arrangement_id UUID REFERENCES work_arrangements(id);
ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_start_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS contract_end_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS probation_end_date DATE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS remote_work_agreement_signed BOOLEAN DEFAULT FALSE;
ALTER TABLE employees ADD COLUMN IF NOT EXISTS client_deployment_id UUID;

-- Client deployments (for client-site workers)
CREATE TABLE client_deployments (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    employee_id UUID REFERENCES employees(id),
    client_name VARCHAR(200),
    client_contact_person VARCHAR(100),
    client_location TEXT,
    deployment_start_date DATE,
    deployment_end_date DATE,
    billing_rate_per_day DECIMAL(10,2),
    billing_rate_per_month DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'active', -- active, completed, terminated
    created_at TIMESTAMP DEFAULT NOW()
);

-- Track employment type changes
CREATE TABLE employment_type_history (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    from_type_id UUID REFERENCES employment_types(id),
    to_type_id UUID REFERENCES employment_types(id),
    from_arrangement_id UUID REFERENCES work_arrangements(id),
    to_arrangement_id UUID REFERENCES work_arrangements(id),
    effective_date DATE NOT NULL,
    reason TEXT,
    approved_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Staff Type Impact on Features

| Feature | Permanent | Contract | Temporary | Consultant | Intern |
|---------|-----------|----------|-----------|------------|--------|
| Payroll Processing | ✓ | ✓ | ✓ | ✗ (Invoice) | ✓ (Stipend) |
| PF Deduction | ✓ | Optional | ✗ | ✗ | ✗ |
| ESI Deduction | ✓ | Optional | ✗ | ✗ | ✗ |
| Leave Accrual | ✓ | As per contract | ✗ | ✗ | Limited |
| Gratuity | ✓ (5+ years) | ✗ | ✗ | ✗ | ✗ |
| Expense Claims | ✓ | ✓ | Limited | ✗ | ✓ |
| Asset Assignment | ✓ | ✓ | ✓ | Limited | ✓ |
| Performance Review | ✓ | ✓ | ✗ | ✗ | ✓ |
| Training Access | ✓ | ✓ | Limited | ✗ | ✓ |
| **Billable for Subscription** | ✓ | ✓ | ✓ | ✓ | ✓ |

> **Note**: All staff types count towards the employee count for subscription billing purposes. A company with 5 permanent + 3 contract + 2 interns = 10 employees for billing.

---

## 5. Ganakys - Platform Owner & Internal User

### Dual Role Architecture

Ganakys operates in two capacities within the platform:

```
┌─────────────────────────────────────────────────────────────────┐
│                    GANAKYS DUAL ROLE                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  ROLE 1: PLATFORM OWNER (Super Admin)                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Manage all customer tenants                           │   │
│  │  • View platform-wide analytics & revenue                │   │
│  │  • Handle billing, subscriptions, support                │   │
│  │  • System configuration & feature flags                  │   │
│  │  • Monitor system health & performance                   │   │
│  │  Access URL: admin.ganakys.com                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ROLE 2: INTERNAL ERP USER (Tenant)                             │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Use ERP for Ganakys' own HR, Payroll, Accounting      │   │
│  │  • Manage Ganakys employees, projects, invoices          │   │
│  │  • Same features as any customer tenant                  │   │
│  │  • Dogfooding - experience the product firsthand         │   │
│  │  Access URL: portal.ganakys.com                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  SHARED IDENTITY                                                │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Single Sign-On across both portals                    │   │
│  │  • Ganakys employees can have both roles                 │   │
│  │  • Role-based access: admin_role + tenant_role           │   │
│  │  • Seamless switching between admin & tenant views       │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Tenant Types

```yaml
tenant_types:
  platform_owner:
    code: "OWNER"
    name: "Platform Owner (Ganakys)"
    description: "The company that owns and operates the platform"
    billing: exempt              # No subscription fees
    features: all_unlocked       # Access to all features
    limits: unlimited            # No AI/storage limits
    can_access_admin: true       # Super admin portal access
    data_isolation: standard     # Same isolation as other tenants
    special_flags:
      - is_platform_owner
      - can_impersonate_tenants
      - receives_system_notifications

  customer:
    code: "CUST"
    name: "Customer Tenant"
    description: "Regular paying customer companies"
    billing: standard            # Monthly/Annual plans
    features: as_per_plan
    limits: as_per_employee_count
    can_access_admin: false
    data_isolation: standard

  demo:
    code: "DEMO"
    name: "Demo/Sandbox Tenant"
    description: "For sales demos and testing"
    billing: exempt
    features: all_unlocked
    limits: limited
    can_access_admin: false
    auto_cleanup: 30_days
    data_isolation: standard
```

### Super Admin Portal Features

```
SUPER ADMIN DASHBOARD
├── Tenant Management
│   ├── View all companies
│   ├── Search/filter tenants
│   ├── View tenant details
│   ├── Impersonate tenant (support access)
│   ├── Suspend/reactivate tenant
│   └── Delete tenant (with data export)
│
├── Subscription Management
│   ├── View all subscriptions
│   ├── Upgrade/downgrade tenants
│   ├── Apply discounts/coupons
│   ├── Generate invoices
│   └── Process refunds
│
├── Usage Analytics
│   ├── Total active tenants
│   ├── MRR/ARR metrics
│   ├── Churn rate
│   ├── AI usage across tenants
│   ├── Storage consumption
│   └── API call volumes
│
├── System Health
│   ├── Database performance
│   ├── API latency
│   ├── Error rates
│   ├── AI provider status
│   └── Queue backlogs
│
├── Support Tools
│   ├── Tenant support tickets
│   ├── System announcements
│   ├── Maintenance mode
│   └── Feature flags
│
└── Configuration
    ├── Plan management
    ├── Feature toggles
    ├── Email templates
    ├── System settings
    └── Audit logs
```

### Super Admin Database Schema

```sql
-- Tenant type classification
ALTER TABLE companies ADD COLUMN IF NOT EXISTS tenant_type VARCHAR(10) DEFAULT 'CUST';
-- OWNER = Ganakys (platform owner)
-- CUST = Regular customer
-- DEMO = Demo/Sandbox tenant

ALTER TABLE companies ADD COLUMN IF NOT EXISTS is_platform_owner BOOLEAN DEFAULT FALSE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS billing_exempt BOOLEAN DEFAULT FALSE;
ALTER TABLE companies ADD COLUMN IF NOT EXISTS limits_exempt BOOLEAN DEFAULT FALSE;

-- Ganakys admin users (for Super Admin portal)
-- These can ALSO be regular users in the Ganakys tenant
CREATE TABLE ganakys_admins (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    admin_role VARCHAR(20) DEFAULT 'support', -- super_admin, admin, support, viewer

    -- Link to Ganakys tenant user (if they also use the ERP)
    linked_user_id UUID REFERENCES users(id),  -- Their user account in Ganakys tenant
    linked_employee_id UUID REFERENCES employees(id),  -- Their employee record

    is_active BOOLEAN DEFAULT TRUE,
    last_admin_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Admin roles and permissions
CREATE TABLE admin_permissions (
    id UUID PRIMARY KEY,
    admin_role VARCHAR(20) NOT NULL,
    permission_code VARCHAR(50) NOT NULL,
    -- Examples: tenant.view, tenant.edit, tenant.suspend, billing.view,
    -- billing.refund, support.impersonate, system.config, etc.
    UNIQUE(admin_role, permission_code)
);

-- Seed default admin permissions
INSERT INTO admin_permissions (id, admin_role, permission_code) VALUES
    -- Super Admin: Full access
    (gen_random_uuid(), 'super_admin', 'tenant.*'),
    (gen_random_uuid(), 'super_admin', 'billing.*'),
    (gen_random_uuid(), 'super_admin', 'support.*'),
    (gen_random_uuid(), 'super_admin', 'system.*'),
    (gen_random_uuid(), 'super_admin', 'analytics.*'),

    -- Admin: Tenant and billing management
    (gen_random_uuid(), 'admin', 'tenant.view'),
    (gen_random_uuid(), 'admin', 'tenant.edit'),
    (gen_random_uuid(), 'admin', 'billing.view'),
    (gen_random_uuid(), 'admin', 'billing.edit'),
    (gen_random_uuid(), 'admin', 'support.*'),
    (gen_random_uuid(), 'admin', 'analytics.view'),

    -- Support: View and impersonate only
    (gen_random_uuid(), 'support', 'tenant.view'),
    (gen_random_uuid(), 'support', 'support.view'),
    (gen_random_uuid(), 'support', 'support.impersonate'),
    (gen_random_uuid(), 'support', 'support.tickets'),

    -- Viewer: Read-only access
    (gen_random_uuid(), 'viewer', 'tenant.view'),
    (gen_random_uuid(), 'viewer', 'analytics.view');

CREATE TABLE tenant_support_access (
    id UUID PRIMARY KEY,
    admin_id UUID REFERENCES ganakys_admins(id),
    company_id UUID REFERENCES companies(id),
    access_granted_at TIMESTAMP DEFAULT NOW(),
    access_expires_at TIMESTAMP,
    access_reason TEXT,
    ip_address VARCHAR(45)
);

CREATE TABLE system_announcements (
    id UUID PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    announcement_type VARCHAR(20), -- info, warning, maintenance
    target_plans TEXT[], -- which plans see this
    starts_at TIMESTAMP,
    ends_at TIMESTAMP,
    created_by UUID REFERENCES ganakys_admins(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE feature_flags (
    id UUID PRIMARY KEY,
    flag_name VARCHAR(100) UNIQUE,
    description TEXT,
    is_enabled BOOLEAN DEFAULT FALSE,
    rollout_percentage INT DEFAULT 0,
    target_plans TEXT[],
    target_companies UUID[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE support_tickets (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    created_by_user_id UUID REFERENCES users(id),
    assigned_to UUID REFERENCES ganakys_admins(id),
    subject VARCHAR(200),
    description TEXT,
    priority VARCHAR(10) DEFAULT 'medium', -- low, medium, high, critical
    status VARCHAR(20) DEFAULT 'open', -- open, in_progress, waiting, resolved, closed
    resolution TEXT,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE ticket_messages (
    id UUID PRIMARY KEY,
    ticket_id UUID REFERENCES support_tickets(id),
    sender_type VARCHAR(10), -- user, admin
    sender_id UUID,
    message TEXT,
    attachments JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Initialize Ganakys as the platform owner tenant
INSERT INTO companies (id, name, tenant_type, is_platform_owner, billing_exempt, limits_exempt, ...)
VALUES (
    'ganakys-uuid-here',
    'Ganakys Technologies',
    'OWNER',
    TRUE,
    TRUE,
    TRUE,
    ...
);
```

### Ganakys User Experience

```
┌─────────────────────────────────────────────────────────────────┐
│                GANAKYS EMPLOYEE LOGIN FLOW                       │
└─────────────────────────────────────────────────────────────────┘

  User logs in with Ganakys email (e.g., john@ganakys.com)
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM CHECKS USER ROLES                                        │
│  • Is user a Ganakys Admin? (ganakys_admins table)              │
│  • Is user a Ganakys Employee? (employees table, Ganakys tenant)│
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  ADMIN ONLY     │  │  BOTH ROLES     │  │  EMPLOYEE ONLY  │
│                 │  │                 │  │                 │
│  → Admin Portal │  │  → Role Switcher│  │  → ERP Dashboard│
│                 │  │    appears      │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ROLE SWITCHER (Top-right corner for dual-role users)           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  John Doe                                       [Switch] │   │
│  │  ─────────────────────────────────────────────────────── │   │
│  │  ○ Super Admin Portal     admin.ganakys.com             │   │
│  │  ● Ganakys ERP            portal.ganakys.com            │   │
│  │  ─────────────────────────────────────────────────────── │   │
│  │  Currently viewing: Ganakys ERP                          │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### URL Structure

| Portal | URL | Purpose |
|--------|-----|---------|
| Super Admin | `admin.ganakys.com` | Platform management |
| Ganakys ERP | `portal.ganakys.com` | Ganakys internal ERP |
| Customer ERP | `{customername}.ganakys.com` | Customer tenant access |
| Marketing Site | `www.ganakys.com` | Marketing & signup |

> **Note**: The customer-facing product may launch under a different brand name in the future. The architecture supports white-labeling and custom domains.

### Authentication Options

```yaml
authentication_methods:
  email_password:
    description: "Standard email + password login"
    flow:
      - User enters company email (e.g., john@acme.com)
      - System identifies tenant from email domain
      - User enters password
      - Redirected to tenant's ERP dashboard
    tenant_detection:
      - Email domain mapping (acme.com → Acme Inc tenant)
      - Subdomain detection (acme.ganakys.com)
      - Manual company selection (for users with multiple companies)

  magic_link:
    description: "Passwordless email login"
    flow:
      - User enters company email
      - Receives magic link via email
      - Click link → logged in
    expiry: 15_minutes
    single_use: true

  google_workspace:
    description: "Login with Google Workspace"
    provider: google
    scopes: [email, profile]
    tenant_detection: email_domain
    auto_provision: optional  # Auto-create user on first login

  microsoft_365:
    description: "Login with Microsoft 365"
    provider: azure_ad
    scopes: [email, profile]
    tenant_detection: email_domain
    auto_provision: optional

  sso_saml:
    description: "Enterprise SAML SSO"
    protocols: [SAML 2.0]
    identity_providers:
      - Okta
      - OneLogin
      - Azure AD
      - Google Workspace
      - Custom SAML IdP
    setup: per_tenant  # Each customer configures their own IdP
    available_for: all_plans  # No plan restriction

  sso_oidc:
    description: "OpenID Connect SSO"
    protocols: [OIDC]
    identity_providers:
      - Auth0
      - Keycloak
      - Custom OIDC provider
```

### Tenant Detection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    LOGIN FLOW                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  USER ENTERS EMAIL: john@acme.com                               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  SYSTEM CHECKS:                                                  │
│  1. Is email domain (acme.com) mapped to a tenant?              │
│  2. Is user registered with this email?                         │
│  3. Does tenant have SSO configured?                            │
└─────────────────────────────────────────────────────────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  SSO ENABLED    │  │  PASSWORD LOGIN │  │  NOT FOUND      │
│                 │  │                 │  │                 │
│  Redirect to    │  │  Show password  │  │  "No account    │
│  IdP login page │  │  input field    │  │  found. Sign up?│
└─────────────────┘  └─────────────────┘  └─────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  ON SUCCESS:                                                     │
│  • Set JWT token with tenant context                            │
│  • Redirect to: {tenant}.ganakys.com/dashboard                  │
│  • Or if on subdomain, stay on same domain                      │
└─────────────────────────────────────────────────────────────────┘
```

### Email Domain Mapping

```sql
-- Map email domains to tenants
CREATE TABLE tenant_email_domains (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    email_domain VARCHAR(255) NOT NULL,  -- e.g., 'acme.com'
    is_primary BOOLEAN DEFAULT FALSE,
    is_verified BOOLEAN DEFAULT FALSE,   -- DNS TXT record verification
    verification_token VARCHAR(100),
    verified_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(email_domain)  -- One domain = one tenant
);

-- SSO configuration per tenant
CREATE TABLE tenant_sso_config (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id) UNIQUE,
    sso_enabled BOOLEAN DEFAULT FALSE,
    sso_required BOOLEAN DEFAULT FALSE,  -- Force SSO, no password login
    provider_type VARCHAR(20),  -- saml, oidc, google, microsoft

    -- SAML settings
    saml_entity_id VARCHAR(500),
    saml_sso_url VARCHAR(500),
    saml_certificate TEXT,

    -- OIDC settings
    oidc_client_id VARCHAR(200),
    oidc_client_secret_encrypted VARCHAR(500),
    oidc_issuer_url VARCHAR(500),

    -- Google/Microsoft OAuth
    oauth_client_id VARCHAR(200),
    oauth_client_secret_encrypted VARCHAR(500),

    -- Auto-provisioning
    auto_provision_users BOOLEAN DEFAULT FALSE,
    default_role_on_provision VARCHAR(20) DEFAULT 'employee',

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Session Management for Dual Roles

```yaml
jwt_claims:
  user_id: "uuid"
  email: "john@ganakys.com"
  roles:
    admin:                          # Super Admin role (if applicable)
      role: "super_admin"
      permissions: ["tenant.*", "billing.*", ...]
    tenant:                         # ERP user role
      company_id: "ganakys-uuid"
      company_name: "Ganakys Technologies"
      user_role: "admin"            # Role within the ERP
      employee_id: "emp-uuid"

# Single JWT token contains both roles
# Frontend switches context based on which portal user is viewing
# No re-authentication needed when switching
```

---

## 6. Self-Service Tenant Onboarding

### Onboarding Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    SELF-SERVICE ONBOARDING                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 1: SIGN UP                                                 │
│  • Email verification                                            │
│  • Mobile OTP verification                                       │
│  • Basic company info (name, industry, size)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 2: COMPANY SETUP (AI-Assisted)                            │
│  • GSTIN lookup → Auto-fill company details                     │
│  • Industry selection → AI recommends org structure             │
│  • Team size → AI generates departments/designations            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 3: STATUTORY SETUP (Auto-configured)                      │
│  • PF registration (optional entry)                             │
│  • ESI registration (optional entry)                            │
│  • Professional Tax state auto-detected                         │
│  • TDS settings (defaults applied)                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 4: PLAN SELECTION                                         │
│  • 14-day free trial (all features)                             │
│  • Plan comparison                                               │
│  • Payment method (Razorpay)                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 5: DATA IMPORT (Optional)                                 │
│  • Excel templates for bulk import                              │
│  • AI-assisted field mapping                                     │
│  • Tally/Zoho/QuickBooks import                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  STEP 6: GO LIVE                                                │
│  • Interactive tutorial                                          │
│  • Sample data option                                            │
│  • Support chat available                                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 7. New Modules Required

### 7.1 Inventory Management

```sql
-- Core inventory tables
CREATE TABLE items (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    item_code VARCHAR(50),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    item_type VARCHAR(20), -- goods, services
    category_id UUID,
    unit_id UUID,
    hsn_sac_code VARCHAR(10),
    gst_rate DECIMAL(5,2),
    purchase_price DECIMAL(15,2),
    selling_price DECIMAL(15,2),
    min_stock_level DECIMAL(15,3),
    max_stock_level DECIMAL(15,3),
    reorder_level DECIMAL(15,3),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, item_code)
);

CREATE TABLE warehouses (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    code VARCHAR(20),
    name VARCHAR(100),
    address TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE stock_ledger (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    item_id UUID REFERENCES items(id),
    warehouse_id UUID REFERENCES warehouses(id),
    transaction_type VARCHAR(20), -- purchase, sale, transfer, adjustment
    reference_type VARCHAR(20), -- purchase_order, invoice, transfer, adjustment
    reference_id UUID,
    quantity DECIMAL(15,3),
    rate DECIMAL(15,2),
    value DECIMAL(15,2),
    balance_quantity DECIMAL(15,3),
    balance_value DECIMAL(15,2),
    transaction_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE stock_transfers (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    transfer_number VARCHAR(50),
    from_warehouse_id UUID REFERENCES warehouses(id),
    to_warehouse_id UUID REFERENCES warehouses(id),
    transfer_date DATE,
    status VARCHAR(20), -- draft, in_transit, received
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7.2 Purchase Order & Procurement

```sql
CREATE TABLE purchase_orders (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    po_number VARCHAR(50) UNIQUE,
    vendor_id UUID REFERENCES vendors(id),
    po_date DATE,
    expected_delivery_date DATE,
    warehouse_id UUID REFERENCES warehouses(id),
    subtotal DECIMAL(15,2),
    tax_amount DECIMAL(15,2),
    total_amount DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'draft', -- draft, sent, partial, received, cancelled
    approved_by UUID,
    approved_at TIMESTAMP,
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE purchase_order_items (
    id UUID PRIMARY KEY,
    po_id UUID REFERENCES purchase_orders(id),
    item_id UUID REFERENCES items(id),
    quantity DECIMAL(15,3),
    rate DECIMAL(15,2),
    amount DECIMAL(15,2),
    received_quantity DECIMAL(15,3) DEFAULT 0,
    gst_rate DECIMAL(5,2),
    gst_amount DECIMAL(15,2)
);

CREATE TABLE goods_receipt_notes (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    grn_number VARCHAR(50),
    po_id UUID REFERENCES purchase_orders(id),
    vendor_id UUID REFERENCES vendors(id),
    receipt_date DATE,
    warehouse_id UUID REFERENCES warehouses(id),
    status VARCHAR(20) DEFAULT 'draft', -- draft, completed
    created_by UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE purchase_requisitions (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    pr_number VARCHAR(50),
    requested_by UUID REFERENCES employees(id),
    department_id UUID REFERENCES departments(id),
    required_date DATE,
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, ordered
    approved_by UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7.3 Fixed Assets & Depreciation

```sql
CREATE TABLE asset_categories (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    name VARCHAR(100),
    depreciation_method VARCHAR(20), -- slm, wdv
    useful_life_years INT,
    depreciation_rate DECIMAL(5,2),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE fixed_assets (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    asset_code VARCHAR(50),
    name VARCHAR(200),
    description TEXT,
    category_id UUID REFERENCES asset_categories(id),
    purchase_date DATE,
    purchase_value DECIMAL(15,2),
    salvage_value DECIMAL(15,2),
    current_value DECIMAL(15,2),
    accumulated_depreciation DECIMAL(15,2),
    location VARCHAR(100),
    assigned_to UUID REFERENCES employees(id),
    status VARCHAR(20) DEFAULT 'active', -- active, disposed, sold, scrapped
    disposed_date DATE,
    disposal_value DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(company_id, asset_code)
);

CREATE TABLE depreciation_entries (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    asset_id UUID REFERENCES fixed_assets(id),
    fiscal_year_id UUID,
    period_start DATE,
    period_end DATE,
    opening_value DECIMAL(15,2),
    depreciation_amount DECIMAL(15,2),
    closing_value DECIMAL(15,2),
    journal_entry_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7.4 Expense Management

```sql
CREATE TABLE expense_categories (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    name VARCHAR(100),
    expense_account_id UUID REFERENCES accounts(id),
    requires_receipt BOOLEAN DEFAULT TRUE,
    max_amount DECIMAL(15,2),
    requires_approval BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE expense_claims (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    employee_id UUID REFERENCES employees(id),
    claim_number VARCHAR(50),
    claim_date DATE,
    total_amount DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'draft', -- draft, submitted, approved, rejected, paid
    submitted_at TIMESTAMP,
    approved_by UUID,
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    paid_in_payroll_run_id UUID,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE expense_claim_items (
    id UUID PRIMARY KEY,
    claim_id UUID REFERENCES expense_claims(id),
    category_id UUID REFERENCES expense_categories(id),
    expense_date DATE,
    description TEXT,
    amount DECIMAL(15,2),
    receipt_url TEXT,
    is_billable BOOLEAN DEFAULT FALSE,
    project_id UUID,
    ai_extracted BOOLEAN DEFAULT FALSE,
    ai_confidence DECIMAL(3,2)
);

CREATE TABLE travel_requests (
    id UUID PRIMARY KEY,
    company_id UUID REFERENCES companies(id),
    employee_id UUID REFERENCES employees(id),
    request_number VARCHAR(50),
    purpose TEXT,
    destination VARCHAR(200),
    travel_start_date DATE,
    travel_end_date DATE,
    estimated_cost DECIMAL(15,2),
    advance_required DECIMAL(15,2),
    status VARCHAR(20) DEFAULT 'pending', -- pending, approved, rejected, completed
    approved_by UUID,
    approved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 8. AI Enhancement Roadmap

### Current AI Capabilities
- Chat assistant with context
- Document extraction (invoices, bills)
- Transaction categorization
- Org structure generation
- Anomaly detection

### New AI Features Required

```yaml
ai_features:
  phase_1: # 3 months
    - smart_data_entry:
        description: "Auto-fill forms from natural language"
        example: "Add employee John Doe, salary 8L, joining March 1st"

    - intelligent_reports:
        description: "Generate custom reports from questions"
        example: "Show me employees whose PF was above 1800 last month"

    - compliance_alerts:
        description: "Proactive compliance warnings"
        example: "PF ECR due in 3 days for 45 employees"

  phase_2: # 6 months
    - auto_reconciliation:
        description: "AI-powered bank reconciliation"
        confidence_threshold: 0.95

    - expense_processor:
        description: "Extract expenses from receipts/photos"
        supported_formats: [image, pdf, email]

    - predictive_payroll:
        description: "Forecast payroll costs"
        features: [headcount_planning, cost_projection]

  phase_3: # 12 months
    - virtual_cfo:
        description: "AI-powered financial insights"
        capabilities:
          - cash_flow_prediction
          - expense_optimization
          - revenue_forecasting

    - hr_analytics:
        description: "People analytics engine"
        capabilities:
          - attrition_prediction
          - performance_correlation
          - hiring_recommendations

    - compliance_automation:
        description: "Auto-file GST returns"
        with_human_approval: true
```

---

## 9. Industry-Specific Templates

### Pre-built Configurations

```yaml
industry_templates:
  saas_tech:
    departments: [Engineering, Product, Design, Sales, Marketing, Customer Success, HR, Finance]
    designations: [Founder, CTO, VP Engineering, Tech Lead, Senior Engineer, Engineer, Intern]
    leave_types: [Casual, Sick, Privilege, Work From Home, Comp Off]
    expense_categories: [Travel, Software, Hardware, Internet, Phone]
    default_modules: [hr, payroll, leave, projects, invoicing]

  fintech:
    departments: [Technology, Risk, Compliance, Operations, Business, HR, Finance]
    designations: [CEO, CRO, Compliance Officer, Risk Analyst, Developer]
    compliance_requirements: [RBI, SEBI, PCI-DSS]
    default_modules: [hr, payroll, compliance, audit_trail]

  edtech:
    departments: [Content, Technology, Marketing, Sales, Operations, HR, Finance]
    designations: [Content Head, Curriculum Designer, Instructor, Developer]
    custom_fields: [student_count, course_count]
    default_modules: [hr, payroll, crm, projects]

  d2c_ecommerce:
    departments: [Product, Technology, Marketing, Operations, Warehouse, HR, Finance]
    designations: [Brand Manager, Category Manager, Warehouse Manager]
    inventory_enabled: true
    default_modules: [hr, payroll, inventory, invoicing, crm]

  manufacturing:
    departments: [Production, Quality, R&D, Supply Chain, HR, Finance]
    designations: [Plant Head, Production Manager, QC Inspector, Operator]
    inventory_enabled: true
    asset_tracking: true
    default_modules: [hr, payroll, inventory, assets, procurement]

  consulting:
    departments: [Delivery, Sales, HR, Finance]
    designations: [Partner, Principal Consultant, Senior Consultant, Consultant, Analyst]
    timesheet_enabled: true
    project_billing: true
    default_modules: [hr, payroll, projects, timesheet, invoicing]
```

---

## 10. Integration Architecture

### Payment Gateway Integration

```
PAYMENT FLOW
┌─────────────────────────────────────────────────────────────────┐
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  User    │───▶│ Ganakys  │───▶│ Razorpay │───▶│  Bank    │  │
│  │ Browser  │    │  Server  │    │   API    │    │          │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│       │               │               │               │         │
│       │               │               │               │         │
│       ▼               ▼               ▼               ▼         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  1. User selects plan                                     │  │
│  │  2. Ganakys creates Razorpay subscription                │  │
│  │  3. User completes payment on Razorpay checkout          │  │
│  │  4. Webhook confirms payment                             │  │
│  │  5. Subscription activated                               │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Third-Party Integrations

```yaml
integrations:
  payment:
    - razorpay  # Primary
    - stripe    # International

  communication:
    - aws_ses   # Email
    - msg91     # SMS
    - whatsapp_business  # WhatsApp

  government:
    - gstn      # GST portal
    - epfo      # PF portal
    - esic      # ESI portal
    - traces    # TDS portal
    - mca       # Company affairs

  accounting:
    - tally_import   # Tally data import
    - zoho_import    # Zoho migration
    - quickbooks     # QB import

  banking:
    - icici_connect  # Bank feed
    - hdfc_smartHub  # Bank feed
    - razorpay_x     # Payouts

  identity:
    - digilocker    # Document verification
    - aadhaar_ekyc  # KYC verification

  storage:
    - aws_s3        # Primary storage
    - cloudfront    # CDN
```

---

## 11. Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────────┐
│                    SECURITY ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  LAYER 1: EDGE SECURITY                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Cloudflare WAF (DDoS protection)                      │   │
│  │  • Rate limiting (per IP, per tenant)                    │   │
│  │  • Bot detection                                          │   │
│  │  • SSL/TLS termination                                    │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  LAYER 2: API GATEWAY                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • JWT validation                                         │   │
│  │  • API key management                                     │   │
│  │  • Request/response logging                               │   │
│  │  • Quota enforcement                                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  LAYER 3: APPLICATION SECURITY                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Input validation (SQL injection, XSS)                 │   │
│  │  • CSRF protection                                        │   │
│  │  • Content Security Policy                                │   │
│  │  • Role-based access control (RBAC)                      │   │
│  │  • Tenant isolation enforcement                           │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  LAYER 4: DATA SECURITY                                         │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Field-level encryption (PAN, Aadhaar, bank details)   │   │
│  │  • Database encryption at rest (AES-256)                 │   │
│  │  • Backup encryption                                      │   │
│  │  • Key management (AWS KMS)                               │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
│  LAYER 5: AUDIT & COMPLIANCE                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │  • Complete audit trail                                   │   │
│  │  • Data retention policies                                │   │
│  │  • GDPR compliance (data export/delete)                  │   │
│  │  • SOC 2 readiness                                        │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 12. DevOps & Infrastructure

### Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRODUCTION INFRASTRUCTURE                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                      CLOUDFLARE                          │   │
│  │              (DNS, CDN, WAF, DDoS)                       │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                       │
│  ┌───────────────────────▼─────────────────────────────────┐   │
│  │                    AWS ALB/NLB                           │   │
│  │              (Load Balancer)                             │   │
│  └───────────────────────┬─────────────────────────────────┘   │
│                          │                                       │
│     ┌────────────────────┼────────────────────┐                 │
│     │                    │                    │                 │
│  ┌──▼──┐              ┌──▼──┐              ┌──▼──┐              │
│  │ ECS │              │ ECS │              │ ECS │              │
│  │Task1│              │Task2│              │Task3│              │
│  └──┬──┘              └──┬──┘              └──┬──┘              │
│     │                    │                    │                 │
│     └────────────────────┼────────────────────┘                 │
│                          │                                       │
│     ┌────────────────────┼────────────────────┐                 │
│     │                    │                    │                 │
│  ┌──▼───────┐      ┌─────▼────┐      ┌───────▼──┐              │
│  │PostgreSQL│      │  Redis   │      │    S3    │              │
│  │  (RDS)   │      │(Elasti-  │      │(Documents│              │
│  │          │      │ cache)   │      │ Storage) │              │
│  └──────────┘      └──────────┘      └──────────┘              │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline

```yaml
pipeline:
  stages:
    - name: Code Quality
      steps:
        - lint (ruff, eslint)
        - type_check (mypy, tsc)
        - security_scan (bandit, npm audit)

    - name: Test
      steps:
        - unit_tests (pytest, vitest)
        - integration_tests
        - e2e_tests (playwright)

    - name: Build
      steps:
        - build_frontend (next build)
        - build_backend (docker build)
        - push_images (ECR)

    - name: Deploy Staging
      steps:
        - deploy_to_staging
        - run_smoke_tests
        - notify_team

    - name: Deploy Production
      steps:
        - manual_approval
        - blue_green_deploy
        - health_checks
        - rollback_on_failure
```

---

## 13. Implementation Phases

### Phase 1: Foundation (Months 1-3)
- [ ] Subscription & billing system
- [ ] Super admin portal (basic)
- [ ] Self-service onboarding flow
- [ ] Usage metering
- [ ] Razorpay integration

### Phase 2: Core Enhancements (Months 4-6)
- [ ] Inventory management module
- [ ] Purchase order workflow
- [ ] Enhanced AI features
- [ ] Industry templates
- [ ] API versioning

### Phase 3: Advanced Features (Months 7-9)
- [ ] Fixed assets module
- [ ] Expense management
- [ ] Advanced analytics
- [ ] Multi-currency support
- [ ] Workflow engine

### Phase 4: Scale & Polish (Months 10-12)
- [ ] Enterprise features (SSO, custom domains)
- [ ] White-labeling capabilities
- [ ] Mobile app (React Native)
- [ ] Marketplace for integrations
- [ ] Performance optimization

---

## 14. Success Metrics

### Business Metrics
| Metric | Target (Year 1) |
|--------|-----------------|
| Monthly Active Tenants | 500+ |
| MRR | ₹25 Lakhs |
| Churn Rate | <5% monthly |
| NPS Score | 40+ |
| Trial to Paid Conversion | 25% |

### Technical Metrics
| Metric | Target |
|--------|--------|
| API Uptime | 99.9% |
| API Latency (p95) | <500ms |
| Page Load Time | <3s |
| AI Response Time | <5s |
| Zero Critical Bugs | Always |

---

## 15. Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Data breach | Critical | Encryption, audit, SOC 2 |
| Downtime | High | Multi-AZ, auto-scaling |
| Compliance failure | High | Automated checks, expert review |
| AI hallucination | Medium | Human-in-loop, confidence thresholds |
| Vendor lock-in | Medium | Abstract integrations, multi-cloud ready |

---

## Conclusion

This architecture document provides a comprehensive roadmap to transform GanaPortal into **Ganakys Codilla Apps** - India's first AI-First ERP SaaS platform. The key transformations include:

1. **True SaaS Architecture**: Multi-tenant with self-service onboarding
2. **AI-First Approach**: Every module enhanced with AI capabilities
3. **Industry Agnostic**: Templates and configurations for any startup
4. **Complete Compliance**: Out-of-box Indian statutory compliance
5. **Ganakys Control**: Full management and analytics capabilities

The phased implementation approach ensures continuous value delivery while building towards the complete vision.

---

*Document Version: 1.0*
*Last Updated: January 2026*
*Author: Ganakys Architecture Team*
