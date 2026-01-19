-- ============================================
-- USER MANAGEMENT SCHEMA MIGRATION
-- GanaPortal - Comprehensive User Categories
-- ============================================

BEGIN;

-- ============================================
-- 1. CREATE ENUM TYPES
-- ============================================

-- Drop existing role check constraint first
ALTER TABLE users DROP CONSTRAINT IF EXISTS users_role_check;

-- Create user_category enum
DO $$ BEGIN
    CREATE TYPE user_category AS ENUM ('INTERNAL', 'EXTERNAL', 'GOVERNMENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create user_type enum
DO $$ BEGIN
    CREATE TYPE user_type AS ENUM (
        -- Internal
        'founder',
        'full_time_employee',
        'contract_employee',
        'intern',
        -- External
        'chartered_accountant',
        'consultant',
        'customer',
        'vendor',
        -- Government
        'tax_official',
        'labor_official',
        'customs_official',
        'other_official'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create data_scope enum
DO $$ BEGIN
    CREATE TYPE data_scope AS ENUM ('ALL', 'OWN', 'DEPARTMENT', 'ASSIGNED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- ============================================
-- 2. CREATE MODULES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS modules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    route VARCHAR(100),
    sort_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 3. ALTER USERS TABLE
-- ============================================

-- Add new columns to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS category user_category;
ALTER TABLE users ADD COLUMN IF NOT EXISTS user_type user_type;
ALTER TABLE users ADD COLUMN IF NOT EXISTS expires_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS linked_entity_type VARCHAR(50);
ALTER TABLE users ADD COLUMN IF NOT EXISTS linked_entity_id UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS organization_name VARCHAR(255);
ALTER TABLE users ADD COLUMN IF NOT EXISTS designation VARCHAR(100);
ALTER TABLE users ADD COLUMN IF NOT EXISTS phone VARCHAR(20);
ALTER TABLE users ADD COLUMN IF NOT EXISTS access_reason TEXT;
ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_by UUID;
ALTER TABLE users ADD COLUMN IF NOT EXISTS invited_at TIMESTAMP WITH TIME ZONE;
ALTER TABLE users ADD COLUMN IF NOT EXISTS last_activity_at TIMESTAMP WITH TIME ZONE;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_users_category ON users(category);
CREATE INDEX IF NOT EXISTS idx_users_user_type ON users(user_type);
CREATE INDEX IF NOT EXISTS idx_users_linked_entity ON users(linked_entity_type, linked_entity_id);
CREATE INDEX IF NOT EXISTS idx_users_expires_at ON users(expires_at) WHERE expires_at IS NOT NULL;

-- ============================================
-- 4. CREATE USER MODULE PERMISSIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS user_module_permissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    module_id UUID NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    can_view BOOLEAN DEFAULT false,
    can_create BOOLEAN DEFAULT false,
    can_edit BOOLEAN DEFAULT false,
    can_delete BOOLEAN DEFAULT false,
    can_export BOOLEAN DEFAULT false,
    can_approve BOOLEAN DEFAULT false,
    data_scope data_scope DEFAULT 'OWN',
    custom_filters JSONB,
    granted_by UUID REFERENCES users(id),
    granted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, module_id)
);

CREATE INDEX IF NOT EXISTS idx_user_permissions_user ON user_module_permissions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_permissions_module ON user_module_permissions(module_id);

-- ============================================
-- 5. CREATE PERMISSION TEMPLATES TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS permission_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    category user_category NOT NULL,
    user_type user_type,
    permissions JSONB NOT NULL,
    is_default BOOLEAN DEFAULT false,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ============================================
-- 6. CREATE USER INVITATIONS TABLE
-- ============================================

CREATE TABLE IF NOT EXISTS user_invitations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) NOT NULL,
    category user_category NOT NULL,
    user_type user_type NOT NULL,
    template_id UUID REFERENCES permission_templates(id),
    organization_name VARCHAR(255),
    linked_entity_type VARCHAR(50),
    linked_entity_id UUID,
    expires_at TIMESTAMP WITH TIME ZONE,
    access_reason TEXT,
    invitation_token VARCHAR(100) UNIQUE NOT NULL,
    invitation_expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    invited_by UUID NOT NULL REFERENCES users(id),
    accepted_at TIMESTAMP WITH TIME ZONE,
    created_user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(email, invitation_token)
);

CREATE INDEX IF NOT EXISTS idx_invitations_email ON user_invitations(email);
CREATE INDEX IF NOT EXISTS idx_invitations_token ON user_invitations(invitation_token);

-- ============================================
-- 7. SEED MODULES DATA
-- ============================================

INSERT INTO modules (code, name, category, description, icon, route, sort_order) VALUES
-- Dashboard
('dashboard', 'Dashboard', 'Core', 'Main dashboard with analytics', 'LayoutDashboard', '/dashboard', 1),

-- HR & Employee Management
('employees', 'Employees', 'HR', 'Employee master data management', 'Users', '/employees', 10),
('departments', 'Departments', 'HR', 'Department and team structure', 'Building2', '/organization', 11),
('attendance', 'Attendance', 'HR', 'Attendance tracking and reports', 'Clock', '/attendance', 12),
('leave', 'Leave Management', 'HR', 'Leave requests and approvals', 'Calendar', '/leave', 13),
('timesheet', 'Timesheet', 'HR', 'Time tracking and project allocation', 'Timer', '/timesheets', 14),
('onboarding', 'Onboarding', 'HR', 'Employee onboarding workflow', 'UserPlus', '/onboarding', 15),
('recruitment', 'Recruitment', 'HR', 'Job postings and hiring', 'Briefcase', '/recruitment', 16),
('exit', 'Exit Management', 'HR', 'Employee offboarding', 'UserMinus', '/exit', 17),

-- Payroll & Statutory
('payroll', 'Payroll', 'Payroll', 'Salary processing and payslips', 'Wallet', '/payroll', 20),
('statutory', 'Statutory Compliance', 'Payroll', 'PF, ESI, PT compliance', 'Shield', '/statutory', 21),

-- Finance - Receivables
('invoices', 'Invoices', 'Finance', 'Customer invoicing (AR)', 'FileText', '/invoices', 30),
('customers', 'Customers', 'Finance', 'Customer master data', 'Users', '/crm', 31),
('receipts', 'Receipts', 'Finance', 'Payment receipts', 'Receipt', '/receipts', 32),

-- Finance - Payables
('bills', 'Bills', 'Finance', 'Vendor bills (AP)', 'FileStack', '/bills', 40),
('vendors', 'Vendors', 'Finance', 'Vendor master data', 'Truck', '/vendors', 41),
('payments', 'Payments', 'Finance', 'Vendor payments', 'CreditCard', '/payments', 42),

-- Banking & Treasury
('banking', 'Banking', 'Finance', 'Bank accounts and reconciliation', 'Landmark', '/banking', 50),

-- Tax & Compliance
('gst', 'GST', 'Compliance', 'GST returns and compliance', 'FileCheck', '/gst', 60),
('tds', 'TDS', 'Compliance', 'TDS deductions and returns', 'FileCheck', '/statutory', 61),

-- Projects
('projects', 'Projects', 'Projects', 'Project management', 'FolderKanban', '/projects', 70),

-- Documents
('documents', 'Documents', 'Core', 'Document management system', 'FolderOpen', '/documents', 80),

-- Reports & Analytics
('reports', 'Reports', 'Reports', 'Financial and operational reports', 'BarChart', '/reports', 90),
('analytics', 'Analytics', 'Reports', 'Advanced analytics dashboard', 'TrendingUp', '/analytics', 91),

-- Settings & Admin
('settings', 'Settings', 'Admin', 'System configuration', 'Settings', '/settings', 100),
('users', 'User Management', 'Admin', 'User accounts and permissions', 'UserCog', '/settings/users', 101),
('audit', 'Audit Logs', 'Admin', 'System audit trail', 'ScrollText', '/audit', 102)

ON CONFLICT (code) DO UPDATE SET
    name = EXCLUDED.name,
    category = EXCLUDED.category,
    description = EXCLUDED.description,
    updated_at = NOW();

-- ============================================
-- 8. SEED PERMISSION TEMPLATES
-- ============================================

-- Founder/Super Admin Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('founder_full_access', 'Founder - Full Access', 'Complete system access for founders', 'INTERNAL', 'founder', true,
'{
    "all_modules": true,
    "data_scope": "ALL",
    "can_view": true,
    "can_create": true,
    "can_edit": true,
    "can_delete": true,
    "can_export": true,
    "can_approve": true
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Full Time Employee Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('employee_standard', 'Employee - Standard Access', 'Standard access for full-time employees', 'INTERNAL', 'full_time_employee', true,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "OWN"},
        "employees": {"can_view": true, "data_scope": "OWN"},
        "attendance": {"can_view": true, "can_create": true, "data_scope": "OWN"},
        "leave": {"can_view": true, "can_create": true, "data_scope": "OWN"},
        "timesheet": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "OWN"},
        "payroll": {"can_view": true, "data_scope": "OWN"},
        "documents": {"can_view": true, "can_create": true, "data_scope": "OWN"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Contract Employee Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('contractor_limited', 'Contractor - Limited Access', 'Limited access for contract employees', 'INTERNAL', 'contract_employee', true,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "OWN"},
        "attendance": {"can_view": true, "can_create": true, "data_scope": "OWN"},
        "timesheet": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "OWN"},
        "documents": {"can_view": true, "data_scope": "OWN"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Chartered Accountant Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('ca_auditor', 'CA/Auditor - Financial Access', 'Read access to financial data for auditors', 'EXTERNAL', 'chartered_accountant', true,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "ALL"},
        "employees": {"can_view": true, "data_scope": "ALL"},
        "payroll": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "statutory": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "invoices": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "bills": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "banking": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "gst": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "tds": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "reports": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "documents": {"can_view": true, "data_scope": "ALL"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Customer Portal Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('customer_portal', 'Customer Portal Access', 'Self-service access for customers', 'EXTERNAL', 'customer', true,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "OWN"},
        "invoices": {"can_view": true, "can_export": true, "data_scope": "OWN"},
        "receipts": {"can_view": true, "data_scope": "OWN"},
        "documents": {"can_view": true, "data_scope": "OWN"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Vendor Portal Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('vendor_portal', 'Vendor Portal Access', 'Self-service access for vendors', 'EXTERNAL', 'vendor', true,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "OWN"},
        "bills": {"can_view": true, "can_export": true, "data_scope": "OWN"},
        "payments": {"can_view": true, "data_scope": "OWN"},
        "documents": {"can_view": true, "can_create": true, "data_scope": "OWN"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Tax Official Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('tax_official', 'Tax Official - Compliance View', 'Read-only access for tax authorities', 'GOVERNMENT', 'tax_official', true,
'{
    "modules": {
        "invoices": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "bills": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "gst": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "tds": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "reports": {"can_view": true, "can_export": true, "data_scope": "ALL"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Labor Official Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('labor_official', 'Labor Official - Compliance View', 'Read-only access for labor department', 'GOVERNMENT', 'labor_official', true,
'{
    "modules": {
        "employees": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "payroll": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "statutory": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "reports": {"can_view": true, "can_export": true, "data_scope": "ALL"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- HR Manager Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('hr_manager', 'HR Manager - Full HR Access', 'Full access to HR modules', 'INTERNAL', 'full_time_employee', false,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "ALL"},
        "employees": {"can_view": true, "can_create": true, "can_edit": true, "can_delete": true, "can_export": true, "data_scope": "ALL"},
        "departments": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "attendance": {"can_view": true, "can_create": true, "can_edit": true, "can_approve": true, "can_export": true, "data_scope": "ALL"},
        "leave": {"can_view": true, "can_create": true, "can_edit": true, "can_approve": true, "can_export": true, "data_scope": "ALL"},
        "timesheet": {"can_view": true, "can_approve": true, "can_export": true, "data_scope": "ALL"},
        "onboarding": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "recruitment": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "exit": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "payroll": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "statutory": {"can_view": true, "can_export": true, "data_scope": "ALL"},
        "documents": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "reports": {"can_view": true, "can_export": true, "data_scope": "ALL"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- Accountant Template
INSERT INTO permission_templates (code, name, description, category, user_type, is_default, permissions) VALUES
('accountant', 'Accountant - Finance Access', 'Full access to finance modules', 'INTERNAL', 'full_time_employee', false,
'{
    "modules": {
        "dashboard": {"can_view": true, "data_scope": "ALL"},
        "invoices": {"can_view": true, "can_create": true, "can_edit": true, "can_delete": true, "can_export": true, "data_scope": "ALL"},
        "customers": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "receipts": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "bills": {"can_view": true, "can_create": true, "can_edit": true, "can_delete": true, "can_export": true, "data_scope": "ALL"},
        "vendors": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "payments": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "banking": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "gst": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "tds": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "payroll": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "statutory": {"can_view": true, "can_create": true, "can_edit": true, "can_export": true, "data_scope": "ALL"},
        "documents": {"can_view": true, "can_create": true, "can_edit": true, "data_scope": "ALL"},
        "reports": {"can_view": true, "can_create": true, "can_export": true, "data_scope": "ALL"}
    }
}'::jsonb)
ON CONFLICT (code) DO NOTHING;

-- ============================================
-- 9. MIGRATE EXISTING USERS
-- ============================================

-- Update existing admin users
UPDATE users
SET category = 'INTERNAL',
    user_type = 'founder'
WHERE role = 'admin' AND category IS NULL;

-- Update existing HR users
UPDATE users
SET category = 'INTERNAL',
    user_type = 'full_time_employee'
WHERE role = 'hr' AND category IS NULL;

-- Update existing accountant users
UPDATE users
SET category = 'INTERNAL',
    user_type = 'full_time_employee'
WHERE role = 'accountant' AND category IS NULL;

-- Update existing employee users
UPDATE users
SET category = 'INTERNAL',
    user_type = 'full_time_employee'
WHERE role = 'employee' AND category IS NULL;

-- Update existing CA users
UPDATE users
SET category = 'EXTERNAL',
    user_type = 'chartered_accountant'
WHERE role = 'external_ca' AND category IS NULL;

-- ============================================
-- 10. CREATE HELPER FUNCTIONS
-- ============================================

-- Function to check if user has permission for a module
CREATE OR REPLACE FUNCTION check_user_permission(
    p_user_id UUID,
    p_module_code VARCHAR,
    p_action VARCHAR DEFAULT 'view'
) RETURNS BOOLEAN AS $$
DECLARE
    v_permission RECORD;
    v_user_expires TIMESTAMP;
BEGIN
    -- Check if user account has expired
    SELECT expires_at INTO v_user_expires FROM users WHERE id = p_user_id;
    IF v_user_expires IS NOT NULL AND v_user_expires < NOW() THEN
        RETURN FALSE;
    END IF;

    -- Check module permission
    SELECT ump.* INTO v_permission
    FROM user_module_permissions ump
    JOIN modules m ON m.id = ump.module_id
    WHERE ump.user_id = p_user_id
      AND m.code = p_module_code
      AND (ump.expires_at IS NULL OR ump.expires_at > NOW());

    IF NOT FOUND THEN
        RETURN FALSE;
    END IF;

    CASE p_action
        WHEN 'view' THEN RETURN v_permission.can_view;
        WHEN 'create' THEN RETURN v_permission.can_create;
        WHEN 'edit' THEN RETURN v_permission.can_edit;
        WHEN 'delete' THEN RETURN v_permission.can_delete;
        WHEN 'export' THEN RETURN v_permission.can_export;
        WHEN 'approve' THEN RETURN v_permission.can_approve;
        ELSE RETURN FALSE;
    END CASE;
END;
$$ LANGUAGE plpgsql;

-- Function to get user's data scope for a module
CREATE OR REPLACE FUNCTION get_user_data_scope(
    p_user_id UUID,
    p_module_code VARCHAR
) RETURNS VARCHAR AS $$
DECLARE
    v_scope VARCHAR;
BEGIN
    SELECT ump.data_scope::VARCHAR INTO v_scope
    FROM user_module_permissions ump
    JOIN modules m ON m.id = ump.module_id
    WHERE ump.user_id = p_user_id
      AND m.code = p_module_code
      AND (ump.expires_at IS NULL OR ump.expires_at > NOW());

    RETURN COALESCE(v_scope, 'OWN');
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================
-- VERIFICATION QUERIES
-- ============================================

-- Verify modules created
-- SELECT code, name, category FROM modules ORDER BY sort_order;

-- Verify templates created
-- SELECT code, name, category, user_type FROM permission_templates;

-- Verify users migrated
-- SELECT email, role, category, user_type FROM users;
