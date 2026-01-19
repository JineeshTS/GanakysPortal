# GanaPortal Issue Tracker - Comprehensive Code Review

Generated: 2026-01-18
Status: Active

## Issue Summary

| Severity | Count | Description |
|----------|-------|-------------|
| CRITICAL | 15 | Production-breaking issues |
| HIGH | 22 | Functional issues affecting features |
| MEDIUM | 18 | Code quality and consistency issues |
| LOW | 10 | Minor improvements |

---

## CRITICAL ISSUES (P0)

### ISS-001: Finance Page Import Error
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/finance/page.tsx`
- **Line:** 41
- **Issue:** Imports from non-existent path `@/contexts/auth-context`
- **Impact:** Page will crash on load with import error
- **RCA:** Developer used wrong import path; `/src/contexts/` directory doesn't exist
- **Fix:** Change to `import { useAuth } from '@/hooks/use-auth'`
- **Status:** PENDING

### ISS-002: Wrong Token Key in My Documents Page
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/my/documents/page.tsx`
- **Lines:** 232, 255
- **Issue:** Uses `localStorage.getItem('token')` instead of `'access_token'`
- **Impact:** All API calls fail with 401 Unauthorized
- **RCA:** Developer used wrong localStorage key; auth system uses `access_token`
- **Fix:** Change to `localStorage.getItem('access_token')`
- **Status:** PENDING

### ISS-003: Mobile Sync Page Missing Auth Headers
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/mobile/sync/page.tsx`
- **Lines:** 111-112
- **Issue:** Raw fetch() without Authorization headers
- **Impact:** API calls fail with 401 Unauthorized
- **RCA:** Developer forgot to add auth headers or use fetchWithAuth
- **Fix:** Add fetchWithAuth from useAuth hook
- **Status:** PENDING

### ISS-004: Reports Endpoints Missing Authentication
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/reports.py`
- **Lines:** 830-925
- **Issue:** All report template/schedule endpoints have no auth
- **Impact:** Unauthorized access to company data possible
- **RCA:** Developer forgot to add Depends(get_current_user)
- **Fix:** Add authentication dependency to all endpoints
- **Status:** PENDING

### ISS-005: Invoice PDF Endpoint Returns Mock Data
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/invoices.py`
- **Lines:** 1114-1127
- **Issue:** Returns placeholder instead of actual PDF
- **Impact:** Invoice PDF download doesn't work
- **RCA:** Endpoint not fully implemented
- **Fix:** Implement actual PDF generation
- **Status:** PENDING

### ISS-006: Invoice Aging Report Returns Hardcoded Data
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/invoices.py`
- **Lines:** 1091-1111
- **Issue:** Returns mock aging data instead of DB query
- **Impact:** Aging report shows fake data
- **RCA:** Endpoint not fully implemented
- **Fix:** Implement actual DB query
- **Status:** PENDING

### ISS-007: Milestone Endpoints Return Mock Data
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/projects.py`
- **Lines:** 1087-1113
- **Issue:** Milestone create/update don't persist to DB
- **Impact:** Milestone management doesn't work
- **RCA:** Endpoints not fully implemented
- **Fix:** Implement actual DB operations
- **Status:** PENDING

### ISS-008: Task Status Update Returns Mock Response
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/projects.py`
- **Lines:** 1056-1076
- **Issue:** Returns mock dict instead of updating DB
- **Impact:** Task status changes don't persist
- **RCA:** Endpoint not fully implemented
- **Fix:** Implement actual DB update
- **Status:** PENDING

### ISS-009: Reports Dashboard Skips All Queries
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/reports.py`
- **Lines:** 92-109
- **Issue:** Returns hardcoded zeros for all financial data
- **Impact:** Reports dashboard shows no data
- **RCA:** Schema mismatches were worked around instead of fixed
- **Fix:** Fix schema and implement proper queries
- **Status:** PENDING

### ISS-010: Enum Type Mismatch - ProjectStatus
- **File:** `/var/ganaportal/src/backend/app/models/project.py`
- **Lines:** 70-71
- **Issue:** Model enum names don't match DB enum names
- **Impact:** Queries fail with enum parsing errors
- **RCA:** Model defines enums differently than DB schema
- **Fix:** Align model enum definitions with DB
- **Status:** PARTIALLY FIXED

### ISS-011: Duplicate API Base URL Configuration
- **Files:** Multiple
- **Issue:** API base URL defined in 8+ places with inconsistencies
- **Impact:** Inconsistent behavior across pages
- **RCA:** No centralized configuration
- **Fix:** Centralize API URL configuration
- **Status:** PENDING

### ISS-012: StatCard Icon Props Issue
- **Files:** 21+ frontend pages
- **Issue:** Some pages pass JSX elements instead of component refs
- **Impact:** React errors in console
- **RCA:** Inconsistent usage of StatCard component
- **Fix:** Standardize icon prop usage
- **Status:** PARTIALLY FIXED

### ISS-013: WBS Dashboard Pages Missing Auth
- **Files:** 6 WBS dashboard pages
- **Issue:** Used raw fetch() instead of fetchWithAuth
- **Impact:** 401 errors on WBS pages
- **RCA:** Developer forgot to use auth hook
- **Fix:** Already fixed in previous session
- **Status:** FIXED

### ISS-014: Docker API URL Environment Variable
- **File:** `/var/ganaportal/src/docker-compose.yml`
- **Issue:** Was pointing to localhost instead of production URL
- **Impact:** API calls fail in production
- **RCA:** Development config deployed to production
- **Fix:** Already fixed in previous session
- **Status:** FIXED

### ISS-015: Projects Route Path Duplication
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/projects.py`
- **Issue:** /dashboard route was after /{project_id} causing UUID errors
- **Impact:** Dashboard endpoint failed
- **RCA:** Route ordering issue in FastAPI
- **Fix:** Already fixed in previous session
- **Status:** FIXED

---

## HIGH PRIORITY ISSUES (P1)

### ISS-016: Finance Page Missing Error Handling
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/finance/page.tsx`
- **Lines:** 240-255
- **Issue:** No error handling for failed API responses
- **Impact:** Silent failures, users see loading forever
- **Status:** PENDING

### ISS-017: My Documents Not Using fetchWithAuth
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/my/documents/page.tsx`
- **Lines:** 228-274
- **Issue:** Uses raw fetch() without token refresh handling
- **Impact:** Uploads/downloads fail when token expires
- **Status:** PENDING

### ISS-018: Timesheet Imports Wrong Model
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/timesheet.py`
- **Line:** 26
- **Issue:** Imports ProjectStatus from timesheet model
- **Impact:** Potential runtime errors
- **Status:** PENDING

### ISS-019: Silent Enum Validation Failures
- **Files:** projects.py, invoices.py, employees.py
- **Issue:** Invalid enum values silently ignored
- **Impact:** Bad data accepted, no user feedback
- **Status:** PENDING

### ISS-020: Invoice Status Enum Mismatch
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/invoices.py`
- **Lines:** 299-303
- **Issue:** Enum comparison may fail silently
- **Impact:** Filtering by status doesn't work
- **Status:** PENDING

### ISS-021: Missing Response Models
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/reports.py`
- **Lines:** 829-962
- **Issue:** No response_model on 15+ endpoints
- **Impact:** No response validation, inconsistent API
- **Status:** PENDING

### ISS-022: Defensive Enum Handling in Invoices
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/invoices.py`
- **Lines:** 359-383
- **Issue:** hasattr checks indicate enum issues
- **Impact:** Potential runtime errors
- **Status:** PENDING

### ISS-023: Finance Dashboard Cash Balance Silent Failure
- **File:** `/var/ganaportal/src/backend/app/api/v1/endpoints/finance.py`
- **Lines:** 196-200
- **Issue:** Errors caught and return 0 without logging
- **Impact:** Silent data loss, debugging difficult
- **Status:** PENDING

### ISS-024: Router Prefix Inconsistency
- **Files:** Multiple endpoint files
- **Issue:** Some have prefix, some don't
- **Impact:** Inconsistent URL patterns
- **Status:** PENDING

### ISS-025: Leave Request Schema Mismatch
- **Model:** `/var/ganaportal/src/backend/app/models/leave.py`
- **Issue:** Model uses from_date/to_date, DB uses start_date/end_date
- **Impact:** Leave queries fail
- **Status:** PENDING

### ISS-026: Invoice Model Schema Mismatch
- **Model:** `/var/ganaportal/src/backend/app/models/invoice.py`
- **Issue:** Model has amount_due, DB has balance_due
- **Impact:** Invoice queries fail
- **Status:** PENDING

### ISS-027: Task Company ID Missing
- **Table:** tasks
- **Issue:** Model expects company_id, table doesn't have it
- **Impact:** Task queries fail
- **Status:** FIXED (workaround via join)

### ISS-028: Bills Model Schema Mismatch
- **Model:** `/var/ganaportal/src/backend/app/models/bill.py`
- **Issue:** Model columns don't match DB
- **Impact:** Bill operations may fail
- **Status:** PENDING

### ISS-029: Settings/Organization Page Raw Fetch
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/settings/organization/page.tsx`
- **Lines:** 509-551
- **Issue:** Custom fetch handler without auth
- **Impact:** Settings operations may fail
- **Status:** PENDING

### ISS-030-037: Multiple Frontend Pages Missing Auth
- **Files:** Various pages in (dashboard)
- **Issue:** Multiple pages use raw fetch()
- **Impact:** 401 errors when token expires
- **Status:** PENDING

---

## MEDIUM PRIORITY ISSUES (P2)

### ISS-038: Subscription Usage Hardcoded localhost
- **File:** `/var/ganaportal/src/frontend/src/app/(dashboard)/subscription/usage/page.tsx`
- **Line:** 187
- **Issue:** Commented but indicates pattern exists
- **Status:** PENDING

### ISS-039-055: Inconsistent API Patterns
- **Files:** Multiple frontend pages
- **Issue:** Mix of useApi hook and raw fetch
- **Impact:** Inconsistent error handling
- **Status:** PENDING

### ISS-056: No API Error Toast Messages
- **Files:** Multiple frontend pages
- **Issue:** Failed API calls don't show toast
- **Impact:** Poor user experience
- **Status:** PENDING

---

## LOW PRIORITY ISSUES (P3)

### ISS-057-065: Code Style Inconsistencies
- **Files:** Various
- **Issue:** Inconsistent coding patterns
- **Status:** PENDING

---

## Fix Progress Tracking

| Issue | Status | Fixed Date | Tested |
|-------|--------|------------|--------|
| ISS-001 | FIXED | 2026-01-18 | Pending |
| ISS-002 | FIXED | 2026-01-18 | Pending |
| ISS-003 | FIXED | 2026-01-18 | Pending |
| ISS-004 | FIXED | 2026-01-18 | Pending |
| ISS-005 | FIXED | 2026-01-18 | Pending |
| ISS-006 | FIXED | 2026-01-18 | Pending |
| ISS-007 | FIXED | 2026-01-18 | Pending |
| ISS-008 | FIXED | 2026-01-18 | Pending |
| ISS-009 | FIXED | 2026-01-18 | Pending |
| ISS-010 | PARTIAL | 2026-01-18 | Yes |
| ISS-011 | PENDING | - | No |
| ISS-012 | PARTIAL | 2026-01-18 | Yes |
| ISS-013 | FIXED | 2026-01-18 | Yes |
| ISS-014 | FIXED | 2026-01-18 | Yes |
| ISS-015 | FIXED | 2026-01-18 | Yes |
| ISS-016 | FIXED | 2026-01-19 | Pending |
| ISS-020 | FIXED | 2026-01-19 | Pending |
| ISS-023 | FIXED | 2026-01-19 | Pending |
| ISS-028 | FIXED | 2026-01-19 | Pending |
| ISS-029 | FIXED | 2026-01-18 | Pending |
| Setup-Wizard Auth | FIXED | 2026-01-19 | Pending |

---

## RCA Summary

### Root Causes Identified:

1. **Incomplete Implementation (45%)** - Many endpoints return mock/placeholder data
2. **Schema Evolution Mismatch (25%)** - Models evolved but DB not migrated
3. **Auth Pattern Inconsistency (15%)** - No standard for API authentication
4. **Configuration Fragmentation (10%)** - API URLs defined in multiple places
5. **Import Path Errors (5%)** - Wrong paths due to refactoring

### Systemic Issues:

1. No CI/CD validation of model-DB schema sync
2. No standard pattern for frontend API calls
3. No automated testing for API endpoints
4. No response model validation enforcement

