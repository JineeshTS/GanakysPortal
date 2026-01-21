-- Fix column mismatches between database and ORM models
-- This script aligns database columns with SQLAlchemy ORM expectations

BEGIN;

-- ====================
-- 1. FIX leave_requests TABLE
-- ====================

-- Rename columns to match ORM
ALTER TABLE leave_requests RENAME COLUMN start_date TO from_date;
ALTER TABLE leave_requests RENAME COLUMN end_date TO to_date;
ALTER TABLE leave_requests RENAME COLUMN days TO total_days;
ALTER TABLE leave_requests RENAME COLUMN approved_by TO approver_id;

-- Drop foreign key that references wrong table
ALTER TABLE leave_requests DROP CONSTRAINT IF EXISTS leave_requests_approved_by_fkey;

-- Add missing columns
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS request_number VARCHAR(20);
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS company_id UUID;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS financial_year VARCHAR(9);
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS from_day_type VARCHAR(20) DEFAULT 'full';
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS to_day_type VARCHAR(20) DEFAULT 'full';
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS working_days NUMERIC(5,2) DEFAULT 0;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS sandwich_days NUMERIC(5,2) DEFAULT 0;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS holiday_days NUMERIC(5,2) DEFAULT 0;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS contact_number VARCHAR(20);
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS contact_address TEXT;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS document_paths JSONB DEFAULT '[]';
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS approver_remarks TEXT;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS rejected_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS cancelled_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS cancellation_reason TEXT;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS cancelled_by UUID;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS revoked_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS revocation_reason TEXT;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS revoked_by UUID;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS is_lop BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS lop_days NUMERIC(5,2) DEFAULT 0;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS submitted_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE leave_requests ADD COLUMN IF NOT EXISTS updated_by UUID;

-- Add foreign key to employees table for approver_id
ALTER TABLE leave_requests DROP CONSTRAINT IF EXISTS leave_requests_approver_id_fkey;
ALTER TABLE leave_requests ADD CONSTRAINT leave_requests_approver_id_fkey
    FOREIGN KEY (approver_id) REFERENCES employees(id);

-- Add foreign key to companies table
ALTER TABLE leave_requests ADD CONSTRAINT leave_requests_company_id_fkey
    FOREIGN KEY (company_id) REFERENCES companies(id);

-- Create indexes for leave_requests
CREATE INDEX IF NOT EXISTS ix_leave_requests_employee_status ON leave_requests(employee_id, status);
CREATE INDEX IF NOT EXISTS ix_leave_requests_dates ON leave_requests(from_date, to_date);
CREATE INDEX IF NOT EXISTS ix_leave_requests_company_fy ON leave_requests(company_id, financial_year);

-- ====================
-- 2. FIX salary_components TABLE
-- ====================

-- Add missing columns to salary_components
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS calculation_formula TEXT;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS is_fixed BOOLEAN DEFAULT TRUE;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS affects_pf BOOLEAN DEFAULT FALSE;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS affects_esi BOOLEAN DEFAULT FALSE;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS affects_pt BOOLEAN DEFAULT FALSE;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS affects_tds BOOLEAN DEFAULT TRUE;
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS min_amount NUMERIC(12,2);
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS max_amount NUMERIC(12,2);
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS default_value NUMERIC(12,2);
ALTER TABLE salary_components ADD COLUMN IF NOT EXISTS description TEXT;

-- ====================
-- 3. FIX leave_types TABLE
-- ====================

-- Check if leave_types needs company_id column
DO $$
BEGIN
    -- Check if company_id exists but references wrong table
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'leave_types_company_id_fkey'
        AND table_name = 'leave_types'
    ) THEN
        ALTER TABLE leave_types DROP CONSTRAINT IF EXISTS leave_types_company_id_fkey;
    END IF;
END $$;

-- Add missing columns to leave_types if not present
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
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS requires_document BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS document_required_after_days INTEGER;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS applicable_gender VARCHAR(10) DEFAULT 'all';
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS min_service_days INTEGER DEFAULT 0;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS probation_applicable BOOLEAN DEFAULT TRUE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS color_code VARCHAR(7) DEFAULT '#3B82F6';
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS sort_order INTEGER DEFAULT 0;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE leave_types ADD COLUMN IF NOT EXISTS updated_by UUID;

-- ====================
-- 4. FIX leave_balances TABLE
-- ====================

-- Check if leave_balances exists
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'leave_balances') THEN
        -- Add missing columns
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS financial_year VARCHAR(9);
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS opening_balance NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS entitled NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS accrued NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS carry_forward NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS adjustment NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS used NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS pending NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS encashed NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS lapsed NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS total_credited NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS available_balance NUMERIC(5,2) DEFAULT 0;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS last_accrual_date DATE;
        ALTER TABLE leave_balances ADD COLUMN IF NOT EXISTS next_accrual_date DATE;
    END IF;
END $$;

-- ====================
-- 5. FIX documents TABLE
-- ====================

-- Check if documents needs status column fix
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'documents' AND column_name = 'status') THEN
        -- Change status to VARCHAR to avoid type mismatch
        ALTER TABLE documents ALTER COLUMN status TYPE VARCHAR(20) USING status::VARCHAR(20);
    END IF;
END $$;

-- Add missing columns to documents
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_name VARCHAR(255);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_path TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_size BIGINT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS file_type VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS mime_type VARCHAR(100);
ALTER TABLE documents ADD COLUMN IF NOT EXISTS folder_id UUID;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS company_id UUID;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS uploaded_by UUID;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS tags JSONB DEFAULT '[]';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE documents ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE documents ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ====================
-- 6. FIX employees TABLE - employment_status type
-- ====================

-- Change employment_status to VARCHAR if it's an enum
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'employees' AND column_name = 'employment_status'
        AND data_type NOT LIKE '%character%'
    ) THEN
        ALTER TABLE employees ALTER COLUMN employment_status TYPE VARCHAR(50)
            USING employment_status::VARCHAR(50);
    END IF;
END $$;

-- ====================
-- 7. FIX folders TABLE
-- ====================

ALTER TABLE folders ADD COLUMN IF NOT EXISTS company_id UUID;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS parent_id UUID;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS name VARCHAR(255);
ALTER TABLE folders ADD COLUMN IF NOT EXISTS path TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS description TEXT;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS is_system BOOLEAN DEFAULT FALSE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS created_by UUID;
ALTER TABLE folders ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE folders ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ====================
-- 8. FIX leads TABLE
-- ====================

ALTER TABLE leads ADD COLUMN IF NOT EXISTS company_id UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS company_name VARCHAR(200);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS contact_name VARCHAR(100);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS source VARCHAR(50);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS status VARCHAR(30) DEFAULT 'new';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS assigned_to UUID;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS expected_value NUMERIC(15,2);
ALTER TABLE leads ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE leads ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leads ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE leads ADD COLUMN IF NOT EXISTS created_by UUID;

-- ====================
-- 9. FIX customers TABLE
-- ====================

ALTER TABLE customers ADD COLUMN IF NOT EXISTS company_id UUID;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS customer_code VARCHAR(50);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS name VARCHAR(200) NOT NULL DEFAULT '';
ALTER TABLE customers ADD COLUMN IF NOT EXISTS email VARCHAR(255);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS gstin VARCHAR(15);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS pan VARCHAR(10);
ALTER TABLE customers ADD COLUMN IF NOT EXISTS billing_address TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS shipping_address TEXT;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS credit_limit NUMERIC(15,2) DEFAULT 0;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS payment_terms INTEGER DEFAULT 30;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;
ALTER TABLE customers ADD COLUMN IF NOT EXISTS created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();
ALTER TABLE customers ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- ====================
-- 10. CREATE leave_transactions TABLE IF NOT EXISTS
-- ====================

CREATE TABLE IF NOT EXISTS leave_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
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

CREATE INDEX IF NOT EXISTS ix_leave_transactions_employee_fy ON leave_transactions(employee_id, financial_year);

-- ====================
-- 11. CREATE leave_encashments TABLE IF NOT EXISTS
-- ====================

CREATE TABLE IF NOT EXISTS leave_encashments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    encashment_number VARCHAR(20) UNIQUE,
    employee_id UUID REFERENCES employees(id),
    company_id UUID REFERENCES companies(id),
    leave_type_id UUID REFERENCES leave_types(id),
    financial_year VARCHAR(9) NOT NULL,
    days_requested NUMERIC(5,2) NOT NULL,
    available_balance NUMERIC(5,2) NOT NULL,
    per_day_amount NUMERIC(12,2) NOT NULL,
    total_amount NUMERIC(12,2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    approver_id UUID REFERENCES employees(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    approver_remarks TEXT,
    rejected_at TIMESTAMP WITH TIME ZONE,
    rejection_reason TEXT,
    payroll_run_id UUID,
    paid_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID
);

CREATE INDEX IF NOT EXISTS ix_leave_encashments_employee ON leave_encashments(employee_id);

-- ====================
-- 12. Grant permissions
-- ====================

GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ganaportal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ganaportal_user;

COMMIT;

-- Report on changes
SELECT 'Schema fixes applied successfully!' as status;
