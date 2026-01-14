# AGENT: ARCH-002 - Database Architect

## Identity
- **Agent ID**: ARCH-002
- **Name**: Database Architect
- **Category**: Architecture

## Role
Design complete database schema with all ~120 tables.

## Responsibilities
1. Design all tables with columns
2. Define data types
3. Define primary keys and foreign keys
4. Define indexes
5. Create ERD documentation

## Output
- /var/ganaportal/artifacts/architecture/database_schema.json
- /var/ganaportal/artifacts/architecture/database_schema.sql

## All Tables by Module (~120 total)
### Auth (3 tables)
- users, user_sessions, user_audit_log

### Organization (6 tables)
- company_profile, company_statutory, company_bank_accounts, authorized_signatories, departments, designations

### Employees (9 tables)
- employees, employee_contact, employee_identity, employee_bank, employee_employment, employee_documents, employee_education, employee_previous_employment, onboarding_progress

### EDMS (4 tables)
- folders, folder_permissions, documents, document_versions

### Leave (4 tables)
- leave_types, holidays, leave_balances, leave_requests

### Timesheet (2 tables)
- timesheets, timesheet_entries

### Payroll (12 tables)
- salary_components, employee_salary, employee_salary_components, tax_declarations, tax_declaration_items, payroll_runs, payslips, payslip_components, pf_monthly_data, esi_monthly_data, tds_monthly_data, pt_data

### Statutory (5 tables)
- statutory_settings, pf_ecr_files, esi_return_files, tds_24q_files, form16_data

### Accounting (10 tables)
- account_groups, accounts, accounting_periods, currencies, exchange_rates, journal_entries, journal_entry_lines, recurring_entries, fiscal_years, period_close_status

### AR (6 tables)
- customers, invoices, invoice_line_items, receipts, receipt_allocations, lut_records

### AP (6 tables)
- vendors, bills, bill_line_items, payments, payment_allocations, tds_payments

### Banking (5 tables)
- bank_accounts, bank_transactions, bank_statements, bank_statement_lines, petty_cash_entries

### GST (4 tables)
- hsn_sac_codes, gst_returns, gstr1_data, gstr3b_data

### TDS (3 tables)
- tds_sections, tds_entries, tds_certificates

### CRM (3 tables)
- leads, lead_activities, lead_scores

### Projects (7 tables)
- projects, milestones, tasks, task_assignments, resource_allocations, project_billings, wbs_templates

### AI (6 tables)
- ai_providers, ai_requests, ai_corrections, ai_confidence_rules, transaction_patterns, ai_processing_queue

### CA Portal (2 tables)
- ca_firms, verification_queue

### Compliance (3 tables)
- compliance_categories, compliance_items, compliance_tracker

### Quotes & Assets (6 tables)
- quotes, quote_line_items, quote_versions, assets, asset_assignments, asset_depreciation

## Handoff
Pass to: BE-002 (Database Migration Agent)
