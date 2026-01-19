-- Create 42 missing ORM tables in database
-- Generated based on SQLAlchemy model definitions
-- Execute: sudo -u postgres psql -d ganaportal_db -f create_missing_tables.sql

BEGIN;

-- Enable uuid-ossp extension if not exists
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================
-- 1. PARTIES (Customer/Vendor master) - Referenced by many tables
-- ====================
CREATE TABLE IF NOT EXISTS parties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    code VARCHAR(20) NOT NULL,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    party_type VARCHAR(20) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    website VARCHAR(255),
    pan VARCHAR(10),
    gstin VARCHAR(15),
    gst_registration_type VARCHAR(30) DEFAULT 'regular',
    tan VARCHAR(10),
    tds_applicable BOOLEAN DEFAULT FALSE,
    tds_section VARCHAR(20),
    tds_rate NUMERIC(5,2),
    lower_deduction_certificate BOOLEAN DEFAULT FALSE,
    ldc_rate NUMERIC(5,2),
    ldc_valid_from TIMESTAMP WITH TIME ZONE,
    ldc_valid_to TIMESTAMP WITH TIME ZONE,
    ldc_certificate_number VARCHAR(50),
    payment_terms VARCHAR(20) DEFAULT 'net_30',
    credit_days INTEGER DEFAULT 30,
    credit_limit NUMERIC(18,2) DEFAULT 0,
    default_currency VARCHAR(3) DEFAULT 'INR',
    price_list_id UUID,
    bank_name VARCHAR(255),
    bank_account_number VARCHAR(50),
    bank_ifsc VARCHAR(20),
    bank_branch VARCHAR(255),
    receivable_account_id UUID REFERENCES accounts(id),
    payable_account_id UUID REFERENCES accounts(id),
    outstanding_receivable NUMERIC(18,2) DEFAULT 0,
    outstanding_payable NUMERIC(18,2) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    CONSTRAINT uq_company_party_code UNIQUE (company_id, code)
);

CREATE INDEX IF NOT EXISTS ix_parties_company_id ON parties(company_id);

-- ====================
-- 2. PARTY ADDRESSES
-- ====================
CREATE TABLE IF NOT EXISTS party_addresses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_id UUID NOT NULL REFERENCES parties(id),
    address_type VARCHAR(20) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    state_code VARCHAR(2),
    pincode VARCHAR(10) NOT NULL,
    country VARCHAR(100) DEFAULT 'India',
    gstin VARCHAR(15),
    contact_person VARCHAR(255),
    phone VARCHAR(20),
    email VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_party_addresses_party_id ON party_addresses(party_id);

-- ====================
-- 3. PARTY CONTACTS
-- ====================
CREATE TABLE IF NOT EXISTS party_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    party_id UUID NOT NULL REFERENCES parties(id),
    name VARCHAR(255) NOT NULL,
    designation VARCHAR(100),
    department VARCHAR(100),
    email VARCHAR(255),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    is_primary BOOLEAN DEFAULT FALSE,
    is_billing_contact BOOLEAN DEFAULT FALSE,
    is_shipping_contact BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_party_contacts_party_id ON party_contacts(party_id);

-- ====================
-- 4. FINANCIAL YEARS
-- ====================
CREATE TABLE IF NOT EXISTS financial_years (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(20) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    is_active BOOLEAN DEFAULT FALSE,
    is_locked BOOLEAN DEFAULT FALSE,
    locked_at TIMESTAMP WITH TIME ZONE,
    locked_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_company_fy_name UNIQUE (company_id, name)
);

CREATE INDEX IF NOT EXISTS ix_financial_years_company_id ON financial_years(company_id);

-- ====================
-- 5. JOURNAL LINES
-- ====================
CREATE TABLE IF NOT EXISTS journal_lines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    journal_entry_id UUID NOT NULL REFERENCES journal_entries(id),
    line_number INTEGER NOT NULL,
    account_id UUID NOT NULL REFERENCES accounts(id),
    description VARCHAR(500),
    debit_amount NUMERIC(18,2) DEFAULT 0,
    credit_amount NUMERIC(18,2) DEFAULT 0,
    party_id UUID REFERENCES parties(id),
    cost_center_id UUID REFERENCES cost_centers(id),
    project_id UUID REFERENCES projects(id),
    tax_code VARCHAR(20),
    tax_amount NUMERIC(18,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_journal_lines_entry_id ON journal_lines(journal_entry_id);
CREATE INDEX IF NOT EXISTS ix_journal_lines_account_id ON journal_lines(account_id);

-- ====================
-- 6. GENERAL LEDGER
-- ====================
CREATE TABLE IF NOT EXISTS general_ledger (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    journal_entry_id UUID REFERENCES journal_entries(id),
    journal_line_id UUID REFERENCES journal_lines(id),
    posting_date DATE NOT NULL,
    value_date DATE,
    financial_year VARCHAR(9) NOT NULL,
    period INTEGER NOT NULL,
    voucher_type VARCHAR(50),
    voucher_number VARCHAR(50),
    description VARCHAR(500),
    debit_amount NUMERIC(18,2) DEFAULT 0,
    credit_amount NUMERIC(18,2) DEFAULT 0,
    balance NUMERIC(18,2) DEFAULT 0,
    party_id UUID REFERENCES parties(id),
    cost_center_id UUID REFERENCES cost_centers(id),
    project_id UUID REFERENCES projects(id),
    reference_type VARCHAR(50),
    reference_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_general_ledger_company_account ON general_ledger(company_id, account_id);
CREATE INDEX IF NOT EXISTS ix_general_ledger_posting_date ON general_ledger(posting_date);

-- ====================
-- 7. BUDGET ENTRIES
-- ====================
CREATE TABLE IF NOT EXISTS budget_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    account_id UUID NOT NULL REFERENCES accounts(id),
    cost_center_id UUID REFERENCES cost_centers(id),
    financial_year VARCHAR(9) NOT NULL,
    period INTEGER NOT NULL,
    budget_amount NUMERIC(18,2) DEFAULT 0,
    actual_amount NUMERIC(18,2) DEFAULT 0,
    variance NUMERIC(18,2) DEFAULT 0,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_budget_entries_company_fy ON budget_entries(company_id, financial_year);

-- ====================
-- 8. INVOICE ITEMS
-- ====================
CREATE TABLE IF NOT EXISTS invoice_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id),
    line_number INTEGER NOT NULL,
    item_type VARCHAR(20) DEFAULT 'service',
    product_id UUID,
    service_id UUID,
    description VARCHAR(500) NOT NULL,
    hsn_sac_code VARCHAR(20),
    quantity NUMERIC(18,4) DEFAULT 1,
    uom VARCHAR(20) DEFAULT 'NOS',
    unit_price NUMERIC(18,4) NOT NULL,
    discount_percent NUMERIC(5,2) DEFAULT 0,
    discount_amount NUMERIC(18,2) DEFAULT 0,
    taxable_amount NUMERIC(18,2) NOT NULL,
    gst_rate NUMERIC(5,2) DEFAULT 18,
    cgst_rate NUMERIC(5,2) DEFAULT 0,
    cgst_amount NUMERIC(18,2) DEFAULT 0,
    sgst_rate NUMERIC(5,2) DEFAULT 0,
    sgst_amount NUMERIC(18,2) DEFAULT 0,
    igst_rate NUMERIC(5,2) DEFAULT 0,
    igst_amount NUMERIC(18,2) DEFAULT 0,
    cess_rate NUMERIC(5,2) DEFAULT 0,
    cess_amount NUMERIC(18,2) DEFAULT 0,
    total_amount NUMERIC(18,2) NOT NULL,
    income_account_id UUID REFERENCES accounts(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_invoice_items_invoice_id ON invoice_items(invoice_id);

-- ====================
-- 9. INVOICE PAYMENTS
-- ====================
CREATE TABLE IF NOT EXISTS invoice_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    invoice_id UUID NOT NULL REFERENCES invoices(id),
    payment_id UUID NOT NULL REFERENCES payments(id),
    amount_applied NUMERIC(18,2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_invoice_payments_invoice_id ON invoice_payments(invoice_id);
CREATE INDEX IF NOT EXISTS ix_invoice_payments_payment_id ON invoice_payments(payment_id);

-- ====================
-- 10. BILL ITEMS
-- ====================
CREATE TABLE IF NOT EXISTS bill_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID NOT NULL REFERENCES bills(id),
    line_number INTEGER NOT NULL,
    item_type VARCHAR(20) DEFAULT 'expense',
    product_id UUID,
    service_id UUID,
    description VARCHAR(500) NOT NULL,
    hsn_sac_code VARCHAR(20),
    quantity NUMERIC(18,4) DEFAULT 1,
    uom VARCHAR(20) DEFAULT 'NOS',
    unit_price NUMERIC(18,4) NOT NULL,
    discount_percent NUMERIC(5,2) DEFAULT 0,
    discount_amount NUMERIC(18,2) DEFAULT 0,
    taxable_amount NUMERIC(18,2) NOT NULL,
    gst_rate NUMERIC(5,2) DEFAULT 18,
    cgst_rate NUMERIC(5,2) DEFAULT 0,
    cgst_amount NUMERIC(18,2) DEFAULT 0,
    sgst_rate NUMERIC(5,2) DEFAULT 0,
    sgst_amount NUMERIC(18,2) DEFAULT 0,
    igst_rate NUMERIC(5,2) DEFAULT 0,
    igst_amount NUMERIC(18,2) DEFAULT 0,
    cess_rate NUMERIC(5,2) DEFAULT 0,
    cess_amount NUMERIC(18,2) DEFAULT 0,
    total_amount NUMERIC(18,2) NOT NULL,
    expense_account_id UUID REFERENCES accounts(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_bill_items_bill_id ON bill_items(bill_id);

-- ====================
-- 11. BILL PAYMENTS
-- ====================
CREATE TABLE IF NOT EXISTS bill_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    bill_id UUID NOT NULL REFERENCES bills(id),
    payment_id UUID NOT NULL REFERENCES payments(id),
    amount_applied NUMERIC(18,2) NOT NULL,
    tds_amount NUMERIC(18,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_bill_payments_bill_id ON bill_payments(bill_id);
CREATE INDEX IF NOT EXISTS ix_bill_payments_payment_id ON bill_payments(payment_id);

-- ====================
-- 12. ADVANCE PAYMENTS
-- ====================
CREATE TABLE IF NOT EXISTS advance_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    payment_id UUID NOT NULL REFERENCES payments(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    party_id UUID NOT NULL REFERENCES parties(id),
    party_type VARCHAR(20),
    advance_amount NUMERIC(18,2) NOT NULL,
    utilized_amount NUMERIC(18,2) DEFAULT 0,
    balance_amount NUMERIC(18,2),
    is_fully_utilized BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_advance_payments_party_id ON advance_payments(party_id);

-- ====================
-- 13. GST TABLES (GSTR1, GSTR2A, GSTR3B)
-- ====================
CREATE TABLE IF NOT EXISTS gstr1 (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    return_period VARCHAR(7) NOT NULL,
    financial_year VARCHAR(9) NOT NULL,
    filing_status VARCHAR(20) DEFAULT 'pending',
    b2b_invoices JSONB DEFAULT '[]',
    b2c_large JSONB DEFAULT '[]',
    b2c_small JSONB DEFAULT '[]',
    credit_debit_notes JSONB DEFAULT '[]',
    exports JSONB DEFAULT '[]',
    nil_rated JSONB DEFAULT '[]',
    hsn_summary JSONB DEFAULT '[]',
    advances JSONB DEFAULT '[]',
    adjustment_advances JSONB DEFAULT '[]',
    total_taxable_value NUMERIC(18,2) DEFAULT 0,
    total_igst NUMERIC(18,2) DEFAULT 0,
    total_cgst NUMERIC(18,2) DEFAULT 0,
    total_sgst NUMERIC(18,2) DEFAULT 0,
    total_cess NUMERIC(18,2) DEFAULT 0,
    json_file_path TEXT,
    arn_number VARCHAR(50),
    filed_at TIMESTAMP WITH TIME ZONE,
    filed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_gstr1_company_period ON gstr1(company_id, return_period);

CREATE TABLE IF NOT EXISTS gstr2a (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    return_period VARCHAR(7) NOT NULL,
    financial_year VARCHAR(9) NOT NULL,
    supplier_gstin VARCHAR(15),
    supplier_name VARCHAR(255),
    invoice_number VARCHAR(50),
    invoice_date DATE,
    invoice_type VARCHAR(20),
    place_of_supply VARCHAR(2),
    is_reverse_charge BOOLEAN DEFAULT FALSE,
    taxable_value NUMERIC(18,2) DEFAULT 0,
    igst_amount NUMERIC(18,2) DEFAULT 0,
    cgst_amount NUMERIC(18,2) DEFAULT 0,
    sgst_amount NUMERIC(18,2) DEFAULT 0,
    cess_amount NUMERIC(18,2) DEFAULT 0,
    total_amount NUMERIC(18,2) DEFAULT 0,
    matched_bill_id UUID REFERENCES bills(id),
    match_status VARCHAR(20) DEFAULT 'pending',
    action_taken VARCHAR(20),
    remarks TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_gstr2a_company_period ON gstr2a(company_id, return_period);

CREATE TABLE IF NOT EXISTS gstr3b (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    return_period VARCHAR(7) NOT NULL,
    financial_year VARCHAR(9) NOT NULL,
    filing_status VARCHAR(20) DEFAULT 'pending',
    outward_taxable_supplies JSONB DEFAULT '{}',
    outward_taxable_zero_rated JSONB DEFAULT '{}',
    outward_taxable_nil_rated JSONB DEFAULT '{}',
    inward_reverse_charge JSONB DEFAULT '{}',
    itc_available JSONB DEFAULT '{}',
    itc_reversed JSONB DEFAULT '{}',
    itc_net JSONB DEFAULT '{}',
    exempt_inward_supplies JSONB DEFAULT '{}',
    interest NUMERIC(18,2) DEFAULT 0,
    late_fee NUMERIC(18,2) DEFAULT 0,
    tax_payable_igst NUMERIC(18,2) DEFAULT 0,
    tax_payable_cgst NUMERIC(18,2) DEFAULT 0,
    tax_payable_sgst NUMERIC(18,2) DEFAULT 0,
    tax_payable_cess NUMERIC(18,2) DEFAULT 0,
    tax_paid_igst NUMERIC(18,2) DEFAULT 0,
    tax_paid_cgst NUMERIC(18,2) DEFAULT 0,
    tax_paid_sgst NUMERIC(18,2) DEFAULT 0,
    tax_paid_cess NUMERIC(18,2) DEFAULT 0,
    arn_number VARCHAR(50),
    filed_at TIMESTAMP WITH TIME ZONE,
    filed_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_gstr3b_company_period ON gstr3b(company_id, return_period);

-- ====================
-- 14. HSN SUMMARY
-- ====================
CREATE TABLE IF NOT EXISTS hsn_summary (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    return_period VARCHAR(7) NOT NULL,
    hsn_code VARCHAR(20) NOT NULL,
    description VARCHAR(500),
    uom VARCHAR(20),
    total_quantity NUMERIC(18,4) DEFAULT 0,
    total_taxable_value NUMERIC(18,2) DEFAULT 0,
    total_igst NUMERIC(18,2) DEFAULT 0,
    total_cgst NUMERIC(18,2) DEFAULT 0,
    total_sgst NUMERIC(18,2) DEFAULT 0,
    total_cess NUMERIC(18,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_hsn_summary_company_period ON hsn_summary(company_id, return_period);

-- ====================
-- 15. GST LEDGER
-- ====================
CREATE TABLE IF NOT EXISTS gst_ledger (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    ledger_type VARCHAR(20) NOT NULL,
    tax_type VARCHAR(10) NOT NULL,
    return_period VARCHAR(7) NOT NULL,
    opening_balance NUMERIC(18,2) DEFAULT 0,
    tax_collected NUMERIC(18,2) DEFAULT 0,
    tax_paid NUMERIC(18,2) DEFAULT 0,
    itc_available NUMERIC(18,2) DEFAULT 0,
    itc_utilized NUMERIC(18,2) DEFAULT 0,
    interest NUMERIC(18,2) DEFAULT 0,
    late_fee NUMERIC(18,2) DEFAULT 0,
    other_adjustments NUMERIC(18,2) DEFAULT 0,
    closing_balance NUMERIC(18,2) DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_gst_ledger_company_period ON gst_ledger(company_id, return_period);

-- ====================
-- 16. ITC TRACKING
-- ====================
CREATE TABLE IF NOT EXISTS itc_tracking (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    financial_year VARCHAR(9) NOT NULL,
    return_period VARCHAR(7) NOT NULL,
    supplier_gstin VARCHAR(15),
    supplier_name VARCHAR(255),
    invoice_number VARCHAR(50),
    invoice_date DATE,
    bill_id UUID REFERENCES bills(id),
    igst_amount NUMERIC(18,2) DEFAULT 0,
    cgst_amount NUMERIC(18,2) DEFAULT 0,
    sgst_amount NUMERIC(18,2) DEFAULT 0,
    cess_amount NUMERIC(18,2) DEFAULT 0,
    total_itc NUMERIC(18,2) DEFAULT 0,
    itc_type VARCHAR(20) DEFAULT 'inputs',
    is_eligible BOOLEAN DEFAULT TRUE,
    ineligible_reason VARCHAR(255),
    is_reversed BOOLEAN DEFAULT FALSE,
    reversed_amount NUMERIC(18,2) DEFAULT 0,
    reversed_reason VARCHAR(255),
    gstr2a_match_status VARCHAR(20) DEFAULT 'pending',
    claimed_in_period VARCHAR(7),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_itc_tracking_company_fy ON itc_tracking(company_id, financial_year);

-- ====================
-- 17. REPORT TEMPLATES
-- ====================
CREATE TABLE IF NOT EXISTS report_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    code VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    description TEXT,
    report_type VARCHAR(50) NOT NULL,
    query_template TEXT,
    parameters JSONB DEFAULT '{}',
    columns JSONB DEFAULT '[]',
    filters JSONB DEFAULT '[]',
    default_sort JSONB DEFAULT '{}',
    output_formats JSONB DEFAULT '["pdf", "xlsx", "csv"]',
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_report_templates_company_id ON report_templates(company_id);

-- ====================
-- 18. REPORT SCHEDULES
-- ====================
CREATE TABLE IF NOT EXISTS report_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    template_id UUID NOT NULL REFERENCES report_templates(id),
    name VARCHAR(255) NOT NULL,
    schedule_type VARCHAR(20) NOT NULL,
    cron_expression VARCHAR(100),
    parameters JSONB DEFAULT '{}',
    output_format VARCHAR(20) DEFAULT 'pdf',
    recipients JSONB DEFAULT '[]',
    email_subject VARCHAR(255),
    email_body TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMP WITH TIME ZONE,
    next_run_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_report_schedules_company_id ON report_schedules(company_id);

-- ====================
-- 19. REPORT EXECUTIONS
-- ====================
CREATE TABLE IF NOT EXISTS report_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    template_id UUID NOT NULL REFERENCES report_templates(id),
    schedule_id UUID REFERENCES report_schedules(id),
    parameters JSONB DEFAULT '{}',
    output_format VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    file_path TEXT,
    file_size BIGINT,
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_report_executions_company_id ON report_executions(company_id);

-- ====================
-- 20. SAVED REPORTS
-- ====================
CREATE TABLE IF NOT EXISTS saved_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    template_id UUID NOT NULL REFERENCES report_templates(id),
    name VARCHAR(255) NOT NULL,
    parameters JSONB DEFAULT '{}',
    filters JSONB DEFAULT '{}',
    columns JSONB DEFAULT '[]',
    sort_order JSONB DEFAULT '{}',
    is_default BOOLEAN DEFAULT FALSE,
    is_shared BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_saved_reports_company_id ON saved_reports(company_id);

-- ====================
-- 21. AI TABLES
-- ====================
CREATE TABLE IF NOT EXISTS ai_conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    user_id UUID NOT NULL REFERENCES users(id),
    title VARCHAR(255),
    context_type VARCHAR(50),
    context_id UUID,
    provider VARCHAR(20) DEFAULT 'anthropic',
    model VARCHAR(50),
    total_tokens INTEGER DEFAULT 0,
    total_cost NUMERIC(10,6) DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    last_message_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_conversations_user_id ON ai_conversations(user_id);

CREATE TABLE IF NOT EXISTS ai_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES ai_conversations(id),
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    tokens INTEGER DEFAULT 0,
    model VARCHAR(50),
    finish_reason VARCHAR(50),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_messages_conversation_id ON ai_messages(conversation_id);

CREATE TABLE IF NOT EXISTS ai_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    user_id UUID NOT NULL REFERENCES users(id),
    feature VARCHAR(50) NOT NULL,
    provider VARCHAR(20) DEFAULT 'anthropic',
    model VARCHAR(50),
    input_tokens INTEGER DEFAULT 0,
    output_tokens INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    cost NUMERIC(10,6) DEFAULT 0,
    request_id VARCHAR(100),
    response_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_usage_company_id ON ai_usage(company_id);

CREATE TABLE IF NOT EXISTS ai_prompt_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    feature VARCHAR(50) NOT NULL,
    system_prompt TEXT,
    user_prompt_template TEXT NOT NULL,
    variables JSONB DEFAULT '[]',
    model VARCHAR(50),
    max_tokens INTEGER,
    temperature NUMERIC(3,2) DEFAULT 0.7,
    is_system BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS ai_quotas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    feature VARCHAR(50) NOT NULL,
    daily_limit INTEGER DEFAULT 100,
    monthly_limit INTEGER DEFAULT 2000,
    daily_used INTEGER DEFAULT 0,
    monthly_used INTEGER DEFAULT 0,
    last_daily_reset DATE,
    last_monthly_reset DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_ai_quotas_company_feature ON ai_quotas(company_id, feature);

CREATE TABLE IF NOT EXISTS ai_document_analyses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    document_id UUID NOT NULL REFERENCES documents(id),
    analysis_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    result JSONB DEFAULT '{}',
    confidence_score NUMERIC(5,4),
    tokens_used INTEGER DEFAULT 0,
    processing_time_ms INTEGER,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_ai_document_analyses_document_id ON ai_document_analyses(document_id);

-- ====================
-- 22. AUDIT LOGS
-- ====================
CREATE TABLE IF NOT EXISTS audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values TEXT,
    new_values TEXT,
    ip_address INET,
    user_agent VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS ix_audit_logs_entity ON audit_logs(entity_type, entity_id);

-- ====================
-- 23. DOCUMENT TABLES
-- ====================
CREATE TABLE IF NOT EXISTS document_templates (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(50) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    template_format VARCHAR(20) NOT NULL,
    template_path VARCHAR(500),
    template_content TEXT,
    variables TEXT,
    header_content TEXT,
    footer_content TEXT,
    include_letterhead BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    is_default BOOLEAN DEFAULT FALSE,
    created_by UUID NOT NULL REFERENCES users(id),
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_document_templates_company_id ON document_templates(company_id);

CREATE TABLE IF NOT EXISTS document_shares (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id),
    share_type VARCHAR(20) NOT NULL,
    shared_with_user UUID REFERENCES users(id),
    shared_with_email VARCHAR(255),
    share_token VARCHAR(100) UNIQUE,
    share_link VARCHAR(500),
    can_view BOOLEAN DEFAULT TRUE,
    can_download BOOLEAN DEFAULT TRUE,
    can_edit BOOLEAN DEFAULT FALSE,
    expires_at TIMESTAMP WITH TIME ZONE,
    max_downloads INTEGER,
    download_count INTEGER DEFAULT 0,
    is_password_protected BOOLEAN DEFAULT FALSE,
    password_hash VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    revoked_by UUID REFERENCES users(id),
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_document_shares_document_id ON document_shares(document_id);

CREATE TABLE IF NOT EXISTS document_audit_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id),
    action VARCHAR(50) NOT NULL,
    action_details TEXT,
    user_id UUID REFERENCES users(id),
    ip_address VARCHAR(45),
    user_agent VARCHAR(500),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_document_audit_logs_document_id ON document_audit_logs(document_id);

-- ====================
-- 24. SHIFT AND TIMESHEET TABLES
-- ====================
CREATE TABLE IF NOT EXISTS shift_schedules (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    name VARCHAR(100) NOT NULL,
    code VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    break_duration NUMERIC(4,2) DEFAULT 1,
    working_hours NUMERIC(4,2) NOT NULL,
    late_grace_minutes INTEGER DEFAULT 15,
    early_leave_grace_minutes INTEGER DEFAULT 15,
    half_day_hours NUMERIC(4,2),
    overtime_after_hours NUMERIC(4,2),
    min_overtime_minutes INTEGER DEFAULT 30,
    is_night_shift BOOLEAN DEFAULT FALSE,
    night_shift_allowance NUMERIC(10,2) DEFAULT 0,
    working_days TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT uq_company_shift_code UNIQUE (company_id, code)
);

CREATE INDEX IF NOT EXISTS ix_shift_schedules_company_id ON shift_schedules(company_id);

CREATE TABLE IF NOT EXISTS employee_shifts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id UUID NOT NULL REFERENCES employees(id),
    shift_id UUID NOT NULL REFERENCES shift_schedules(id),
    effective_from DATE NOT NULL,
    effective_to DATE,
    is_rotation BOOLEAN DEFAULT FALSE,
    rotation_pattern TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_employee_shifts_employee_id ON employee_shifts(employee_id);

CREATE TABLE IF NOT EXISTS overtime_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_number VARCHAR(20) UNIQUE NOT NULL,
    employee_id UUID NOT NULL REFERENCES employees(id),
    overtime_date DATE NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    hours_requested NUMERIC(4,2) NOT NULL,
    reason TEXT NOT NULL,
    project_id UUID REFERENCES projects(id),
    status VARCHAR(20) DEFAULT 'pending',
    approver_id UUID REFERENCES employees(id),
    approved_hours NUMERIC(4,2),
    approved_at TIMESTAMP WITH TIME ZONE,
    approver_remarks TEXT,
    compensation_type VARCHAR(20),
    hourly_rate NUMERIC(10,2),
    overtime_multiplier NUMERIC(3,2) DEFAULT 1.5,
    total_compensation NUMERIC(12,2),
    processed_in_payroll UUID,
    comp_off_created UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_overtime_requests_employee_id ON overtime_requests(employee_id);

-- ====================
-- 25. BANKING TABLES
-- ====================
CREATE TABLE IF NOT EXISTS bank_reconciliation_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    reconciliation_id UUID NOT NULL REFERENCES bank_reconciliations(id),
    bank_transaction_id UUID REFERENCES bank_transactions(id),
    item_type VARCHAR(50) NOT NULL,
    transaction_date DATE NOT NULL,
    reference_number VARCHAR(100),
    description VARCHAR(500),
    debit_amount NUMERIC(18,2) DEFAULT 0,
    credit_amount NUMERIC(18,2) DEFAULT 0,
    is_matched BOOLEAN DEFAULT FALSE,
    matched_with_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_bank_recon_items_recon_id ON bank_reconciliation_items(reconciliation_id);

CREATE TABLE IF NOT EXISTS bank_statement_imports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    bank_account_id UUID NOT NULL REFERENCES company_bank_accounts(id),
    file_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(500),
    file_format VARCHAR(20),
    statement_from DATE,
    statement_to DATE,
    total_records INTEGER DEFAULT 0,
    imported_records INTEGER DEFAULT 0,
    duplicate_records INTEGER DEFAULT 0,
    error_records INTEGER DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    error_message TEXT,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_bank_statement_imports_company_id ON bank_statement_imports(company_id);

CREATE TABLE IF NOT EXISTS cheque_register (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    bank_account_id UUID NOT NULL REFERENCES company_bank_accounts(id),
    cheque_number VARCHAR(20) NOT NULL,
    cheque_date DATE NOT NULL,
    payee_name VARCHAR(255) NOT NULL,
    party_id UUID REFERENCES parties(id),
    amount NUMERIC(18,2) NOT NULL,
    description VARCHAR(500),
    payment_id UUID REFERENCES payments(id),
    status VARCHAR(20) DEFAULT 'issued',
    presented_date DATE,
    cleared_date DATE,
    bounced_date DATE,
    cancelled_date DATE,
    stale_date DATE,
    bounce_reason VARCHAR(255),
    bounce_charges NUMERIC(18,2) DEFAULT 0,
    replaced_by_cheque VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id),
    CONSTRAINT uq_bank_cheque UNIQUE (bank_account_id, cheque_number)
);

CREATE INDEX IF NOT EXISTS ix_cheque_register_company_id ON cheque_register(company_id);

CREATE TABLE IF NOT EXISTS payment_batches (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    bank_account_id UUID NOT NULL REFERENCES company_bank_accounts(id),
    batch_number VARCHAR(50) NOT NULL,
    batch_type VARCHAR(20) NOT NULL,
    batch_date DATE NOT NULL,
    value_date DATE,
    description VARCHAR(500),
    reference VARCHAR(100),
    payment_mode VARCHAR(20) DEFAULT 'neft',
    total_amount NUMERIC(18,2) DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    processed_amount NUMERIC(18,2) DEFAULT 0,
    processed_count INTEGER DEFAULT 0,
    failed_amount NUMERIC(18,2) DEFAULT 0,
    failed_count INTEGER DEFAULT 0,
    status VARCHAR(30) DEFAULT 'draft',
    file_format VARCHAR(50),
    file_path VARCHAR(500),
    file_reference VARCHAR(100),
    file_generated_at TIMESTAMP WITH TIME ZONE,
    bank_batch_id VARCHAR(100),
    bank_response TEXT,
    source_type VARCHAR(50),
    source_id UUID,
    submitted_by UUID REFERENCES users(id),
    submitted_at TIMESTAMP WITH TIME ZONE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    processed_by UUID REFERENCES users(id),
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_payment_batches_company_id ON payment_batches(company_id);

CREATE TABLE IF NOT EXISTS payment_instructions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    batch_id UUID NOT NULL REFERENCES payment_batches(id),
    sequence_number INTEGER NOT NULL,
    beneficiary_name VARCHAR(255) NOT NULL,
    beneficiary_code VARCHAR(50),
    beneficiary_email VARCHAR(255),
    beneficiary_phone VARCHAR(20),
    account_number VARCHAR(50) NOT NULL,
    ifsc_code VARCHAR(20) NOT NULL,
    bank_name VARCHAR(255),
    branch_name VARCHAR(255),
    upi_id VARCHAR(100),
    amount NUMERIC(18,2) NOT NULL,
    narration VARCHAR(255),
    remarks VARCHAR(500),
    entity_type VARCHAR(50),
    entity_id UUID,
    payment_mode VARCHAR(20) DEFAULT 'neft',
    status VARCHAR(20) DEFAULT 'pending',
    validation_errors TEXT,
    utr_number VARCHAR(50),
    bank_reference VARCHAR(100),
    processed_at TIMESTAMP WITH TIME ZONE,
    response_code VARCHAR(20),
    response_message VARCHAR(500),
    bank_response TEXT,
    retry_count INTEGER DEFAULT 0,
    last_retry_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_payment_instructions_batch_id ON payment_instructions(batch_id);

-- ====================
-- 26. PROJECT TEAMS
-- ====================
CREATE TABLE IF NOT EXISTS project_teams (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id),
    employee_id UUID NOT NULL REFERENCES employees(id),
    role VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    allocation_percentage INTEGER DEFAULT 100,
    start_date DATE,
    end_date DATE,
    billing_rate NUMERIC(10,2),
    cost_rate NUMERIC(10,2),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_project_teams_project_id ON project_teams(project_id);
CREATE INDEX IF NOT EXISTS ix_project_teams_employee_id ON project_teams(employee_id);

-- ====================
-- 27. TIME ENTRIES
-- ====================
CREATE TABLE IF NOT EXISTS time_entries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_id UUID NOT NULL REFERENCES companies(id),
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    employee_id UUID NOT NULL REFERENCES employees(id),
    entry_date DATE NOT NULL,
    start_time TIMESTAMP WITH TIME ZONE,
    end_time TIMESTAMP WITH TIME ZONE,
    hours NUMERIC(6,2) NOT NULL,
    description TEXT,
    is_billable BOOLEAN DEFAULT TRUE,
    billing_rate NUMERIC(10,2),
    billing_amount NUMERIC(12,2),
    is_billed BOOLEAN DEFAULT FALSE,
    invoice_id UUID REFERENCES invoices(id),
    is_approved BOOLEAN DEFAULT FALSE,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_by UUID REFERENCES users(id)
);

CREATE INDEX IF NOT EXISTS ix_time_entries_employee_id ON time_entries(employee_id);
CREATE INDEX IF NOT EXISTS ix_time_entries_project_id ON time_entries(project_id);
CREATE INDEX IF NOT EXISTS ix_time_entries_entry_date ON time_entries(entry_date);

-- ====================
-- 28. GRANT PERMISSIONS
-- ====================
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO ganaportal_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO ganaportal_user;

COMMIT;

-- Verification query
SELECT
    'Tables created successfully! Total count: ' || COUNT(*)::text as status
FROM information_schema.tables
WHERE table_schema = 'public'
AND table_type = 'BASE TABLE';
