-- ═══════════════════════════════════════════════════════════════════
-- GANAPORTAL - MISSING TABLES SCHEMA
-- Adds 90 missing tables to complete the 127-table requirement
-- ═══════════════════════════════════════════════════════════════════

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ═══════════════════════════════════════════════════════════════════
-- ENUM TYPES (Create if not exists)
-- ═══════════════════════════════════════════════════════════════════

DO $$ BEGIN
    CREATE TYPE holiday_type AS ENUM ('national', 'state', 'company', 'restricted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE leave_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE timesheet_status AS ENUM ('draft', 'submitted', 'approved', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE onboarding_status AS ENUM ('in_progress', 'submitted', 'approved', 'rejected', 'changes_requested');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE document_status AS ENUM ('active', 'archived', 'deleted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE project_status AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'review', 'done', 'blocked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE payment_mode AS ENUM ('cash', 'cheque', 'bank_transfer', 'upi', 'neft', 'rtgs', 'imps');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE loan_status AS ENUM ('active', 'closed', 'defaulted');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE reconciliation_status AS ENUM ('pending', 'matched', 'unmatched', 'manual');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE compliance_status AS ENUM ('pending', 'in_progress', 'completed', 'overdue');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 1: Organization Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Company Bank Accounts
CREATE TABLE IF NOT EXISTS company_bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    bank_name VARCHAR(100) NOT NULL,
    branch_name VARCHAR(100),
    account_number VARCHAR(20) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    account_type VARCHAR(20) DEFAULT 'current',
    is_primary BOOLEAN DEFAULT FALSE,
    is_salary_account BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Authorized Signatories
CREATE TABLE IF NOT EXISTS authorized_signatories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    pan VARCHAR(10),
    signature_url VARCHAR(500),
    can_sign_invoices BOOLEAN DEFAULT TRUE,
    can_sign_statutory BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 2: Employee Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Employee Employment Details
CREATE TABLE IF NOT EXISTS employee_employment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id) UNIQUE,
    date_of_joining DATE NOT NULL,
    date_of_confirmation DATE,
    date_of_exit DATE,
    exit_type VARCHAR(20),
    exit_reason TEXT,
    notice_period_days INT DEFAULT 30,
    probation_period_months INT DEFAULT 6,
    department_id UUID REFERENCES departments(id),
    designation_id UUID REFERENCES designations(id),
    reporting_to UUID REFERENCES employees(id),
    employment_type VARCHAR(20) DEFAULT 'full_time',
    work_location VARCHAR(100),
    shift_timing VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee Education
CREATE TABLE IF NOT EXISTS employee_education (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    degree VARCHAR(100),
    specialization VARCHAR(100),
    institution VARCHAR(200),
    university VARCHAR(200),
    year_of_passing INT,
    percentage DECIMAL(5,2),
    grade VARCHAR(10),
    document_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee Previous Employment
CREATE TABLE IF NOT EXISTS employee_previous_employment (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    company_name VARCHAR(200),
    designation VARCHAR(100),
    start_date DATE,
    end_date DATE,
    last_ctc DECIMAL(12,2),
    reason_for_leaving TEXT,
    relieving_letter_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Employee Nominees
CREATE TABLE IF NOT EXISTS employee_nominees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    name VARCHAR(100) NOT NULL,
    relationship VARCHAR(50),
    date_of_birth DATE,
    percentage DECIMAL(5,2) DEFAULT 100,
    address TEXT,
    phone VARCHAR(15),
    is_minor BOOLEAN DEFAULT FALSE,
    guardian_name VARCHAR(100),
    nominee_type VARCHAR(20) DEFAULT 'pf',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 3: Document Management
-- ═══════════════════════════════════════════════════════════════════

-- Folders
CREATE TABLE IF NOT EXISTS folders (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES folders(id),
    path TEXT,
    owner_id UUID REFERENCES users(id),
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Folder Permissions
CREATE TABLE IF NOT EXISTS folder_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    folder_id UUID REFERENCES folders(id),
    user_id UUID REFERENCES users(id),
    role VARCHAR(20),
    can_read BOOLEAN DEFAULT TRUE,
    can_write BOOLEAN DEFAULT FALSE,
    can_delete BOOLEAN DEFAULT FALSE,
    can_share BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    folder_id UUID REFERENCES folders(id),
    name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    mime_type VARCHAR(100),
    checksum VARCHAR(64),
    status document_status DEFAULT 'active',
    uploaded_by UUID REFERENCES users(id),
    entity_type VARCHAR(50),
    entity_id UUID,
    tags TEXT[],
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document Versions
CREATE TABLE IF NOT EXISTS document_versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES documents(id),
    version_number INT NOT NULL,
    file_path VARCHAR(500),
    file_size BIGINT,
    checksum VARCHAR(64),
    uploaded_by UUID REFERENCES users(id),
    change_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 4: Onboarding
-- ═══════════════════════════════════════════════════════════════════

-- Onboarding Progress
CREATE TABLE IF NOT EXISTS onboarding_progress (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id) UNIQUE,
    current_step INT DEFAULT 1,
    step_1_complete BOOLEAN DEFAULT FALSE,
    step_2_complete BOOLEAN DEFAULT FALSE,
    step_3_complete BOOLEAN DEFAULT FALSE,
    step_4_complete BOOLEAN DEFAULT FALSE,
    step_5_complete BOOLEAN DEFAULT FALSE,
    step_6_complete BOOLEAN DEFAULT FALSE,
    step_7_complete BOOLEAN DEFAULT FALSE,
    step_8_complete BOOLEAN DEFAULT FALSE,
    submitted_at TIMESTAMP WITH TIME ZONE,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    status onboarding_status DEFAULT 'in_progress',
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Onboarding Documents Checklist
CREATE TABLE IF NOT EXISTS onboarding_documents_checklist (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    document_name VARCHAR(100) NOT NULL,
    document_type VARCHAR(50),
    is_mandatory BOOLEAN DEFAULT TRUE,
    onboarding_step INT,
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 5: Leave Management
-- ═══════════════════════════════════════════════════════════════════

-- Leave Types
CREATE TABLE IF NOT EXISTS leave_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(50) NOT NULL,
    annual_quota INT,
    carry_forward BOOLEAN DEFAULT FALSE,
    max_carry_forward INT,
    is_encashable BOOLEAN DEFAULT FALSE,
    requires_document BOOLEAN DEFAULT FALSE,
    min_days DECIMAL(3,1) DEFAULT 0.5,
    max_days INT,
    advance_notice_days INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

-- Holidays
CREATE TABLE IF NOT EXISTS holidays (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type holiday_type DEFAULT 'company',
    is_optional BOOLEAN DEFAULT FALSE,
    year INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, date, name)
);

-- Leave Balances
CREATE TABLE IF NOT EXISTS leave_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
    year INT,
    opening_balance DECIMAL(4,1) DEFAULT 0,
    accrued DECIMAL(4,1) DEFAULT 0,
    used DECIMAL(4,1) DEFAULT 0,
    pending DECIMAL(4,1) DEFAULT 0,
    lapsed DECIMAL(4,1) DEFAULT 0,
    closing_balance DECIMAL(4,1),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, leave_type_id, year)
);

-- Leave Requests
CREATE TABLE IF NOT EXISTS leave_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days DECIMAL(4,1) NOT NULL,
    reason TEXT,
    document_id UUID REFERENCES documents(id),
    status leave_status DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leave Encashments
CREATE TABLE IF NOT EXISTS leave_encashments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
    year INT,
    days DECIMAL(4,1) NOT NULL,
    per_day_amount DECIMAL(12,2),
    total_amount DECIMAL(12,2),
    payroll_run_id UUID,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 6: Timesheet
-- ═══════════════════════════════════════════════════════════════════

-- Timesheets
CREATE TABLE IF NOT EXISTS timesheets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    total_hours DECIMAL(5,2) DEFAULT 0,
    billable_hours DECIMAL(5,2) DEFAULT 0,
    status timesheet_status DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, week_start_date)
);

-- Timesheet Entries
CREATE TABLE IF NOT EXISTS timesheet_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timesheet_id UUID REFERENCES timesheets(id),
    project_id UUID,
    task_id UUID,
    date DATE NOT NULL,
    hours DECIMAL(4,2) NOT NULL,
    is_billable BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Timesheet Approvals
CREATE TABLE IF NOT EXISTS timesheet_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timesheet_id UUID REFERENCES timesheets(id),
    approver_id UUID REFERENCES users(id),
    action VARCHAR(20) NOT NULL,
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 7: Payroll Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Tax Declarations (Form 12BB)
CREATE TABLE IF NOT EXISTS tax_declarations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    financial_year VARCHAR(10) NOT NULL,
    tax_regime VARCHAR(10) DEFAULT 'new',
    hra_rent_paid DECIMAL(12,2) DEFAULT 0,
    hra_landlord_name VARCHAR(100),
    hra_landlord_pan VARCHAR(10),
    hra_address TEXT,
    section_80c DECIMAL(12,2) DEFAULT 0,
    section_80d DECIMAL(12,2) DEFAULT 0,
    section_80g DECIMAL(12,2) DEFAULT 0,
    section_24b DECIMAL(12,2) DEFAULT 0,
    section_80e DECIMAL(12,2) DEFAULT 0,
    section_80tta DECIMAL(12,2) DEFAULT 0,
    nps_80ccd1b DECIMAL(12,2) DEFAULT 0,
    other_deductions DECIMAL(12,2) DEFAULT 0,
    total_deductions DECIMAL(12,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    verified_by UUID REFERENCES users(id),
    verified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, financial_year)
);

-- Tax Declaration Items
CREATE TABLE IF NOT EXISTS tax_declaration_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    declaration_id UUID REFERENCES tax_declarations(id),
    section VARCHAR(20) NOT NULL,
    description VARCHAR(200),
    declared_amount DECIMAL(12,2),
    proof_document_id UUID REFERENCES documents(id),
    verified_amount DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payslip Adjustments
CREATE TABLE IF NOT EXISTS payslip_adjustments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payslip_id UUID REFERENCES payslips(id),
    adjustment_type VARCHAR(20) NOT NULL,
    component_code VARCHAR(20),
    description VARCHAR(200),
    amount DECIMAL(12,2),
    is_earning BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Salary Advances
CREATE TABLE IF NOT EXISTS salary_advances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    amount DECIMAL(12,2) NOT NULL,
    requested_date DATE NOT NULL,
    reason TEXT,
    recovery_months INT DEFAULT 1,
    monthly_deduction DECIMAL(12,2),
    recovered_amount DECIMAL(12,2) DEFAULT 0,
    balance_amount DECIMAL(12,2),
    status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Salary Advance Recoveries
CREATE TABLE IF NOT EXISTS salary_advance_recoveries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    advance_id UUID REFERENCES salary_advances(id),
    payroll_run_id UUID REFERENCES payroll_runs(id),
    amount DECIMAL(12,2),
    recovered_on DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loans
CREATE TABLE IF NOT EXISTS loans (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    loan_type VARCHAR(50),
    principal_amount DECIMAL(12,2) NOT NULL,
    interest_rate DECIMAL(5,2) DEFAULT 0,
    tenure_months INT,
    emi_amount DECIMAL(12,2),
    start_date DATE,
    end_date DATE,
    recovered_principal DECIMAL(12,2) DEFAULT 0,
    recovered_interest DECIMAL(12,2) DEFAULT 0,
    outstanding_amount DECIMAL(12,2),
    status loan_status DEFAULT 'active',
    approved_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Loan EMIs
CREATE TABLE IF NOT EXISTS loan_emis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    loan_id UUID REFERENCES loans(id),
    emi_number INT,
    due_date DATE,
    principal_component DECIMAL(12,2),
    interest_component DECIMAL(12,2),
    emi_amount DECIMAL(12,2),
    paid_amount DECIMAL(12,2) DEFAULT 0,
    paid_on DATE,
    payroll_run_id UUID REFERENCES payroll_runs(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Arrears
CREATE TABLE IF NOT EXISTS arrears (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    arrear_type VARCHAR(50),
    from_month DATE,
    to_month DATE,
    amount DECIMAL(12,2),
    reason TEXT,
    payroll_run_id UUID REFERENCES payroll_runs(id),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reimbursements
CREATE TABLE IF NOT EXISTS reimbursements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    category VARCHAR(50),
    description TEXT,
    amount DECIMAL(12,2),
    expense_date DATE,
    document_id UUID REFERENCES documents(id),
    status VARCHAR(20) DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    payroll_run_id UUID REFERENCES payroll_runs(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 8: Statutory Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Statutory Settings
CREATE TABLE IF NOT EXISTS statutory_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id) UNIQUE,
    pf_enabled BOOLEAN DEFAULT TRUE,
    pf_employee_rate DECIMAL(5,2) DEFAULT 12.00,
    pf_employer_rate DECIMAL(5,2) DEFAULT 12.00,
    pf_admin_charges DECIMAL(5,2) DEFAULT 0.50,
    pf_edli DECIMAL(5,2) DEFAULT 0.50,
    pf_wage_ceiling DECIMAL(12,2) DEFAULT 15000,
    esi_enabled BOOLEAN DEFAULT TRUE,
    esi_employee_rate DECIMAL(5,2) DEFAULT 0.75,
    esi_employer_rate DECIMAL(5,2) DEFAULT 3.25,
    esi_wage_ceiling DECIMAL(12,2) DEFAULT 21000,
    pt_enabled BOOLEAN DEFAULT TRUE,
    pt_state VARCHAR(50) DEFAULT 'Karnataka',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PF ECR Files
CREATE TABLE IF NOT EXISTS pf_ecr_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    month DATE NOT NULL,
    file_path VARCHAR(500),
    total_employees INT,
    total_pf_wages DECIMAL(14,2),
    total_epf DECIMAL(14,2),
    total_eps DECIMAL(14,2),
    total_employer_contribution DECIMAL(14,2),
    trrn VARCHAR(50),
    challan_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ESI Return Files
CREATE TABLE IF NOT EXISTS esi_return_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    contribution_period VARCHAR(20) NOT NULL,
    file_path VARCHAR(500),
    total_employees INT,
    total_esi_wages DECIMAL(14,2),
    total_employee_contribution DECIMAL(14,2),
    total_employer_contribution DECIMAL(14,2),
    challan_number VARCHAR(50),
    challan_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TDS Salary Monthly
CREATE TABLE IF NOT EXISTS tds_salary_monthly (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    financial_year VARCHAR(10),
    month DATE,
    gross_salary DECIMAL(12,2),
    exemptions DECIMAL(12,2),
    deductions DECIMAL(12,2),
    taxable_income DECIMAL(12,2),
    tax_calculated DECIMAL(12,2),
    cess DECIMAL(12,2),
    tds_deducted DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, month)
);

-- TDS 24Q Files
CREATE TABLE IF NOT EXISTS tds_24q_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    financial_year VARCHAR(10),
    quarter VARCHAR(5),
    file_path VARCHAR(500),
    total_employees INT,
    total_tds DECIMAL(14,2),
    token_number VARCHAR(50),
    filed_date DATE,
    status VARCHAR(20) DEFAULT 'draft',
    generated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Form 16 Data
CREATE TABLE IF NOT EXISTS form16_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    financial_year VARCHAR(10),
    part_a_certificate_number VARCHAR(50),
    part_a_generated BOOLEAN DEFAULT FALSE,
    part_b_generated BOOLEAN DEFAULT FALSE,
    form16_file_id UUID REFERENCES documents(id),
    gross_salary DECIMAL(12,2),
    exemptions DECIMAL(12,2),
    deductions_16 DECIMAL(12,2),
    income_from_salary DECIMAL(12,2),
    chapter_vi_deductions DECIMAL(12,2),
    total_taxable_income DECIMAL(12,2),
    tax_payable DECIMAL(12,2),
    surcharge DECIMAL(12,2),
    cess DECIMAL(12,2),
    total_tax DECIMAL(12,2),
    tds_deducted DECIMAL(12,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, financial_year)
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 9: Accounting Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Accounting Periods
CREATE TABLE IF NOT EXISTS accounting_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    fiscal_year_id UUID,
    period_number INT,
    name VARCHAR(50),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    closed_by UUID REFERENCES users(id),
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Fiscal Years
CREATE TABLE IF NOT EXISTS fiscal_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT FALSE,
    is_closed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, name)
);

-- Recurring Entries
CREATE TABLE IF NOT EXISTS recurring_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    frequency VARCHAR(20) NOT NULL,
    next_execution_date DATE,
    last_executed DATE,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Recurring Entry Lines
CREATE TABLE IF NOT EXISTS recurring_entry_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recurring_entry_id UUID REFERENCES recurring_entries(id),
    account_id UUID REFERENCES accounts(id),
    description VARCHAR(200),
    debit_amount DECIMAL(14,2) DEFAULT 0,
    credit_amount DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Period Close Status
CREATE TABLE IF NOT EXISTS period_close_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    period_id UUID REFERENCES accounting_periods(id),
    module VARCHAR(50) NOT NULL,
    is_closed BOOLEAN DEFAULT FALSE,
    closed_by UUID REFERENCES users(id),
    closed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(period_id, module)
);

-- Opening Balances
CREATE TABLE IF NOT EXISTS opening_balances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    fiscal_year_id UUID REFERENCES fiscal_years(id),
    account_id UUID REFERENCES accounts(id),
    debit_balance DECIMAL(14,2) DEFAULT 0,
    credit_balance DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(fiscal_year_id, account_id)
);

-- Ledger Transactions
CREATE TABLE IF NOT EXISTS ledger_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    account_id UUID REFERENCES accounts(id),
    transaction_date DATE NOT NULL,
    voucher_type VARCHAR(50),
    voucher_number VARCHAR(50),
    voucher_id UUID,
    description TEXT,
    debit_amount DECIMAL(14,2) DEFAULT 0,
    credit_amount DECIMAL(14,2) DEFAULT 0,
    balance DECIMAL(14,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Cost Centers
CREATE TABLE IF NOT EXISTS cost_centers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    parent_id UUID REFERENCES cost_centers(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, code)
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 10: Multi-Currency
-- ═══════════════════════════════════════════════════════════════════

-- Currencies
CREATE TABLE IF NOT EXISTS currencies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(3) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    symbol VARCHAR(5),
    decimal_places INT DEFAULT 2,
    is_base BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Exchange Rates
CREATE TABLE IF NOT EXISTS exchange_rates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_currency VARCHAR(3) REFERENCES currencies(code),
    to_currency VARCHAR(3) REFERENCES currencies(code),
    rate_date DATE NOT NULL,
    rate DECIMAL(18,8) NOT NULL,
    source VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(from_currency, to_currency, rate_date)
);

-- Forex Transactions
CREATE TABLE IF NOT EXISTS forex_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    transaction_date DATE NOT NULL,
    from_currency VARCHAR(3),
    to_currency VARCHAR(3),
    from_amount DECIMAL(14,2),
    to_amount DECIMAL(14,2),
    exchange_rate DECIMAL(18,8),
    gain_loss DECIMAL(14,2),
    reference_type VARCHAR(50),
    reference_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 11: Customer & AR Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Customer Contacts
CREATE TABLE IF NOT EXISTS customer_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Customer Addresses
CREATE TABLE IF NOT EXISTS customer_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    customer_id UUID REFERENCES customers(id),
    address_type VARCHAR(20) DEFAULT 'billing',
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    state_code VARCHAR(2),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',
    gstin VARCHAR(15),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Receipts
CREATE TABLE IF NOT EXISTS receipts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    receipt_number VARCHAR(50) UNIQUE NOT NULL,
    receipt_date DATE NOT NULL,
    customer_id UUID REFERENCES customers(id),
    amount DECIMAL(14,2) NOT NULL,
    payment_mode payment_mode,
    reference_number VARCHAR(100),
    bank_account_id UUID,
    tds_amount DECIMAL(14,2) DEFAULT 0,
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Receipt Allocations
CREATE TABLE IF NOT EXISTS receipt_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    receipt_id UUID REFERENCES receipts(id),
    invoice_id UUID REFERENCES invoices(id),
    allocated_amount DECIMAL(14,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- LUT Records (Letter of Undertaking for exports)
CREATE TABLE IF NOT EXISTS lut_records (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    financial_year VARCHAR(10) NOT NULL,
    lut_number VARCHAR(50),
    filing_date DATE,
    valid_from DATE,
    valid_to DATE,
    document_id UUID REFERENCES documents(id),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, financial_year)
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 12: Vendor & AP Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- Vendor Contacts
CREATE TABLE IF NOT EXISTS vendor_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id),
    name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vendor Addresses
CREATE TABLE IF NOT EXISTS vendor_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id),
    address_type VARCHAR(20) DEFAULT 'billing',
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    state_code VARCHAR(2),
    pincode VARCHAR(10),
    country VARCHAR(100) DEFAULT 'India',
    gstin VARCHAR(15),
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bill Line Items
CREATE TABLE IF NOT EXISTS bill_line_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID REFERENCES bills(id),
    hsn_sac_code VARCHAR(10),
    description TEXT,
    quantity DECIMAL(10,3) DEFAULT 1,
    unit VARCHAR(20),
    rate DECIMAL(14,2),
    amount DECIMAL(14,2),
    discount_percent DECIMAL(5,2) DEFAULT 0,
    discount_amount DECIMAL(14,2) DEFAULT 0,
    taxable_amount DECIMAL(14,2),
    cgst_rate DECIMAL(5,2) DEFAULT 0,
    cgst_amount DECIMAL(14,2) DEFAULT 0,
    sgst_rate DECIMAL(5,2) DEFAULT 0,
    sgst_amount DECIMAL(14,2) DEFAULT 0,
    igst_rate DECIMAL(5,2) DEFAULT 0,
    igst_amount DECIMAL(14,2) DEFAULT 0,
    total_amount DECIMAL(14,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payments
CREATE TABLE IF NOT EXISTS payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    payment_number VARCHAR(50) UNIQUE NOT NULL,
    payment_date DATE NOT NULL,
    vendor_id UUID REFERENCES vendors(id),
    amount DECIMAL(14,2) NOT NULL,
    payment_mode payment_mode,
    reference_number VARCHAR(100),
    bank_account_id UUID,
    tds_section VARCHAR(20),
    tds_rate DECIMAL(5,2) DEFAULT 0,
    tds_amount DECIMAL(14,2) DEFAULT 0,
    net_amount DECIMAL(14,2),
    notes TEXT,
    status VARCHAR(20) DEFAULT 'draft',
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Payment Allocations
CREATE TABLE IF NOT EXISTS payment_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID REFERENCES payments(id),
    bill_id UUID REFERENCES bills(id),
    allocated_amount DECIMAL(14,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TDS Certificates (Form 16A)
CREATE TABLE IF NOT EXISTS tds_certificates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    vendor_id UUID REFERENCES vendors(id),
    financial_year VARCHAR(10),
    quarter VARCHAR(5),
    certificate_number VARCHAR(50),
    amount_paid DECIMAL(14,2),
    tds_deducted DECIMAL(14,2),
    date_of_deduction DATE,
    date_of_deposit DATE,
    challan_number VARCHAR(50),
    document_id UUID REFERENCES documents(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 13: Banking
-- ═══════════════════════════════════════════════════════════════════

-- Bank Accounts
CREATE TABLE IF NOT EXISTS bank_accounts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    account_id UUID REFERENCES accounts(id),
    bank_name VARCHAR(100) NOT NULL,
    branch_name VARCHAR(100),
    account_number VARCHAR(20) NOT NULL,
    ifsc_code VARCHAR(11) NOT NULL,
    account_type VARCHAR(20) DEFAULT 'current',
    opening_balance DECIMAL(14,2) DEFAULT 0,
    current_balance DECIMAL(14,2) DEFAULT 0,
    is_primary BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Transactions
CREATE TABLE IF NOT EXISTS bank_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_account_id UUID REFERENCES bank_accounts(id),
    transaction_date DATE NOT NULL,
    value_date DATE,
    reference_number VARCHAR(100),
    description TEXT,
    debit_amount DECIMAL(14,2) DEFAULT 0,
    credit_amount DECIMAL(14,2) DEFAULT 0,
    balance DECIMAL(14,2),
    transaction_type VARCHAR(50),
    voucher_type VARCHAR(50),
    voucher_id UUID,
    is_reconciled BOOLEAN DEFAULT FALSE,
    reconciliation_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Statements
CREATE TABLE IF NOT EXISTS bank_statements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_account_id UUID REFERENCES bank_accounts(id),
    statement_date DATE NOT NULL,
    from_date DATE,
    to_date DATE,
    opening_balance DECIMAL(14,2),
    closing_balance DECIMAL(14,2),
    total_debits DECIMAL(14,2),
    total_credits DECIMAL(14,2),
    file_id UUID REFERENCES documents(id),
    imported_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Statement Lines
CREATE TABLE IF NOT EXISTS bank_statement_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    statement_id UUID REFERENCES bank_statements(id),
    transaction_date DATE NOT NULL,
    value_date DATE,
    reference_number VARCHAR(100),
    description TEXT,
    debit_amount DECIMAL(14,2) DEFAULT 0,
    credit_amount DECIMAL(14,2) DEFAULT 0,
    balance DECIMAL(14,2),
    is_matched BOOLEAN DEFAULT FALSE,
    matched_transaction_id UUID REFERENCES bank_transactions(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Bank Reconciliations
CREATE TABLE IF NOT EXISTS bank_reconciliations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bank_account_id UUID REFERENCES bank_accounts(id),
    reconciliation_date DATE NOT NULL,
    statement_balance DECIMAL(14,2),
    book_balance DECIMAL(14,2),
    reconciled_balance DECIMAL(14,2),
    unreconciled_amount DECIMAL(14,2),
    status reconciliation_status DEFAULT 'pending',
    completed_by UUID REFERENCES users(id),
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Reconciliation Matches
CREATE TABLE IF NOT EXISTS reconciliation_matches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reconciliation_id UUID REFERENCES bank_reconciliations(id),
    statement_line_id UUID REFERENCES bank_statement_lines(id),
    transaction_id UUID REFERENCES bank_transactions(id),
    match_type VARCHAR(20) DEFAULT 'auto',
    matched_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Petty Cash Entries
CREATE TABLE IF NOT EXISTS petty_cash_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    entry_date DATE NOT NULL,
    description TEXT,
    paid_to VARCHAR(100),
    amount DECIMAL(12,2) NOT NULL,
    expense_account_id UUID REFERENCES accounts(id),
    document_id UUID REFERENCES documents(id),
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 14: GST Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- GSTR-1 B2B
CREATE TABLE IF NOT EXISTS gstr1_b2b (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gst_return_id UUID REFERENCES gst_returns(id),
    invoice_id UUID REFERENCES invoices(id),
    gstin VARCHAR(15) NOT NULL,
    invoice_number VARCHAR(50),
    invoice_date DATE,
    invoice_type VARCHAR(10),
    place_of_supply VARCHAR(2),
    taxable_value DECIMAL(14,2),
    igst DECIMAL(14,2) DEFAULT 0,
    cgst DECIMAL(14,2) DEFAULT 0,
    sgst DECIMAL(14,2) DEFAULT 0,
    cess DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GSTR-1 B2CS
CREATE TABLE IF NOT EXISTS gstr1_b2cs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gst_return_id UUID REFERENCES gst_returns(id),
    place_of_supply VARCHAR(2),
    rate DECIMAL(5,2),
    taxable_value DECIMAL(14,2),
    igst DECIMAL(14,2) DEFAULT 0,
    cgst DECIMAL(14,2) DEFAULT 0,
    sgst DECIMAL(14,2) DEFAULT 0,
    cess DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GSTR-3B Data
CREATE TABLE IF NOT EXISTS gstr3b_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    gst_return_id UUID REFERENCES gst_returns(id),
    section VARCHAR(20),
    description VARCHAR(200),
    taxable_value DECIMAL(14,2) DEFAULT 0,
    igst DECIMAL(14,2) DEFAULT 0,
    cgst DECIMAL(14,2) DEFAULT 0,
    sgst DECIMAL(14,2) DEFAULT 0,
    cess DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- GST Reconciliation
CREATE TABLE IF NOT EXISTS gst_reconciliation (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    return_period VARCHAR(10),
    vendor_gstin VARCHAR(15),
    invoice_number VARCHAR(50),
    invoice_date DATE,
    gstr2a_taxable DECIMAL(14,2),
    gstr2a_gst DECIMAL(14,2),
    books_taxable DECIMAL(14,2),
    books_gst DECIMAL(14,2),
    difference DECIMAL(14,2),
    status VARCHAR(20) DEFAULT 'mismatch',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 15: TDS on Vendors
-- ═══════════════════════════════════════════════════════════════════

-- TDS Sections
CREATE TABLE IF NOT EXISTS tds_sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    section_code VARCHAR(10) UNIQUE NOT NULL,
    description VARCHAR(200),
    individual_rate DECIMAL(5,2),
    company_rate DECIMAL(5,2),
    threshold_single DECIMAL(12,2),
    threshold_aggregate DECIMAL(12,2),
    surcharge_applicable BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Vendor TDS Tracking
CREATE TABLE IF NOT EXISTS vendor_tds_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    vendor_id UUID REFERENCES vendors(id),
    financial_year VARCHAR(10),
    tds_section VARCHAR(10),
    total_invoiced DECIMAL(14,2) DEFAULT 0,
    total_tds_deducted DECIMAL(14,2) DEFAULT 0,
    total_tds_deposited DECIMAL(14,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(vendor_id, financial_year, tds_section)
);

-- TDS Payments (Challan)
CREATE TABLE IF NOT EXISTS tds_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    financial_year VARCHAR(10),
    month DATE,
    tds_section VARCHAR(10),
    amount DECIMAL(14,2),
    interest DECIMAL(14,2) DEFAULT 0,
    late_fee DECIMAL(14,2) DEFAULT 0,
    total_amount DECIMAL(14,2),
    challan_number VARCHAR(50),
    bsr_code VARCHAR(10),
    payment_date DATE,
    bank_name VARCHAR(100),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TDS 26Q Data
CREATE TABLE IF NOT EXISTS tds_26q_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    financial_year VARCHAR(10),
    quarter VARCHAR(5),
    deductee_pan VARCHAR(10),
    deductee_name VARCHAR(200),
    section_code VARCHAR(10),
    payment_date DATE,
    amount_paid DECIMAL(14,2),
    tds_deducted DECIMAL(14,2),
    tds_deposited DECIMAL(14,2),
    deposit_date DATE,
    challan_number VARCHAR(50),
    certificate_number VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 16: CRM
-- ═══════════════════════════════════════════════════════════════════

-- Lead Sources
CREATE TABLE IF NOT EXISTS lead_sources (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Leads
CREATE TABLE IF NOT EXISTS leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    company_name VARCHAR(200),
    source_id UUID REFERENCES lead_sources(id),
    status lead_status DEFAULT 'new',
    assigned_to UUID REFERENCES users(id),
    expected_value DECIMAL(14,2),
    expected_close_date DATE,
    notes TEXT,
    converted_to_customer_id UUID REFERENCES customers(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lead Activities
CREATE TABLE IF NOT EXISTS lead_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id),
    activity_type VARCHAR(50),
    subject VARCHAR(200),
    description TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    outcome TEXT,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Lead Scores
CREATE TABLE IF NOT EXISTS lead_scores (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    lead_id UUID REFERENCES leads(id) UNIQUE,
    total_score INT DEFAULT 0,
    engagement_score INT DEFAULT 0,
    profile_score INT DEFAULT 0,
    behavior_score INT DEFAULT 0,
    last_calculated TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pipelines
CREATE TABLE IF NOT EXISTS pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    stages JSONB,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 17: Projects
-- ═══════════════════════════════════════════════════════════════════

-- Project Types
CREATE TABLE IF NOT EXISTS project_types (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    is_billable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    project_type_id UUID REFERENCES project_types(id),
    customer_id UUID REFERENCES customers(id),
    start_date DATE,
    end_date DATE,
    estimated_hours DECIMAL(10,2),
    actual_hours DECIMAL(10,2) DEFAULT 0,
    budget DECIMAL(14,2),
    billed_amount DECIMAL(14,2) DEFAULT 0,
    status project_status DEFAULT 'planning',
    project_manager_id UUID REFERENCES employees(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Milestones
CREATE TABLE IF NOT EXISTS milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE,
    completed_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    billing_amount DECIMAL(14,2),
    is_billed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    milestone_id UUID REFERENCES milestones(id),
    parent_task_id UUID REFERENCES tasks(id),
    code VARCHAR(20),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    start_date DATE,
    due_date DATE,
    estimated_hours DECIMAL(8,2),
    actual_hours DECIMAL(8,2) DEFAULT 0,
    priority VARCHAR(10) DEFAULT 'medium',
    status task_status DEFAULT 'todo',
    is_billable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task Assignments
CREATE TABLE IF NOT EXISTS task_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID REFERENCES tasks(id),
    employee_id UUID REFERENCES employees(id),
    assigned_hours DECIMAL(8,2),
    logged_hours DECIMAL(8,2) DEFAULT 0,
    assigned_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(task_id, employee_id)
);

-- Resource Allocations
CREATE TABLE IF NOT EXISTS resource_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    employee_id UUID REFERENCES employees(id),
    start_date DATE,
    end_date DATE,
    allocation_percentage DECIMAL(5,2) DEFAULT 100,
    hourly_rate DECIMAL(10,2),
    is_billable BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Project Billings
CREATE TABLE IF NOT EXISTS project_billings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id),
    invoice_id UUID REFERENCES invoices(id),
    billing_type VARCHAR(20),
    billing_period_start DATE,
    billing_period_end DATE,
    hours_billed DECIMAL(10,2),
    amount DECIMAL(14,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- WBS Templates
CREATE TABLE IF NOT EXISTS wbs_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    name VARCHAR(100) NOT NULL,
    project_type_id UUID REFERENCES project_types(id),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- WBS Template Items
CREATE TABLE IF NOT EXISTS wbs_template_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    template_id UUID REFERENCES wbs_templates(id),
    parent_id UUID REFERENCES wbs_template_items(id),
    phase_number INT,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    estimated_hours DECIMAL(8,2),
    deliverables TEXT,
    sort_order INT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 18: AI Additional Tables
-- ═══════════════════════════════════════════════════════════════════

-- AI Corrections (Learning from user feedback)
CREATE TABLE IF NOT EXISTS ai_corrections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id UUID REFERENCES ai_requests(id),
    original_output JSONB,
    corrected_output JSONB,
    correction_type VARCHAR(50),
    corrected_by UUID REFERENCES users(id),
    learned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Confidence Rules
CREATE TABLE IF NOT EXISTS ai_confidence_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    feature VARCHAR(100) NOT NULL,
    auto_execute_threshold DECIMAL(3,2) DEFAULT 0.95,
    queue_threshold DECIMAL(3,2) DEFAULT 0.70,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, feature)
);

-- Transaction Patterns (AI Learning)
CREATE TABLE IF NOT EXISTS transaction_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    pattern_type VARCHAR(50),
    pattern_key VARCHAR(200),
    pattern_value JSONB,
    frequency INT DEFAULT 1,
    confidence DECIMAL(3,2),
    last_seen TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- AI Suggestions
CREATE TABLE IF NOT EXISTS ai_suggestions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    suggestion_type VARCHAR(50),
    entity_type VARCHAR(50),
    entity_id UUID,
    suggestion JSONB,
    confidence DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'pending',
    accepted BOOLEAN,
    accepted_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ═══════════════════════════════════════════════════════════════════
-- SECTION 19: Compliance
-- ═══════════════════════════════════════════════════════════════════

-- Compliance Categories
CREATE TABLE IF NOT EXISTS compliance_categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    is_statutory BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance Items
CREATE TABLE IF NOT EXISTS compliance_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category_id UUID REFERENCES compliance_categories(id),
    name VARCHAR(200) NOT NULL,
    description TEXT,
    frequency VARCHAR(20),
    due_day INT,
    applicable_states TEXT[],
    penalty_info TEXT,
    form_number VARCHAR(20),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Compliance Tracker
CREATE TABLE IF NOT EXISTS compliance_tracker (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES company_profile(id),
    compliance_item_id UUID REFERENCES compliance_items(id),
    period DATE NOT NULL,
    due_date DATE NOT NULL,
    completed_date DATE,
    status compliance_status DEFAULT 'pending',
    filed_by UUID REFERENCES users(id),
    document_id UUID REFERENCES documents(id),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, compliance_item_id, period)
);

-- ═══════════════════════════════════════════════════════════════════
-- CREATE INDEXES FOR PERFORMANCE
-- ═══════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS idx_employees_company ON employees(company_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_employee ON leave_requests(employee_id);
CREATE INDEX IF NOT EXISTS idx_leave_requests_status ON leave_requests(status);
CREATE INDEX IF NOT EXISTS idx_timesheets_employee ON timesheets(employee_id);
CREATE INDEX IF NOT EXISTS idx_timesheets_week ON timesheets(week_start_date);
CREATE INDEX IF NOT EXISTS idx_payslips_payroll_run ON payslips(payroll_run_id);
CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id);
CREATE INDEX IF NOT EXISTS idx_invoices_date ON invoices(invoice_date);
CREATE INDEX IF NOT EXISTS idx_bills_vendor ON bills(vendor_id);
CREATE INDEX IF NOT EXISTS idx_journal_entries_date ON journal_entries(entry_date);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_account ON bank_transactions(bank_account_id);
CREATE INDEX IF NOT EXISTS idx_bank_transactions_date ON bank_transactions(transaction_date);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_ai_requests_status ON ai_requests(status);
CREATE INDEX IF NOT EXISTS idx_compliance_tracker_due ON compliance_tracker(due_date);

-- ═══════════════════════════════════════════════════════════════════
-- INSERT DEFAULT DATA
-- ═══════════════════════════════════════════════════════════════════

-- Default currencies
INSERT INTO currencies (code, name, symbol, is_base) VALUES
    ('INR', 'Indian Rupee', '₹', TRUE),
    ('USD', 'US Dollar', '$', FALSE),
    ('EUR', 'Euro', '€', FALSE),
    ('GBP', 'British Pound', '£', FALSE)
ON CONFLICT (code) DO NOTHING;

-- Default TDS sections
INSERT INTO tds_sections (section_code, description, individual_rate, company_rate, threshold_single) VALUES
    ('194A', 'Interest other than securities', 10.00, 10.00, 5000),
    ('194C', 'Payment to contractors', 1.00, 2.00, 30000),
    ('194H', 'Commission or brokerage', 5.00, 5.00, 15000),
    ('194I', 'Rent', 10.00, 10.00, 240000),
    ('194J', 'Professional/Technical fees', 10.00, 10.00, 30000),
    ('194O', 'E-commerce operator', 1.00, 1.00, 500000)
ON CONFLICT (section_code) DO NOTHING;

-- Default compliance categories
INSERT INTO compliance_categories (name, description, is_statutory) VALUES
    ('PF', 'Provident Fund Compliance', TRUE),
    ('ESI', 'Employee State Insurance Compliance', TRUE),
    ('TDS', 'Tax Deducted at Source', TRUE),
    ('GST', 'Goods and Services Tax', TRUE),
    ('PT', 'Professional Tax', TRUE),
    ('Labour Laws', 'Labour Law Compliance', TRUE),
    ('MCA', 'Ministry of Corporate Affairs', TRUE)
ON CONFLICT DO NOTHING;

-- ═══════════════════════════════════════════════════════════════════
-- SCHEMA COMPLETE
-- ═══════════════════════════════════════════════════════════════════
