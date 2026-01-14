-- ============================================================================
-- GanaPortal Database Schema Fix - Align DB with ORM Models
-- ============================================================================
-- This script fixes the mismatches between the SQLAlchemy ORM models and
-- the actual database schema.
-- ============================================================================

-- Remove transaction wrapper to allow partial success
-- BEGIN;

-- ============================================================================
-- 1. CREATE MISSING ENUM TYPES
-- ============================================================================

DO $$ BEGIN
    CREATE TYPE timesheet_status_enum AS ENUM ('draft', 'submitted', 'approved', 'rejected', 'locked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE attendance_status_enum AS ENUM ('present', 'absent', 'half_day', 'leave', 'holiday', 'weekend', 'work_from_home', 'on_duty');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE overtime_status_enum AS ENUM ('pending', 'approved', 'rejected');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE project_status_enum AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE task_status_enum AS ENUM ('todo', 'in_progress', 'review', 'completed', 'blocked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE leave_status_enum AS ENUM ('draft', 'pending', 'approved', 'rejected', 'cancelled', 'revoked');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE day_type_enum AS ENUM ('full', 'first_half', 'second_half');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE accrual_frequency_enum AS ENUM ('monthly', 'quarterly', 'half_yearly', 'yearly');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE gender_enum AS ENUM ('male', 'female', 'all');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE document_category_enum AS ENUM ('hr', 'finance', 'legal', 'compliance', 'project', 'general', 'employee', 'payroll', 'invoice', 'contract');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE document_status_enum AS ENUM ('draft', 'active', 'archived', 'deleted', 'expired');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE entity_type_enum AS ENUM ('lead', 'contact', 'customer', 'opportunity');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE lead_source_enum AS ENUM ('website', 'referral', 'social_media', 'cold_call', 'email_campaign', 'trade_show', 'advertisement', 'partner', 'indiamart', 'justdial', 'google_ads', 'other');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE opportunity_stage_enum AS ENUM ('prospecting', 'qualification', 'needs_analysis', 'proposal', 'negotiation', 'closed_won', 'closed_lost');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE activity_type_enum AS ENUM ('call', 'email', 'meeting', 'task', 'note', 'follow_up', 'site_visit', 'demo', 'whatsapp');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE gst_registration_type_enum AS ENUM ('regular', 'composition', 'unregistered', 'sez', 'deemed_export', 'overseas');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

DO $$ BEGIN
    CREATE TYPE payment_terms_enum AS ENUM ('immediate', 'net_7', 'net_15', 'net_30', 'net_45', 'net_60', 'net_90', 'custom');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

-- ============================================================================
-- 2. FIX TIMESHEETS TABLE
-- ============================================================================

-- Drop and recreate timesheets with correct structure
DROP TABLE IF EXISTS timesheet_entries CASCADE;
DROP TABLE IF EXISTS timesheet_approvals CASCADE;
DROP TABLE IF EXISTS timesheets CASCADE;
DROP TABLE IF EXISTS timesheet_tasks CASCADE;
DROP TABLE IF EXISTS timesheet_projects CASCADE;
DROP TABLE IF EXISTS timesheet_periods CASCADE;

-- Timesheet periods
CREATE TABLE timesheet_periods (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    period_type VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    year INTEGER NOT NULL,
    period_number INTEGER NOT NULL,
    submission_deadline TIMESTAMP WITH TIME ZONE,
    approval_deadline TIMESTAMP WITH TIME ZONE,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(company_id, start_date, end_date)
);

-- Timesheet projects
CREATE TABLE timesheet_projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    client_id UUID,
    client_name VARCHAR(255),
    start_date DATE,
    end_date DATE,
    budget_hours NUMERIC(10,2) DEFAULT 0,
    actual_hours NUMERIC(10,2) DEFAULT 0,
    billable_rate NUMERIC(10,2),
    status project_status_enum DEFAULT 'planning',
    is_billable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    UNIQUE(company_id, code)
);

-- Timesheet tasks
CREATE TABLE timesheet_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES timesheet_projects(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    estimated_hours NUMERIC(10,2) DEFAULT 0,
    actual_hours NUMERIC(10,2) DEFAULT 0,
    status task_status_enum DEFAULT 'todo',
    is_billable BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Main timesheets table
CREATE TABLE timesheets (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    employee_id UUID NOT NULL REFERENCES employees(id),
    period_id UUID REFERENCES timesheet_periods(id),
    date DATE NOT NULL,
    week_ending DATE,
    total_working_days INTEGER DEFAULT 0,
    total_days_worked INTEGER DEFAULT 0,
    total_hours NUMERIC(6,2) DEFAULT 0,
    total_billable_hours NUMERIC(6,2) DEFAULT 0,
    total_non_billable_hours NUMERIC(6,2) DEFAULT 0,
    total_overtime_hours NUMERIC(6,2) DEFAULT 0,
    total_leave_days NUMERIC(5,2) DEFAULT 0,
    total_holidays INTEGER DEFAULT 0,
    total_weekends INTEGER DEFAULT 0,
    status timesheet_status_enum DEFAULT 'draft',
    submitted_at TIMESTAMP WITH TIME ZONE,
    submitted_by UUID REFERENCES users(id),
    approver_id UUID REFERENCES employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    approver_remarks TEXT,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(employee_id, date)
);

CREATE INDEX idx_timesheet_employee_status ON timesheets(employee_id, status);
CREATE INDEX idx_timesheet_company_date ON timesheets(company_id, date);

-- Timesheet entries
CREATE TABLE timesheet_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timesheet_id UUID NOT NULL REFERENCES timesheets(id) ON DELETE CASCADE,
    project_id UUID REFERENCES timesheet_projects(id),
    task_id UUID REFERENCES timesheet_tasks(id),
    hours NUMERIC(4,2) NOT NULL DEFAULT 0,
    description TEXT,
    billable BOOLEAN DEFAULT TRUE,
    billing_rate NUMERIC(10,2),
    billing_amount NUMERIC(12,2),
    entry_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_timesheet_entry_project ON timesheet_entries(project_id, entry_date);

-- ============================================================================
-- 3. FIX ATTENDANCE TABLE (Create if missing)
-- ============================================================================

CREATE TABLE IF NOT EXISTS attendance_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id),
    log_date DATE NOT NULL,
    log_time TIME NOT NULL,
    log_type VARCHAR(20) NOT NULL,
    source VARCHAR(50),
    device_id VARCHAR(100),
    latitude NUMERIC(10,8),
    longitude NUMERIC(11,8),
    location_address TEXT,
    photo_path VARCHAR(500),
    is_verified BOOLEAN DEFAULT TRUE,
    verified_by UUID REFERENCES users(id),
    verification_remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_attendance_logs_employee ON attendance_logs(employee_id, log_date);

-- ============================================================================
-- 4. FIX LEAVE_TYPES TABLE
-- ============================================================================

-- Add missing columns to leave_types
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_paid BOOLEAN DEFAULT TRUE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_encashable BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_carry_forward BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS max_carry_forward_days NUMERIC(5,2) DEFAULT 0;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS carry_forward_expiry_months INTEGER DEFAULT 3;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS max_days_per_year NUMERIC(5,2);
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS max_consecutive_days INTEGER;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS min_days_per_application NUMERIC(3,2) DEFAULT 0.5;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS max_days_per_application NUMERIC(5,2);
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS document_required_after_days INTEGER;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS applicable_gender gender_enum DEFAULT 'all';
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS min_service_days INTEGER DEFAULT 0;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS probation_applicable BOOLEAN DEFAULT TRUE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS color_code VARCHAR(7) DEFAULT '#3B82F6';
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS updated_by UUID;

-- ============================================================================
-- 5. FIX FOLDERS TABLE
-- ============================================================================

ALTER TABLE folders ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS color VARCHAR(20);
ALTER TABLE folders ADD COLUMN IF NOT EXISTS icon VARCHAR(50);
ALTER TABLE folders ADD COLUMN IF NOT EXISTS level INTEGER DEFAULT 0;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS is_private BOOLEAN DEFAULT FALSE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS allowed_users TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS allowed_roles TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS allowed_departments TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS inherit_permissions BOOLEAN DEFAULT TRUE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS allow_subfolders BOOLEAN DEFAULT TRUE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS max_file_size_mb INTEGER;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS allowed_file_types TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE folders ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);

-- ============================================================================
-- 6. FIX DOCUMENTS TABLE
-- ============================================================================

ALTER TABLE documents ADD COLUMN IF NOT EXISTS company_id UUID REFERENCES companies(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS folder_id UUID REFERENCES folders(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS category document_category_enum DEFAULT 'general';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_path VARCHAR(500);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_size BIGINT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_extension VARCHAR(20);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_type VARCHAR(20) DEFAULT 'local';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_bucket VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS storage_key VARCHAR(500);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS parent_document_id UUID REFERENCES documents(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_latest BOOLEAN DEFAULT TRUE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS reference_type VARCHAR(50);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS reference_id UUID;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_confidential BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS access_level VARCHAR(20) DEFAULT 'company';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS allowed_users TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS allowed_roles TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS expiry_date TIMESTAMP WITH TIME ZONE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS reminder_days_before INTEGER;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS reminder_sent BOOLEAN DEFAULT FALSE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS status document_status_enum DEFAULT 'active';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS custom_fields TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);

-- ============================================================================
-- 7. FIX LEADS TABLE
-- ============================================================================

ALTER TABLE leads ADD COLUMN IF NOT EXISTS lead_number VARCHAR(20);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS company_size VARCHAR(50);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS website VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS mobile VARCHAR(20);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS designation VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS address TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS city VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS state VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS pincode VARCHAR(10);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS country VARCHAR(100) DEFAULT 'India';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS source lead_source_enum DEFAULT 'other';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS score INTEGER DEFAULT 0;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS rating VARCHAR(10);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS converted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS converted_customer_id UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS converted_opportunity_id UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS campaign_id UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS campaign_name VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS requirements TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- Update lead_number for existing records
UPDATE leads SET lead_number = 'LD-' || TO_CHAR(created_at, 'YYYYMM') || '-' || LPAD(id::text, 4, '0') WHERE lead_number IS NULL;

-- ============================================================================
-- 8. FIX CUSTOMERS TABLE
-- ============================================================================

ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_code VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS display_name VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS gstin VARCHAR(15);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS pan VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS gst_registration_type gst_registration_type_enum DEFAULT 'regular';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS tan VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS cin VARCHAR(21);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS state VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS state_code VARCHAR(2);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS tds_applicable BOOLEAN DEFAULT FALSE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS tds_section VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS tds_rate NUMERIC(5,2);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_address_line1 VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_address_line2 VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_city VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_state VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_pincode VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_country VARCHAR(100) DEFAULT 'India';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_address_line1 VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_address_line2 VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_city VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_state VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_pincode VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_country VARCHAR(100) DEFAULT 'India';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_same_as_billing BOOLEAN DEFAULT TRUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(18,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS credit_used NUMERIC(18,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS payment_terms payment_terms_enum DEFAULT 'net_30';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS credit_days INTEGER DEFAULT 30;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS currency VARCHAR(3) DEFAULT 'INR';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS bank_name VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS bank_account_number VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS bank_ifsc VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS bank_branch VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_type VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS industry VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS segment VARCHAR(100);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS primary_email VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS primary_phone VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS website VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS account_manager_id UUID REFERENCES users(id);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS converted_from_lead_id UUID;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS outstanding_receivable NUMERIC(18,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS total_revenue NUMERIC(18,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_by UUID REFERENCES users(id);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_by UUID REFERENCES users(id);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE;

-- ============================================================================
-- 9. CREATE MISSING CRM TABLES
-- ============================================================================

-- Contacts table
DROP TABLE IF EXISTS contacts CASCADE;
CREATE TABLE contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    customer_id UUID NOT NULL REFERENCES customers(id),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    designation VARCHAR(100),
    department VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    is_billing_contact BOOLEAN DEFAULT FALSE,
    is_shipping_contact BOOLEAN DEFAULT FALSE,
    is_decision_maker BOOLEAN DEFAULT FALSE,
    preferred_contact_method VARCHAR(20),
    best_time_to_call VARCHAR(50),
    linkedin_url VARCHAR(255),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_contacts_customer ON contacts(customer_id);

-- Opportunities table
DROP TABLE IF EXISTS opportunities CASCADE;
CREATE TABLE opportunities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    opportunity_number VARCHAR(20) UNIQUE NOT NULL,
    title VARCHAR(255) NOT NULL,
    lead_id UUID REFERENCES leads(id),
    customer_id UUID REFERENCES customers(id),
    value NUMERIC(18,2) DEFAULT 0,
    probability INTEGER DEFAULT 10,
    weighted_value NUMERIC(18,2) DEFAULT 0,
    currency VARCHAR(3) DEFAULT 'INR',
    stage opportunity_stage_enum DEFAULT 'prospecting',
    stage_changed_at TIMESTAMP WITH TIME ZONE,
    expected_close_date DATE,
    actual_close_date DATE,
    is_closed BOOLEAN DEFAULT FALSE,
    is_won BOOLEAN,
    close_reason VARCHAR(255),
    competitor_lost_to VARCHAR(255),
    source lead_source_enum,
    campaign_id UUID,
    owner_id UUID REFERENCES users(id),
    next_step VARCHAR(500),
    next_step_date DATE,
    description TEXT,
    competitors TEXT,
    requirements TEXT,
    products TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_opportunities_company_stage ON opportunities(company_id, stage);

-- CRM Activities table
DROP TABLE IF EXISTS crm_activities CASCADE;
CREATE TABLE crm_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    entity_type entity_type_enum NOT NULL,
    entity_id UUID NOT NULL,
    lead_id UUID REFERENCES leads(id),
    opportunity_id UUID REFERENCES opportunities(id),
    customer_id UUID REFERENCES customers(id),
    type activity_type_enum NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT,
    scheduled_at TIMESTAMP WITH TIME ZONE,
    duration_minutes INTEGER,
    is_all_day BOOLEAN DEFAULT FALSE,
    location VARCHAR(255),
    meeting_link VARCHAR(500),
    completed_at TIMESTAMP WITH TIME ZONE,
    outcome TEXT,
    owner_id UUID REFERENCES users(id),
    assigned_to UUID REFERENCES users(id),
    status VARCHAR(20) DEFAULT 'scheduled',
    priority VARCHAR(10) DEFAULT 'normal',
    reminder_at TIMESTAMP WITH TIME ZONE,
    reminder_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX idx_crm_activities_entity ON crm_activities(company_id, entity_type, entity_id);

-- CRM Notes table
DROP TABLE IF EXISTS crm_notes CASCADE;
CREATE TABLE crm_notes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    entity_type entity_type_enum NOT NULL,
    entity_id UUID NOT NULL,
    lead_id UUID REFERENCES leads(id),
    opportunity_id UUID REFERENCES opportunities(id),
    customer_id UUID REFERENCES customers(id),
    content TEXT NOT NULL,
    is_pinned BOOLEAN DEFAULT FALSE,
    is_private BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID NOT NULL REFERENCES users(id)
);

-- Pipelines table
DROP TABLE IF EXISTS pipelines CASCADE;
CREATE TABLE pipelines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    stage_config TEXT,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

-- ============================================================================
-- 10. CREATE MISSING LEAVE TABLES
-- ============================================================================

-- Leave policies
DROP TABLE IF EXISTS leave_policies CASCADE;
CREATE TABLE leave_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    leave_type_id UUID NOT NULL REFERENCES leave_types(id),
    name VARCHAR(100) NOT NULL,
    annual_entitlement NUMERIC(5,2) DEFAULT 0,
    is_accrual_based BOOLEAN DEFAULT FALSE,
    accrual_frequency accrual_frequency_enum,
    accrual_amount NUMERIC(5,2),
    accrual_start_from VARCHAR(20) DEFAULT 'joining',
    allow_carry_forward BOOLEAN DEFAULT FALSE,
    max_carry_forward NUMERIC(5,2) DEFAULT 0,
    carry_forward_expiry_months INTEGER DEFAULT 3,
    allow_encashment BOOLEAN DEFAULT FALSE,
    max_encashment_days NUMERIC(5,2) DEFAULT 0,
    encashment_rate NUMERIC(5,2) DEFAULT 100,
    max_consecutive_days INTEGER,
    min_days_notice INTEGER DEFAULT 0,
    requires_document BOOLEAN DEFAULT FALSE,
    document_after_days INTEGER,
    apply_sandwich_rule BOOLEAN DEFAULT FALSE,
    sandwich_include_holidays BOOLEAN DEFAULT TRUE,
    prorate_on_joining BOOLEAN DEFAULT TRUE,
    prorate_on_separation BOOLEAN DEFAULT TRUE,
    applicable_gender gender_enum DEFAULT 'all',
    min_service_months INTEGER DEFAULT 0,
    probation_applicable BOOLEAN DEFAULT TRUE,
    applicable_employment_types JSONB DEFAULT '["full_time"]',
    applicable_departments JSONB,
    applicable_designations JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    effective_from DATE,
    effective_to DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID,
    updated_by UUID,
    UNIQUE(company_id, leave_type_id)
);

-- Compensatory offs
DROP TABLE IF EXISTS compensatory_offs CASCADE;
CREATE TABLE compensatory_offs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    work_date DATE NOT NULL,
    work_type VARCHAR(20) NOT NULL,
    holiday_id UUID REFERENCES holidays(id),
    work_hours NUMERIC(4,2),
    work_reason TEXT,
    days_earned NUMERIC(4,2) DEFAULT 1,
    expiry_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    is_approved BOOLEAN DEFAULT FALSE,
    approver_id UUID REFERENCES employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approver_remarks TEXT,
    is_used BOOLEAN DEFAULT FALSE,
    used_in_leave_request_id UUID REFERENCES leave_requests(id),
    used_at TIMESTAMP WITH TIME ZONE,
    is_expired BOOLEAN DEFAULT FALSE,
    expired_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

-- Leave transactions
DROP TABLE IF EXISTS leave_transactions CASCADE;
CREATE TABLE leave_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id),
    leave_type_id UUID NOT NULL REFERENCES leave_types(id),
    financial_year VARCHAR(9) NOT NULL,
    transaction_type VARCHAR(30) NOT NULL,
    days NUMERIC(5,2) NOT NULL,
    balance_before NUMERIC(5,2) NOT NULL,
    balance_after NUMERIC(5,2) NOT NULL,
    reference_type VARCHAR(30),
    reference_id UUID,
    description TEXT,
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

CREATE INDEX idx_leave_transactions_employee ON leave_transactions(employee_id, financial_year);

-- ============================================================================
-- 11. CREATE MISSING SETTINGS TABLES
-- ============================================================================

-- Company branches
DROP TABLE IF EXISTS company_branches CASCADE;
CREATE TABLE company_branches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(255) NOT NULL,
    gstin VARCHAR(20),
    pf_establishment_code VARCHAR(50),
    esi_code VARCHAR(20),
    pt_state VARCHAR(5),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    pincode VARCHAR(10),
    is_head_office BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PF Settings
DROP TABLE IF EXISTS pf_settings CASCADE;
CREATE TABLE pf_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    employee_contribution FLOAT DEFAULT 12.0,
    employer_contribution FLOAT DEFAULT 12.0,
    employer_eps FLOAT DEFAULT 8.33,
    admin_charges FLOAT DEFAULT 0.5,
    wage_ceiling INTEGER DEFAULT 15000,
    restrict_to_basic BOOLEAN DEFAULT FALSE,
    include_da BOOLEAN DEFAULT TRUE,
    include_special_allowance BOOLEAN DEFAULT FALSE,
    opt_out_allowed BOOLEAN DEFAULT TRUE,
    opt_out_wage_limit INTEGER DEFAULT 15000,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ESI Settings
DROP TABLE IF EXISTS esi_settings CASCADE;
CREATE TABLE esi_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    employee_contribution FLOAT DEFAULT 0.75,
    employer_contribution FLOAT DEFAULT 3.25,
    wage_ceiling INTEGER DEFAULT 21000,
    round_off VARCHAR(10) DEFAULT 'nearest',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- PT Settings
DROP TABLE IF EXISTS pt_settings CASCADE;
CREATE TABLE pt_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    state VARCHAR(5) DEFAULT 'KA',
    slabs JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- TDS Settings
DROP TABLE IF EXISTS tds_settings CASCADE;
CREATE TABLE tds_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    default_regime VARCHAR(10) DEFAULT 'new',
    allow_employee_choice BOOLEAN DEFAULT TRUE,
    standard_deduction INTEGER DEFAULT 50000,
    cess FLOAT DEFAULT 4.0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Pay Schedule
DROP TABLE IF EXISTS pay_schedules CASCADE;
CREATE TABLE pay_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    pay_day INTEGER DEFAULT 1,
    processing_day INTEGER DEFAULT 28,
    attendance_cutoff INTEGER DEFAULT 25,
    arrear_processing VARCHAR(10) DEFAULT 'next',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Week Off Settings
DROP TABLE IF EXISTS week_off_settings CASCADE;
CREATE TABLE week_off_settings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    week_offs JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Shifts
DROP TABLE IF EXISTS shifts CASCADE;
CREATE TABLE shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    break_duration INTEGER DEFAULT 60,
    working_hours FLOAT DEFAULT 8.0,
    grace_in_minutes INTEGER DEFAULT 15,
    grace_out_minutes INTEGER DEFAULT 15,
    half_day_hours FLOAT DEFAULT 4.0,
    is_default BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    applicable_days INTEGER[] DEFAULT '{1,2,3,4,5}',
    color VARCHAR(10) DEFAULT '#3B82F6',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Overtime Rules
DROP TABLE IF EXISTS overtime_rules CASCADE;
CREATE TABLE overtime_rules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    min_hours FLOAT DEFAULT 1.0,
    multiplier FLOAT DEFAULT 1.5,
    requires_approval BOOLEAN DEFAULT TRUE,
    max_hours_per_day FLOAT DEFAULT 4.0,
    max_hours_per_week FLOAT DEFAULT 20.0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Attendance Config
DROP TABLE IF EXISTS attendance_config CASCADE;
CREATE TABLE attendance_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id) UNIQUE,
    marking_method VARCHAR(20) DEFAULT 'all',
    allow_multiple_checkin BOOLEAN DEFAULT TRUE,
    auto_checkout_enabled BOOLEAN DEFAULT TRUE,
    auto_checkout_time TIME DEFAULT '23:00',
    min_work_hours_full_day FLOAT DEFAULT 8.0,
    min_work_hours_half_day FLOAT DEFAULT 4.0,
    late_mark_after_minutes INTEGER DEFAULT 15,
    early_leave_before_minutes INTEGER DEFAULT 15,
    geo_fence_enabled BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Geo Fence Locations
DROP TABLE IF EXISTS geo_fence_locations CASCADE;
CREATE TABLE geo_fence_locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    address TEXT,
    latitude FLOAT NOT NULL,
    longitude FLOAT NOT NULL,
    radius_meters INTEGER DEFAULT 100,
    is_active BOOLEAN DEFAULT TRUE,
    applicable_branches UUID[] DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Email Templates
DROP TABLE IF EXISTS email_templates CASCADE;
CREATE TABLE email_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    category VARCHAR(20) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    variables VARCHAR[] DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Roles
DROP TABLE IF EXISTS roles CASCADE;
CREATE TABLE roles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    description TEXT,
    permissions VARCHAR[] DEFAULT '{}',
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================================================
-- 12. INSERT DEFAULT SETTINGS FOR COMPANY
-- ============================================================================

-- Insert default settings for the existing company
INSERT INTO pf_settings (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO esi_settings (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO pt_settings (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO tds_settings (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO pay_schedules (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO week_off_settings (company_id, week_offs)
SELECT id, '[{"day": 0, "isOff": true}, {"day": 6, "isOff": true}]'::jsonb
FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

INSERT INTO attendance_config (company_id)
SELECT id FROM companies WHERE id = 'a0000000-0000-0000-0000-000000000001'
ON CONFLICT (company_id) DO NOTHING;

-- Insert default shift
INSERT INTO shifts (company_id, code, name, start_time, end_time, is_default)
SELECT 'a0000000-0000-0000-0000-000000000001', 'GEN', 'General Shift', '09:00', '18:00', TRUE
WHERE NOT EXISTS (SELECT 1 FROM shifts WHERE company_id = 'a0000000-0000-0000-0000-000000000001');

-- Insert default leave types
INSERT INTO leave_types (company_id, code, name, is_paid, annual_quota, is_active)
SELECT 'a0000000-0000-0000-0000-000000000001', 'CL', 'Casual Leave', TRUE, 12, TRUE
WHERE NOT EXISTS (SELECT 1 FROM leave_types WHERE code = 'CL' AND company_id = 'a0000000-0000-0000-0000-000000000001');

INSERT INTO leave_types (company_id, code, name, is_paid, annual_quota, is_active, is_encashable, is_carry_forward)
SELECT 'a0000000-0000-0000-0000-000000000001', 'EL', 'Earned Leave', TRUE, 15, TRUE, TRUE, TRUE
WHERE NOT EXISTS (SELECT 1 FROM leave_types WHERE code = 'EL' AND company_id = 'a0000000-0000-0000-0000-000000000001');

INSERT INTO leave_types (company_id, code, name, is_paid, annual_quota, is_active, requires_document)
SELECT 'a0000000-0000-0000-0000-000000000001', 'SL', 'Sick Leave', TRUE, 12, TRUE, TRUE
WHERE NOT EXISTS (SELECT 1 FROM leave_types WHERE code = 'SL' AND company_id = 'a0000000-0000-0000-0000-000000000001');

-- COMMIT;

-- ============================================================================
-- DONE
-- ============================================================================
