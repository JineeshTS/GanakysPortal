# GanaPortal - Phase 2 WBS
## Startup Operations & AI Autonomous Accounting

**Project:** GanaPortal - Phase 2 Extensions  
**Version:** 1.0  
**Date:** December 2025  
**Client:** Ganakys Codilla Apps (OPC) Private Limited  
**Prerequisite:** Phase 1 Complete (HRMS + Accounting + Projects)  

---

## Executive Summary

Phase 2 extends GanaPortal with startup-specific operational features and transforms the accounting module into a fully autonomous AI-driven system with CA firm oversight.

### Phase 2 Modules

| Module | Description | Priority |
|--------|-------------|----------|
| **AI Autonomous Accountant** | Claude AI handles 95% of bookkeeping automatically | Critical |
| **CA Verification Portal** | CA firm reviews, approves, and audits AI entries | Critical |
| **Compliance Tracker** | ROC, GST, TDS, PF filings with CA collaboration | High |
| **Quotes & Proposals** | Pre-sales quotes that convert to projects/invoices | High |
| **Asset Management** | IT assets, software licenses, depreciation | High |
| **Budget & Financial Planning** | Budget vs actual, runway, burn rate | Medium |
| **ESOP Management** | Stock options for employees | Medium |
| **Customer Support Portal** | Support tickets for your SaaS products | Medium |
| **Cap Table Management** | Shareholding, funding rounds | Low |

### Phase 2 Statistics

| Metric | Value |
|--------|-------|
| Total Phases | 9 (Phases 31-39) |
| Total Tasks | 260 |
| Total Hours | 1,040 |
| Estimated Timeline | 5-6 months (1 dev) |

### Combined Project Statistics (Phase 1 + Phase 2)

| Metric | Phase 1 | Phase 2 | Total |
|--------|---------|---------|-------|
| Tasks | 639 | 260 | 899 |
| Hours | 2,548 | 1,040 | 3,588 |
| Timeline (1 dev) | 12-14 months | 5-6 months | 18-20 months |
| Timeline (2 devs) | 6-8 months | 3-4 months | 10-12 months |

---

## Architecture: AI Autonomous Accounting

### System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    AI AUTONOMOUS ACCOUNTING SYSTEM                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                         INPUT CHANNELS                            │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  📄 Bank Statement    📧 Email Forward    💬 Natural Language    │   │
│  │     Upload               (bills@)           Commands              │   │
│  │                                                                   │   │
│  │  📑 Vendor Bill       🔄 Recurring        📱 Mobile Upload       │   │
│  │     Upload              Transactions                              │   │
│  │                                                                   │   │
│  └────────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│                               ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐   │
│  │                      CLAUDE AI AGENT                              │   │
│  ├──────────────────────────────────────────────────────────────────┤   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │  Document   │  │   Pattern   │  │ Confidence  │              │   │
│  │  │  Processor  │  │   Matcher   │  │   Scorer    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                   │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │   │
│  │  │  Category   │  │   Entry     │  │  Learning   │              │   │
│  │  │  Predictor  │  │  Generator  │  │   Engine    │              │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘              │   │
│  │                                                                   │   │
│  └────────────────────────────┬─────────────────────────────────────┘   │
│                               │                                          │
│              ┌────────────────┼────────────────┐                        │
│              ▼                ▼                ▼                        │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐               │
│  │  AUTO-POST    │  │   PENDING     │  │   FLAGGED     │               │
│  │  Conf > 95%   │  │  Conf 70-95%  │  │   Conf < 70%  │               │
│  │               │  │               │  │               │               │
│  │  No review    │  │  Batch review │  │  Manual entry │               │
│  │  needed       │  │  by CA        │  │  required     │               │
│  └───────────────┘  └───────┬───────┘  └───────────────┘               │
│                             │                                           │
│                             ▼                                           │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      CA FIRM PORTAL                               │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                   │  │
│  │  ✓ Approve    ✗ Reject    ✎ Correct    📊 Reports    📋 Audit   │  │
│  │                                                                   │  │
│  │  • Verification Queue       • Compliance Calendar                 │  │
│  │  • Correction Interface     • Filing Status                       │  │
│  │  • Audit Trail Access       • Document Repository                 │  │
│  │                                                                   │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### Role Responsibilities

| Role | Daily Tasks | System Access |
|------|-------------|---------------|
| **Founder (You)** | Upload statements, approve invoices, review AI alerts | Full |
| **Claude AI Agent** | Process documents, categorize, create entries, reconcile | Automated |
| **CA Firm** | Verify AI entries, correct mistakes, file returns, audit | `external_ca` role |

---

## PHASE 31: AI Autonomous Accountant (2 weeks)

### EPIC 31.1: Confidence Scoring System

#### FEATURE 31.1.1: AI Confidence Framework

##### STORY 31.1.1.1: Implement Confidence Scoring

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 31.1.1.1.1 | Create `ai_confidence_rules` table: id, rule_type ENUM ('vendor_match', 'category_match', 'amount_pattern', 'description_pattern', 'historical_match'), rule_name, rule_config (JSON), weight (DECIMAL, 0-1), is_active, created_at; defines what contributes to confidence | 4 |
| 31.1.1.1.2 | Create `transaction_patterns` table: id, pattern_type ENUM ('vendor', 'description', 'amount_range', 'recurring'), pattern_value (TEXT), matched_vendor_id, matched_category_account_id, occurrence_count (INT), last_seen_at, confidence_boost (DECIMAL), created_at, updated_at; stores learned patterns | 4 |
| 31.1.1.1.3 | Implement confidence calculation service: for each AI-processed transaction, calculate confidence based on: (1) exact vendor match = +30%, (2) fuzzy vendor match = +15%, (3) category seen before for vendor = +25%, (4) amount in expected range = +10%, (5) description keyword match = +10%, (6) recurring pattern = +10%; cap at 100% | 6 |
| 31.1.1.1.4 | Implement confidence thresholds config: create `ai_settings` table with thresholds: auto_post_threshold (default 95), review_threshold (default 70), flag_threshold (default 50); admin can adjust | 3 |
| 31.1.1.1.5 | Create confidence explanation service: for each scored transaction, generate human-readable explanation ("95% confident: Known vendor Adobe, category matches 15 previous transactions, amount within expected range") | 4 |

### EPIC 31.2: Auto-Posting Workflow

#### FEATURE 31.2.1: Automated Entry Processing

##### STORY 31.2.1.1: Implement Auto-Post System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 31.2.1.1.1 | Enhance `journal_entries` table: add ai_generated (BOOLEAN), ai_confidence (DECIMAL), ai_explanation (TEXT), review_status ENUM ('auto_posted', 'pending_review', 'approved', 'rejected', 'corrected'), reviewed_by (FK), reviewed_at, correction_notes (TEXT) | 4 |
| 31.2.1.1.2 | Implement auto-post decision service: after AI processes transaction, check confidence against thresholds; if > auto_post_threshold: create entry with status='auto_posted', post immediately; if > review_threshold: create entry with status='pending_review'; if < review_threshold: create entry with status='flagged', notify admin | 5 |
| 31.2.1.1.3 | Create `ai_processing_queue` table: id, source_type ENUM ('bank_statement', 'bill_upload', 'email_forward', 'natural_language', 'recurring'), source_id (UUID), source_data (JSON), status ENUM ('queued', 'processing', 'completed', 'failed', 'held'), priority (INT), scheduled_at, started_at, completed_at, result_entry_id, error_message | 4 |
| 31.2.1.1.4 | Implement queue processor service: background worker that processes queue items in priority order; handles rate limiting for Claude API; implements retry logic with exponential backoff | 6 |
| 31.2.1.1.5 | Implement batch processing mode: when bank statement uploaded, queue all transactions; process in batch; generate summary report ("45 transactions processed: 38 auto-posted, 5 pending review, 2 flagged") | 5 |
| 31.2.1.1.6 | Create POST /api/v1/ai/process-queue endpoint: trigger queue processing; useful for manual batch runs | 3 |
| 31.2.1.1.7 | Create GET /api/v1/ai/queue-status endpoint: return queue stats (pending, processing, completed today, failed) | 3 |

### EPIC 31.3: AI Learning Engine

#### FEATURE 31.3.1: Learn from Corrections

##### STORY 31.3.1.1: Implement Learning System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 31.3.1.1.1 | Create `ai_corrections` table: id, original_entry_id, correction_type ENUM ('category_change', 'vendor_change', 'amount_change', 'split_transaction', 'merge_transaction', 'delete'), original_value (JSON), corrected_value (JSON), corrected_by, corrected_at, applied_to_learning (BOOLEAN) | 4 |
| 31.3.1.1.2 | Implement correction capture service: when CA/admin corrects an AI entry, log the correction with before/after values; mark original entry as 'corrected' | 4 |
| 31.3.1.1.3 | Implement pattern learning service: analyze corrections; if vendor X categorized wrongly 3+ times, update transaction_patterns; if new vendor identified, create vendor record; if category pattern emerges, boost confidence for future | 6 |
| 31.3.1.1.4 | Implement learning feedback loop: scheduled job (daily) processes unprocessed corrections; updates patterns; recalculates confidence rules weights based on accuracy | 5 |
| 31.3.1.1.5 | Create GET /api/v1/ai/learning-stats endpoint: return AI performance metrics (accuracy rate, common corrections, patterns learned this month) | 4 |
| 31.3.1.1.6 | Implement accuracy tracking: track % of auto-posted entries that were later corrected; alert if accuracy drops below 90% | 4 |

### EPIC 31.4: Scheduled Automation

#### FEATURE 31.4.1: Automated Jobs

##### STORY 31.4.1.1: Setup Scheduled Processing

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 31.4.1.1.1 | Create `scheduled_jobs` table: id, job_type ENUM ('daily_briefing', 'reconciliation_check', 'overdue_alerts', 'compliance_reminder', 'learning_update', 'recurring_invoice'), schedule_cron (VARCHAR), last_run_at, next_run_at, is_active, config (JSON) | 3 |
| 31.4.1.1.2 | Implement job scheduler service: use APScheduler or Celery Beat; run jobs based on cron schedule; log executions | 5 |
| 31.4.1.1.3 | Implement daily briefing job: every morning 8 AM, generate AI briefing (cash position, pending receipts, bills due, compliance deadlines, anomalies); send via email or dashboard notification | 5 |
| 31.4.1.1.4 | Implement reconciliation check job: weekly, compare bank balance per statements vs book balance; flag discrepancies | 4 |
| 31.4.1.1.5 | Implement recurring transaction processor: identify recurring patterns (monthly subscriptions, salaries); on expected date, prompt user to confirm or auto-create if high confidence | 5 |
| 31.4.1.1.6 | Create GET /api/v1/ai/scheduled-jobs endpoint: list jobs with status and next run | 2 |
| 31.4.1.1.7 | Create POST /api/v1/ai/scheduled-jobs/{id}/run endpoint: manually trigger job | 2 |

---

## PHASE 32: CA Verification Portal (1.5 weeks)

### EPIC 32.1: CA User Role

#### FEATURE 32.1.1: External CA Access

##### STORY 32.1.1.1: Implement CA Role

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 32.1.1.1.1 | Add 'external_ca' to user role ENUM; update all role-checking dependencies | 3 |
| 32.1.1.1.2 | Define CA permissions matrix: full access to verification queue, compliance module, audit logs, financial reports; view-only for GL, AR, AP; upload to compliance EDMS folder; no access to HR, payroll processing, project management | 4 |
| 32.1.1.1.3 | Implement CA-specific authentication: optionally enable 2FA requirement for CA role; session timeout after 30 min inactivity; IP whitelist option | 4 |
| 32.1.1.1.4 | Create CA invitation flow: admin enters CA firm email; system sends invite with temporary password; CA sets password on first login; link CA user to `ca_firms` record | 4 |
| 32.1.1.1.5 | Create `ca_firms` table: id, firm_name, contact_person, email, phone, gstin, address, engagement_start_date, engagement_type ENUM ('accounting', 'audit', 'both'), is_active, created_at | 3 |

### EPIC 32.2: Verification Queue

#### FEATURE 32.2.1: Review Interface

##### STORY 32.2.1.1: Build Verification System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 32.2.2.1.1 | Implement GET /api/v1/ca/verification-queue endpoint: return all entries with review_status='pending_review'; include AI confidence, explanation, supporting document; sort by date, allow filter by type | 5 |
| 32.2.2.1.2 | Implement POST /api/v1/ca/entries/{id}/approve endpoint: update review_status='approved', set reviewed_by/at; if entry was draft, post it | 3 |
| 32.2.2.1.3 | Implement POST /api/v1/ca/entries/{id}/reject endpoint: update review_status='rejected', require rejection_reason; do not post entry; notify admin | 3 |
| 32.2.2.1.4 | Implement POST /api/v1/ca/entries/{id}/correct endpoint: accept corrected entry data; create correction record; update entry with new values; mark as 'corrected'; trigger learning | 5 |
| 32.2.2.1.5 | Implement POST /api/v1/ca/entries/bulk-approve endpoint: accept array of entry IDs; approve all; useful for batch review | 3 |
| 32.2.2.1.6 | Implement GET /api/v1/ca/auto-posted endpoint: return entries that were auto-posted in date range; for periodic review; flag if any seem incorrect | 4 |
| 32.2.2.1.7 | Implement GET /api/v1/ca/flagged endpoint: return entries with review_status='flagged' that need manual attention | 3 |

### EPIC 32.3: CA Dashboard

#### FEATURE 32.3.1: CA Interface

##### STORY 32.3.1.1: Build CA Frontend

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 32.3.3.1.1 | Build CA login page with firm branding option | 3 |
| 32.3.3.1.2 | Build CA dashboard at /ca: summary cards (pending review count, flagged count, auto-posted this week, accuracy rate); quick action buttons | 5 |
| 32.3.3.1.3 | Build verification queue page at /ca/queue: table with date, type, description, amount, AI confidence, actions; inline approve/reject; click to expand details | 6 |
| 32.3.3.1.4 | Build entry detail modal: show full entry with all lines, supporting document preview, AI explanation, similar past entries; edit form for corrections | 5 |
| 32.3.3.1.5 | Build auto-posted review page: list of auto-posted entries for spot-checking; mark as "reviewed" or "needs correction" | 4 |
| 32.3.3.1.6 | Build correction interface: side-by-side original vs corrected; category dropdown, vendor selector, amount edit; save triggers learning | 5 |
| 32.3.3.1.7 | Build CA audit log page: all actions taken by CA user with timestamps | 3 |
| 32.3.3.1.8 | Build CA financial reports access: P&L, Balance Sheet, Trial Balance, AR/AP aging - view and export only | 4 |

---

## PHASE 33: Compliance Tracker (1 week)

### EPIC 33.1: Compliance Master

#### FEATURE 33.1.1: Compliance Configuration

##### STORY 33.1.1.1: Setup Compliance System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 33.1.1.1.1 | Create `compliance_categories` table: id, name, code, description, is_active; seed: ROC, GST, TDS, PF, ESI, Income Tax, Professional Tax, LWF | 3 |
| 33.1.1.1.2 | Create `compliance_items` table: id, category_id, name, code, description, frequency ENUM ('monthly', 'quarterly', 'half_yearly', 'annual', 'event_based'), due_day (INT, day of month/quarter), due_month (INT, for annual), grace_days (INT), penalty_info (TEXT), form_number (VARCHAR), filing_portal (VARCHAR), is_active, created_at | 4 |
| 33.1.1.1.3 | Seed ROC compliance items: AOC-4 (annual, within 30 days of AGM), MGT-7A (annual, within 60 days of AGM), DIR-3 KYC (annual, 30 Sep), ADT-1 (annual, within 15 days of AGM), INC-20A (one-time, 180 days of incorporation), MSME-1 (half-yearly, 31 Oct & 30 Apr) | 3 |
| 33.1.1.1.4 | Seed GST compliance items: GSTR-1 (monthly, 11th), GSTR-3B (monthly, 20th), GSTR-9 (annual, 31 Dec), GSTR-9C (annual, if turnover > threshold) | 2 |
| 33.1.1.1.5 | Seed TDS compliance items: TDS Payment (monthly, 7th), 24Q (quarterly, 31st of following month), 26Q (quarterly), 27Q (quarterly), Form 16 (annual, 15 Jun), Form 16A (quarterly) | 2 |
| 33.1.1.1.6 | Seed other compliance items: PF ECR (monthly, 15th), ESI Return (monthly, 15th), Advance Tax (quarterly, 15th of Jun/Sep/Dec/Mar), ITR (annual, 31 Oct for companies), PT (monthly/annual per state) | 2 |

### EPIC 33.2: Compliance Tracking

#### FEATURE 33.2.1: Due Date Management

##### STORY 33.2.1.1: Track Compliance

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 33.2.1.1.1 | Create `compliance_tracker` table: id, compliance_item_id, period_identifier (VARCHAR, e.g., '2025-12' or 'Q3-2025' or 'FY-2025-26'), due_date (DATE), status ENUM ('upcoming', 'pending', 'in_progress', 'filed', 'acknowledged', 'overdue'), filed_date (DATE, nullable), acknowledgement_number (VARCHAR), acknowledgement_date (DATE), filed_by (FK, nullable - internal or CA), document_ids (UUID[], filed documents), notes (TEXT), created_at, updated_at | 4 |
| 33.2.1.1.2 | Implement due date calculation service: based on compliance_item frequency and rules, calculate actual due date for given period; handle weekends/holidays (move to next working day); handle special cases (AGM-based filings) | 6 |
| 33.2.1.1.3 | Implement compliance generation job: at start of each month, generate tracker entries for all compliance items due in next 60 days; avoid duplicates | 4 |
| 33.2.1.1.4 | Implement GET /api/v1/compliance endpoint: list tracker entries with filters (category, status, date_range); return with days_until_due calculated | 4 |
| 33.2.1.1.5 | Implement PUT /api/v1/compliance/{id} endpoint: update status, filed_date, acknowledgement; attach documents | 3 |
| 33.2.1.1.6 | Implement compliance reminder service: send email/notification at 30, 15, 7, 1 days before due; escalate overdue items daily | 4 |
| 33.2.1.1.7 | Implement overdue detection job: daily check, mark items past due_date as 'overdue'; notify admin and CA | 3 |

### EPIC 33.3: Compliance Frontend

#### FEATURE 33.3.1: Compliance UI

##### STORY 33.3.1.1: Build Compliance Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 33.3.1.1.1 | Build compliance dashboard at /compliance: cards showing upcoming (next 30 days), overdue, recently filed; monthly calendar view | 5 |
| 33.3.1.1.2 | Build compliance list page: filterable table with item name, category, due date, status, actions; status badges with colors | 4 |
| 33.3.1.1.3 | Build compliance detail modal: item details, status update form, document upload, acknowledgement entry, history log | 4 |
| 33.3.1.1.4 | Build compliance calendar view: month calendar with compliance items as events; click to open detail | 5 |
| 33.3.1.1.5 | Build compliance settings page (admin): manage items, add custom items, set reminder preferences | 4 |
| 33.3.1.1.6 | Add compliance widget to main dashboard: "3 compliance items due this week" with quick links | 2 |
| 33.3.1.1.7 | Add compliance section to CA dashboard: full access to view and update compliance items | 3 |

---

## PHASE 34: Quotes & Proposals (1.5 weeks)

### EPIC 34.1: Quote Management

#### FEATURE 34.1.1: Quote Creation

##### STORY 34.1.1.1: Build Quote System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 34.1.1.1.1 | Create `quotes` table: id, quote_number (unique), quote_type ENUM ('proposal', 'quotation', 'estimate'), customer_id (FK, nullable for prospects), prospect_name (VARCHAR, if no customer), prospect_email, prospect_company, lead_id (FK, nullable, link to CRM), project_type ENUM ('fixed_price', 'time_material', 'retainer', 'mixed'), title (VARCHAR 200), description (TEXT), valid_until (DATE), currency, exchange_rate, subtotal, discount_type ENUM ('percentage', 'fixed'), discount_value, discount_amount, tax_amount, total_amount, status ENUM ('draft', 'sent', 'viewed', 'accepted', 'rejected', 'expired', 'converted'), sent_at, viewed_at, accepted_at, rejected_at, rejection_reason, converted_project_id (FK, nullable), converted_invoice_id (FK, nullable), terms_and_conditions (TEXT), notes (TEXT), pdf_path, created_by, created_at, updated_at | 6 |
| 34.1.1.1.2 | Create `quote_line_items` table: id, quote_id, item_type ENUM ('service', 'product', 'milestone', 'phase', 'hourly', 'monthly'), description (TEXT), details (TEXT), hsn_sac_code, quantity, unit (VARCHAR), rate, amount, is_optional (BOOLEAN, for optional add-ons), display_order, created_at | 4 |
| 34.1.1.1.3 | Create `quote_versions` table: id, quote_id, version_number, snapshot (JSON, full quote data), change_summary (TEXT), created_by, created_at; track revisions | 3 |
| 34.1.1.1.4 | Implement quote number generation: format QT-{YEAR}-{SEQ} (e.g., QT-2026-001) | 2 |
| 34.1.1.1.5 | Implement POST /api/v1/quotes endpoint: create quote, optionally link to customer or lead; calculate totals | 5 |
| 34.1.1.1.6 | Implement GET /api/v1/quotes endpoint: list with filters (status, customer, date_range, created_by) | 4 |
| 34.1.1.1.7 | Implement GET /api/v1/quotes/{id} endpoint: full quote with line items and version history | 3 |
| 34.1.1.1.8 | Implement PUT /api/v1/quotes/{id} endpoint: update quote, if status != draft, create new version | 4 |
| 34.1.1.1.9 | Implement POST /api/v1/quotes/{id}/send endpoint: generate PDF, email to customer, update status='sent', record sent_at | 4 |

#### FEATURE 34.1.2: Quote Workflow

##### STORY 34.1.2.1: Quote Lifecycle

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 34.1.2.1.1 | Implement POST /api/v1/quotes/{id}/accept endpoint: update status='accepted', accepted_at; optionally auto-convert to project or invoice | 3 |
| 34.1.2.1.2 | Implement POST /api/v1/quotes/{id}/reject endpoint: update status='rejected', record rejection_reason | 2 |
| 34.1.2.1.3 | Implement POST /api/v1/quotes/{id}/convert-to-project endpoint: create project from quote (milestones from line items if fixed price, rates if T&M); link converted_project_id | 5 |
| 34.1.2.1.4 | Implement POST /api/v1/quotes/{id}/convert-to-invoice endpoint: create invoice from quote (for direct product/service sales); link converted_invoice_id | 4 |
| 34.1.2.1.5 | Implement quote expiry job: daily check, mark quotes past valid_until as 'expired'; notify creator | 3 |
| 34.1.2.1.6 | Implement duplicate quote: POST /api/v1/quotes/{id}/duplicate creates copy with new number | 2 |

### EPIC 34.2: Quote Documents

#### FEATURE 34.2.1: Quote PDF

##### STORY 34.2.1.1: Generate Quote Documents

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 34.2.1.1.1 | Create quote PDF template: company branding, customer/prospect details, quote title and description, line items table (grouped by phase/milestone if applicable), optional items section, totals, validity, terms, signature area | 6 |
| 34.2.1.1.2 | Implement POST /api/v1/quotes/{id}/generate-pdf endpoint | 3 |
| 34.2.1.1.3 | Implement quote email template: professional email with quote summary, PDF attachment, accept/reject links (optional: online acceptance) | 4 |
| 34.2.1.1.4 | Implement online quote viewer (optional): public URL with token for customer to view quote online, track 'viewed' status | 5 |

### EPIC 34.3: Quote Frontend

#### FEATURE 34.3.1: Quote UI

##### STORY 34.3.1.1: Build Quote Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 34.3.1.1.1 | Build quotes list page at /quotes: table with quote#, customer/prospect, title, amount, status, valid_until; status badges; filters and search | 5 |
| 34.3.1.1.2 | Build quote create/edit page: customer/prospect selector (or inline entry), line items builder with drag-to-reorder, optional items toggle, discount section, terms editor, preview panel | 8 |
| 34.3.1.1.3 | Build quote detail page: formatted quote view (similar to PDF), action buttons (send, accept, reject, convert, duplicate), version history tab | 5 |
| 34.3.1.1.4 | Build quote PDF preview modal: rendered PDF in browser | 3 |
| 34.3.1.1.5 | Add quote creation from lead: in CRM lead detail, "Create Quote" button pre-fills prospect info | 3 |
| 34.3.1.1.6 | Add quotes widget to CRM dashboard: recent quotes, pending quotes, conversion rate | 3 |

---

## PHASE 35: Asset Management (1 week)

### EPIC 35.1: Asset Master

#### FEATURE 35.1.1: Asset Setup

##### STORY 35.1.1.1: Create Asset System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 35.1.1.1.1 | Create `asset_categories` table: id, name, code, parent_id, depreciation_method ENUM ('straight_line', 'written_down', 'none'), useful_life_years (INT), depreciation_rate (DECIMAL), asset_account_id (FK), depreciation_account_id (FK), accumulated_depreciation_account_id (FK), is_active | 4 |
| 35.1.1.1.2 | Seed asset categories: IT Equipment (Laptops, Desktops, Monitors, Servers), Furniture (Desks, Chairs), Office Equipment (Printers, ACs), Software Licenses, Vehicles, Leasehold Improvements | 3 |
| 35.1.1.1.3 | Create `assets` table: id, asset_code (unique), name, description, category_id, serial_number (VARCHAR), model_number, manufacturer, purchase_date, purchase_price, vendor_id (FK), invoice_number, warranty_expiry_date, location (VARCHAR), status ENUM ('available', 'assigned', 'under_maintenance', 'disposed', 'lost'), condition ENUM ('new', 'good', 'fair', 'poor'), assigned_to_employee_id (FK, nullable), assigned_date, expected_return_date, notes (TEXT), document_ids (UUID[], purchase invoice, warranty docs), created_at, updated_at | 5 |
| 35.1.1.1.4 | Implement asset code generation: format AST-{CATEGORY_CODE}-{SEQ} (e.g., AST-LAP-001) | 2 |
| 35.1.1.1.5 | Implement asset CRUD endpoints: POST, GET (with filters), GET /{id}, PUT | 5 |
| 35.1.1.1.6 | Create `asset_assignments` table: id, asset_id, employee_id, assigned_date, returned_date (nullable), assigned_by, return_condition, notes; tracks assignment history | 3 |
| 35.1.1.1.7 | Implement POST /api/v1/assets/{id}/assign endpoint: assign asset to employee, create assignment record, update asset status and assigned_to | 4 |
| 35.1.1.1.8 | Implement POST /api/v1/assets/{id}/return endpoint: return asset, record condition, update status to 'available' | 3 |
| 35.1.1.1.9 | Implement GET /api/v1/employees/{id}/assets endpoint: list assets currently assigned to employee | 3 |

### EPIC 35.2: Software Licenses

#### FEATURE 35.2.1: License Tracking

##### STORY 35.2.1.1: Manage Software Licenses

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 35.2.1.1.1 | Create `software_licenses` table: id, software_name, vendor, license_type ENUM ('perpetual', 'subscription_monthly', 'subscription_annual', 'per_seat', 'site_license'), license_key (encrypted), purchase_date, expiry_date (nullable for perpetual), renewal_date, total_seats (INT, nullable), used_seats (INT), cost_per_period (DECIMAL), billing_cycle ENUM ('monthly', 'annual', 'one_time'), auto_renew (BOOLEAN), status ENUM ('active', 'expiring_soon', 'expired', 'cancelled'), vendor_id (FK, nullable), notes, document_ids, created_at, updated_at | 4 |
| 35.2.1.1.2 | Create `license_assignments` table: id, license_id, employee_id, assigned_date, revoked_date, assigned_by | 3 |
| 35.2.1.1.3 | Implement license CRUD endpoints | 4 |
| 35.2.1.1.4 | Implement license assignment/revocation endpoints | 3 |
| 35.2.1.1.5 | Implement license expiry alerts: 30/15/7 days before expiry, email notification; update status to 'expiring_soon' | 4 |
| 35.2.1.1.6 | Implement GET /api/v1/reports/license-costs endpoint: total monthly/annual software costs | 3 |

### EPIC 35.3: Depreciation

#### FEATURE 35.3.1: Asset Depreciation

##### STORY 35.3.1.1: Calculate Depreciation

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 35.3.1.1.1 | Create `asset_depreciation` table: id, asset_id, depreciation_date (DATE, typically month-end), opening_value, depreciation_amount, closing_value, accumulated_depreciation, journal_entry_id (FK), created_at | 3 |
| 35.3.1.1.2 | Implement depreciation calculation service: for each asset, based on category depreciation_method and rate; straight_line: (purchase_price / useful_life_years) / 12; written_down: current_value * rate / 12 | 5 |
| 35.3.1.1.3 | Implement monthly depreciation job: calculate depreciation for all active assets; create depreciation records; create journal entry (DR: Depreciation Expense, CR: Accumulated Depreciation) | 5 |
| 35.3.1.1.4 | Implement GET /api/v1/reports/depreciation endpoint: depreciation schedule by asset, by category; current book value | 4 |
| 35.3.1.1.5 | Implement asset disposal: POST /api/v1/assets/{id}/dispose records disposal, calculates gain/loss vs book value, creates journal entry | 4 |

### EPIC 35.4: Asset Frontend

#### FEATURE 35.4.1: Asset UI

##### STORY 35.4.1.1: Build Asset Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 35.4.1.1.1 | Build assets list page at /assets: table with filters (category, status, assigned_to); quick assign action | 5 |
| 35.4.1.1.2 | Build asset detail page: asset info, assignment history, depreciation schedule, maintenance log, documents | 5 |
| 35.4.1.1.3 | Build asset create/edit form: category selector, purchase info, document upload | 4 |
| 35.4.1.1.4 | Build asset assignment modal: employee selector, expected return date, notes | 3 |
| 35.4.1.1.5 | Build software licenses page at /assets/licenses: list with expiry highlighting, seat usage | 4 |
| 35.4.1.1.6 | Build my assets page for employees: assets currently assigned to logged-in user | 3 |
| 35.4.1.1.7 | Add asset count to employee profile page | 2 |

---

## PHASE 36: Budget & Financial Planning (1 week)

### EPIC 36.1: Budget Management

#### FEATURE 36.1.1: Budget Setup

##### STORY 36.1.1.1: Create Budget System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 36.1.1.1.1 | Create `budgets` table: id, name, financial_year, budget_type ENUM ('annual', 'quarterly', 'monthly', 'project'), status ENUM ('draft', 'approved', 'active', 'closed'), total_revenue, total_expense, net_budget, approved_by, approved_at, notes, created_by, created_at, updated_at | 4 |
| 36.1.1.1.2 | Create `budget_line_items` table: id, budget_id, account_id (FK), category (VARCHAR, for grouping), period_month (INT, 1-12), budgeted_amount, notes | 3 |
| 36.1.1.1.3 | Implement POST /api/v1/budgets endpoint: create budget with line items; validate account types (revenue/expense) | 4 |
| 36.1.1.1.4 | Implement GET /api/v1/budgets endpoint: list budgets with filters | 3 |
| 36.1.1.1.5 | Implement GET /api/v1/budgets/{id} endpoint: full budget with line items | 3 |
| 36.1.1.1.6 | Implement PUT /api/v1/budgets/{id} endpoint: update budget (only if draft or with revision tracking) | 3 |
| 36.1.1.1.7 | Implement POST /api/v1/budgets/{id}/approve endpoint: approve budget, activate | 2 |
| 36.1.1.1.8 | Implement budget template: copy previous year's budget as starting point | 3 |

#### FEATURE 36.1.2: Budget vs Actual

##### STORY 36.1.2.1: Compare Budget to Actuals

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 36.1.2.1.1 | Implement budget vs actual calculation service: for each budget line item, get actual amount from GL for same account and period; calculate variance (absolute and %) | 5 |
| 36.1.2.1.2 | Implement GET /api/v1/reports/budget-vs-actual endpoint: return budget, actual, variance for each line item; support period filter (month, quarter, YTD) | 5 |
| 36.1.2.1.3 | Implement variance alerts: if actual exceeds budget by configurable threshold (e.g., 20%), send alert | 3 |
| 36.1.2.1.4 | Implement AI budget insights: analyze variances, explain significant deviations, predict full-year based on run rate | 5 |

### EPIC 36.2: Runway & Burn Rate

#### FEATURE 36.2.1: Cash Runway

##### STORY 36.2.1.1: Calculate Runway

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 36.2.1.1.1 | Implement burn rate calculation service: average monthly expense over last 3/6 months; separate operating vs total burn; include payroll, rent, subscriptions, other | 4 |
| 36.2.1.1.2 | Implement runway calculation: current cash position / monthly burn rate = months of runway; factor in expected revenue | 4 |
| 36.2.1.1.3 | Implement GET /api/v1/reports/runway endpoint: return current cash, burn rate (3m, 6m, 12m average), runway months, projected zero cash date | 4 |
| 36.2.1.1.4 | Implement runway projection with revenue: factor in AR aging (expected collections), committed revenue, seasonality | 5 |
| 36.2.1.1.5 | Implement runway alerts: if runway < 6 months, alert; if < 3 months, critical alert | 3 |

### EPIC 36.3: Budget Frontend

#### FEATURE 36.3.1: Budget UI

##### STORY 36.3.1.1: Build Budget Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 36.3.1.1.1 | Build budgets list page at /budgets: list with status, year, totals | 3 |
| 36.3.1.1.2 | Build budget create/edit page: line items grid, monthly breakdown, copy from previous option | 6 |
| 36.3.1.1.3 | Build budget vs actual report page: table with budget/actual/variance columns; highlight over-budget items; drill-down to transactions | 6 |
| 36.3.1.1.4 | Build runway dashboard widget: current cash, burn rate, runway months with visual indicator | 4 |
| 36.3.1.1.5 | Build runway detail page: burn trend chart, projection chart, scenario modeling (what if burn increases/decreases) | 5 |

---

## PHASE 37: ESOP Management (1 week)

### EPIC 37.1: ESOP Pool

#### FEATURE 37.1.1: ESOP Setup

##### STORY 37.1.1.1: Create ESOP System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 37.1.1.1.1 | Create `esop_pools` table: id, pool_name, total_shares (INT), allocated_shares (INT), available_shares (INT, computed), share_price (DECIMAL, for valuation), pool_creation_date, board_resolution_date, board_resolution_document_id, status ENUM ('active', 'exhausted', 'discontinued'), notes, created_at, updated_at | 4 |
| 37.1.1.1.2 | Create `esop_grants` table: id, pool_id, employee_id, grant_number (unique), grant_date, total_options (INT), exercise_price (DECIMAL), vesting_schedule ENUM ('four_year_one_cliff', 'four_year_monthly', 'three_year_one_cliff', 'custom'), cliff_months (INT, typically 12), vesting_period_months (INT, typically 48), vested_options (INT, computed), exercised_options (INT), cancelled_options (INT), status ENUM ('active', 'partially_vested', 'fully_vested', 'exercised', 'cancelled', 'lapsed'), grant_document_id, notes, created_at, updated_at | 5 |
| 37.1.1.1.3 | Create `esop_vesting_schedule` table: id, grant_id, vesting_date (DATE), options_vesting (INT), cumulative_vested (INT), status ENUM ('pending', 'vested', 'cancelled'); stores each vesting event | 3 |
| 37.1.1.1.4 | Implement vesting schedule generation: based on grant vesting_schedule type, generate vesting entries (e.g., 4-year with 1-year cliff: 25% at 12 months, then monthly for remaining 36 months) | 5 |
| 37.1.1.1.5 | Implement POST /api/v1/esop/grants endpoint: create grant, generate vesting schedule, update pool allocated | 4 |
| 37.1.1.1.6 | Implement GET /api/v1/esop/grants endpoint: list grants with filters (employee, status) | 3 |
| 37.1.1.1.7 | Implement GET /api/v1/esop/grants/{id} endpoint: full grant with vesting schedule | 3 |

### EPIC 37.2: Vesting & Exercise

#### FEATURE 37.2.1: Manage ESOP Lifecycle

##### STORY 37.2.1.1: ESOP Operations

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 37.2.1.1.1 | Implement vesting processing job: daily check, for grants with vesting_date = today, mark vesting entry as 'vested', update grant vested_options | 4 |
| 37.2.1.1.2 | Create `esop_exercises` table: id, grant_id, exercise_date, options_exercised (INT), exercise_price, total_amount, payment_received (BOOLEAN), shares_issued (BOOLEAN), certificate_number, notes, created_at | 3 |
| 37.2.1.1.3 | Implement POST /api/v1/esop/grants/{id}/exercise endpoint: record exercise, validate against vested options, update exercised_options | 4 |
| 37.2.1.1.4 | Implement grant cancellation: POST /api/v1/esop/grants/{id}/cancel for employee termination; cancel unvested options, return to pool | 4 |
| 37.2.1.1.5 | Implement GET /api/v1/employees/{id}/esop endpoint: employee's grants with vesting status, exercisable options | 3 |
| 37.2.1.1.6 | Implement vesting notification: email employee when options vest | 3 |

### EPIC 37.3: ESOP Frontend

#### FEATURE 37.3.1: ESOP UI

##### STORY 37.3.1.1: Build ESOP Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 37.3.1.1.1 | Build ESOP dashboard at /esop (admin): pool summary, total granted, vested, exercised; pool utilization chart | 4 |
| 37.3.1.1.2 | Build grants list page: table with employee, grant date, options, vesting progress bar, status | 4 |
| 37.3.1.1.3 | Build grant create form: employee selector, options, exercise price, vesting schedule selector | 4 |
| 37.3.1.1.4 | Build grant detail page: vesting schedule timeline, exercise history, documents | 4 |
| 37.3.1.1.5 | Build my ESOP page for employees: their grants, vesting schedule, vest calculator, exercise button (if allowed) | 5 |
| 37.3.1.1.6 | Build ESOP report: summary for board, valuation calculations | 3 |

---

## PHASE 38: Customer Support Portal (1 week)

### EPIC 38.1: Support Tickets

#### FEATURE 38.1.1: Ticket System

##### STORY 38.1.1.1: Create Support System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 38.1.1.1.1 | Create `support_products` table: id, name, code, description, is_active; your SaaS products that have support | 2 |
| 38.1.1.1.2 | Create `support_tickets` table: id, ticket_number (unique), product_id, customer_id (FK), customer_user_name (for external users), customer_user_email, subject, description (TEXT), priority ENUM ('low', 'medium', 'high', 'critical'), status ENUM ('new', 'open', 'in_progress', 'waiting_customer', 'waiting_internal', 'resolved', 'closed'), category ENUM ('bug', 'feature_request', 'question', 'billing', 'other'), assigned_to_employee_id (FK, nullable), source ENUM ('portal', 'email', 'chat'), first_response_at, resolved_at, satisfaction_rating (INT 1-5, nullable), tags (TEXT[]), created_at, updated_at | 5 |
| 38.1.1.1.3 | Create `ticket_comments` table: id, ticket_id, comment_type ENUM ('reply', 'internal_note'), content (TEXT), attachment_ids (UUID[]), is_from_customer (BOOLEAN), created_by_employee_id (FK, nullable), created_by_name (for customer comments), created_at | 3 |
| 38.1.1.1.4 | Implement ticket number generation: format TKT-{YEAR}-{SEQ} | 2 |
| 38.1.1.1.5 | Implement POST /api/v1/support/tickets endpoint (internal): create ticket on behalf of customer | 4 |
| 38.1.1.1.6 | Implement GET /api/v1/support/tickets endpoint: list with filters (status, priority, product, assigned_to, customer_id) | 4 |
| 38.1.1.1.7 | Implement GET /api/v1/support/tickets/{id} endpoint: full ticket with comments | 3 |
| 38.1.1.1.8 | Implement POST /api/v1/support/tickets/{id}/comments endpoint: add reply or internal note | 3 |
| 38.1.1.1.9 | Implement PATCH /api/v1/support/tickets/{id} endpoint: update status, priority, assignment | 3 |
| 38.1.1.1.10 | Implement ticket assignment: auto-assign based on product or round-robin; manual reassignment | 3 |

### EPIC 38.2: SLA Tracking

#### FEATURE 38.2.1: SLA Management

##### STORY 38.2.1.1: Track SLAs

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 38.2.1.1.1 | Create `sla_policies` table: id, name, product_id (nullable, for product-specific), priority, first_response_hours (INT), resolution_hours (INT), is_active | 3 |
| 38.2.1.1.2 | Seed default SLA: Critical (1hr response, 4hr resolution), High (4hr, 24hr), Medium (8hr, 48hr), Low (24hr, 72hr) | 2 |
| 38.2.1.1.3 | Implement SLA breach detection: calculate due times based on policy; check if first_response_at or resolved_at exceeds SLA; flag breached tickets | 4 |
| 38.2.1.1.4 | Implement SLA escalation: if approaching SLA breach (80% time elapsed), send alert; if breached, escalate to manager | 4 |
| 38.2.1.1.5 | Implement GET /api/v1/reports/support-sla endpoint: SLA compliance report (% met, average response time, average resolution time) | 4 |

### EPIC 38.3: Support Frontend

#### FEATURE 38.3.1: Support UI

##### STORY 38.3.1.1: Build Support Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 38.3.1.1.1 | Build support dashboard at /support: ticket counts by status, SLA status, unassigned tickets, my tickets | 5 |
| 38.3.1.1.2 | Build tickets list page: Kanban view by status or table view; filters, search, quick actions | 6 |
| 38.3.1.1.3 | Build ticket detail page: customer info, conversation thread, internal notes (separate section), status/priority/assignment controls, SLA indicator | 6 |
| 38.3.1.1.4 | Build ticket create form: customer search or manual entry, product, subject, description, priority | 4 |
| 38.3.1.1.5 | Build support reports page: ticket volume trends, SLA compliance, resolution time, customer satisfaction | 4 |
| 38.3.1.1.6 | (Optional) Build customer-facing portal: customers log in to view their tickets, submit new tickets | 6 |

---

## PHASE 39: Cap Table Management (0.5 weeks)

### EPIC 39.1: Cap Table

#### FEATURE 39.1.1: Shareholding Structure

##### STORY 39.1.1.1: Create Cap Table System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 39.1.1.1.1 | Create `share_classes` table: id, class_name (e.g., 'Equity', 'Preference'), class_code, voting_rights (BOOLEAN), dividend_preference (DECIMAL, nullable), liquidation_preference (DECIMAL, nullable), conversion_ratio (DECIMAL, nullable), authorized_shares (INT), issued_shares (INT), is_active | 3 |
| 39.1.1.1.2 | Create `shareholders` table: id, shareholder_type ENUM ('individual', 'company', 'esop_pool', 'employee'), name, email, pan, address, is_founder (BOOLEAN), is_active, created_at | 3 |
| 39.1.1.1.3 | Create `shareholdings` table: id, shareholder_id, share_class_id, num_shares (INT), share_certificate_number, acquisition_type ENUM ('founding', 'investment', 'esop_exercise', 'transfer', 'bonus'), acquisition_date, acquisition_price_per_share, total_investment, document_ids, created_at | 4 |
| 39.1.1.1.4 | Create `funding_rounds` table: id, round_name (e.g., 'Seed', 'Series A'), round_date, pre_money_valuation, amount_raised, post_money_valuation, price_per_share, share_class_id, lead_investor, notes, term_sheet_document_id, sha_document_id, status ENUM ('in_progress', 'closed', 'cancelled'), created_at | 4 |
| 39.1.1.1.5 | Implement GET /api/v1/cap-table endpoint: return current cap table with all shareholders, shares, percentage ownership; filter by share class | 4 |
| 39.1.1.1.6 | Implement POST /api/v1/cap-table/transactions endpoint: record share issuance, transfer, or buyback; update shareholdings | 4 |
| 39.1.1.1.7 | Implement GET /api/v1/cap-table/history endpoint: cap table at any historical date; useful for due diligence | 4 |
| 39.1.1.1.8 | Implement cap table calculations: fully diluted ownership (include ESOP pool), ownership percentages, dilution modeling | 4 |

### EPIC 39.2: Cap Table Frontend

#### FEATURE 39.2.1: Cap Table UI

##### STORY 39.2.1.1: Build Cap Table Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 39.2.2.1.1 | Build cap table page at /cap-table: pie chart of ownership, table with shareholder, shares, percentage; toggle fully-diluted view | 5 |
| 39.2.2.1.2 | Build shareholders list page: manage shareholders (add founder, investor, etc.) | 3 |
| 39.2.2.1.3 | Build funding rounds page: list rounds with details, add new round | 4 |
| 39.2.2.1.4 | Build dilution modeler: "What if" scenario - if we raise $X at $Y valuation, what's the dilution? | 5 |
| 39.2.2.1.5 | Build cap table export: PDF and Excel export for investors/due diligence | 3 |

---

## Summary Statistics - Phase 2

| Phase | Module | Tasks | Hours |
|-------|--------|-------|-------|
| 31 | AI Autonomous Accountant | 42 | 168 |
| 32 | CA Verification Portal | 28 | 112 |
| 33 | Compliance Tracker | 23 | 92 |
| 34 | Quotes & Proposals | 35 | 140 |
| 35 | Asset Management | 33 | 132 |
| 36 | Budget & Financial Planning | 26 | 104 |
| 37 | ESOP Management | 26 | 104 |
| 38 | Customer Support Portal | 30 | 120 |
| 39 | Cap Table Management | 17 | 68 |
| **Phase 2 Total** | | **260** | **1,040** |

---

## Combined Project Summary

| Phase | Description | Tasks | Hours |
|-------|-------------|-------|-------|
| Phase 1 | HRMS + Accounting + Projects + AI | 639 | 2,548 |
| Phase 2 | Startup Operations + AI Accountant | 260 | 1,040 |
| **Grand Total** | | **899** | **3,588** |

### Timeline Estimates

| Scenario | Phase 1 | Phase 2 | Total |
|----------|---------|---------|-------|
| 1 Developer (40 hrs/week) | 64 weeks | 26 weeks | ~22 months |
| 2 Developers | 32 weeks | 13 weeks | ~11 months |
| 1 Dev + AI Assistance | 45 weeks | 18 weeks | ~16 months |

---

## Implementation Priority

### Recommended Order for Phase 2

| Priority | Module | Why |
|----------|--------|-----|
| 1 | AI Autonomous Accountant | Core productivity gain |
| 2 | CA Verification Portal | Enables CA collaboration |
| 3 | Compliance Tracker | Avoid penalties |
| 4 | Quotes & Proposals | Revenue generation |
| 5 | Asset Management | Operational need |
| 6 | Budget & Financial Planning | Financial control |
| 7 | Customer Support Portal | When SaaS launches |
| 8 | ESOP Management | When hiring with ESOPs |
| 9 | Cap Table Management | When raising funding |

---

## Appendix A: New API Endpoints Summary

### AI Accountant
- GET /api/v1/ai/queue-status
- POST /api/v1/ai/process-queue
- GET /api/v1/ai/learning-stats
- GET /api/v1/ai/scheduled-jobs
- POST /api/v1/ai/scheduled-jobs/{id}/run

### CA Portal
- GET /api/v1/ca/verification-queue
- POST /api/v1/ca/entries/{id}/approve
- POST /api/v1/ca/entries/{id}/reject
- POST /api/v1/ca/entries/{id}/correct
- POST /api/v1/ca/entries/bulk-approve
- GET /api/v1/ca/auto-posted
- GET /api/v1/ca/flagged

### Compliance
- GET /api/v1/compliance
- PUT /api/v1/compliance/{id}
- GET /api/v1/compliance/categories
- POST /api/v1/compliance/items

### Quotes
- GET /api/v1/quotes
- POST /api/v1/quotes
- GET /api/v1/quotes/{id}
- PUT /api/v1/quotes/{id}
- POST /api/v1/quotes/{id}/send
- POST /api/v1/quotes/{id}/accept
- POST /api/v1/quotes/{id}/reject
- POST /api/v1/quotes/{id}/convert-to-project
- POST /api/v1/quotes/{id}/convert-to-invoice
- POST /api/v1/quotes/{id}/duplicate
- POST /api/v1/quotes/{id}/generate-pdf

### Assets
- GET /api/v1/assets
- POST /api/v1/assets
- GET /api/v1/assets/{id}
- PUT /api/v1/assets/{id}
- POST /api/v1/assets/{id}/assign
- POST /api/v1/assets/{id}/return
- POST /api/v1/assets/{id}/dispose
- GET /api/v1/employees/{id}/assets
- GET /api/v1/software-licenses
- POST /api/v1/software-licenses
- GET /api/v1/reports/depreciation
- GET /api/v1/reports/license-costs

### Budget
- GET /api/v1/budgets
- POST /api/v1/budgets
- GET /api/v1/budgets/{id}
- PUT /api/v1/budgets/{id}
- POST /api/v1/budgets/{id}/approve
- GET /api/v1/reports/budget-vs-actual
- GET /api/v1/reports/runway

### ESOP
- GET /api/v1/esop/pools
- POST /api/v1/esop/pools
- GET /api/v1/esop/grants
- POST /api/v1/esop/grants
- GET /api/v1/esop/grants/{id}
- POST /api/v1/esop/grants/{id}/exercise
- POST /api/v1/esop/grants/{id}/cancel
- GET /api/v1/employees/{id}/esop

### Support
- GET /api/v1/support/tickets
- POST /api/v1/support/tickets
- GET /api/v1/support/tickets/{id}
- PATCH /api/v1/support/tickets/{id}
- POST /api/v1/support/tickets/{id}/comments
- GET /api/v1/reports/support-sla

### Cap Table
- GET /api/v1/cap-table
- POST /api/v1/cap-table/transactions
- GET /api/v1/cap-table/history
- GET /api/v1/shareholders
- POST /api/v1/shareholders
- GET /api/v1/funding-rounds
- POST /api/v1/funding-rounds

---

## Appendix B: New Database Tables Summary

### AI Accountant (7 tables)
- ai_confidence_rules
- transaction_patterns
- ai_processing_queue
- ai_corrections
- scheduled_jobs

### CA Portal (2 tables)
- ca_firms
- (Enhanced: journal_entries, users)

### Compliance (3 tables)
- compliance_categories
- compliance_items
- compliance_tracker

### Quotes (3 tables)
- quotes
- quote_line_items
- quote_versions

### Assets (6 tables)
- asset_categories
- assets
- asset_assignments
- software_licenses
- license_assignments
- asset_depreciation

### Budget (2 tables)
- budgets
- budget_line_items

### ESOP (4 tables)
- esop_pools
- esop_grants
- esop_vesting_schedule
- esop_exercises

### Support (4 tables)
- support_products
- support_tickets
- ticket_comments
- sla_policies

### Cap Table (4 tables)
- share_classes
- shareholders
- shareholdings
- funding_rounds

**Total New Tables: 35**

---

## Appendix C: Integration Points

### AI Accountant Integrations
- Bank Reconciliation → AI Processing Queue
- Bill Upload → AI Document Processor
- Journal Entries → Confidence Scoring
- CA Portal → Verification Queue

### Compliance Integrations
- GST Returns (Phase 1) → Compliance Tracker
- TDS Returns (Phase 1) → Compliance Tracker
- PF/ESI Returns (Phase 1) → Compliance Tracker
- CA Portal → Compliance Status Updates

### Quotes Integrations
- CRM Leads → Quote Creation
- Quotes → Project Creation
- Quotes → Invoice Creation
- Customers → Quote Recipients

### Asset Integrations
- Employees → Asset Assignment
- Vendors → Asset Purchase
- GL Accounts → Depreciation Posting
- EDMS → Asset Documents

### ESOP Integrations
- Employees → Grant Recipients
- Cap Table → ESOP Pool
- Payroll → Exercise Tax Implications (future)

### Support Integrations
- Customers → Ticket Creators
- Products → Support Categories
- Employees → Ticket Assignees

---

*End of Phase 2 WBS Document*
