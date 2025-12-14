# GanaPortal Fix Implementation - Work Breakdown Structure

## Project Overview
**Objective**: Production-harden GanaPortal based on RCA findings
**Total Phases**: 3
**Total Tasks**: 42
**Approach**: Fix → Test → Verify No Regression → Commit

---

## PHASE 1: Foundation Fixes (No Breaking Changes)

### EPIC 1.1: Configuration Security

#### FEATURE 1.1.1: Environment Validation

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 1.1.1.1 | Add Pydantic model validator to detect default secrets in production | 1 | None |
| 1.1.1.2 | Add startup warning log when using development defaults | 0.5 | 1.1.1.1 |
| 1.1.1.3 | Change `extra="ignore"` to `extra="forbid"` with explicit allowed extras | 0.5 | None |
| 1.1.1.4 | Test: Verify app starts with valid .env | 0.5 | 1.1.1.1-3 |
| 1.1.1.5 | Test: Verify app warns with default secrets | 0.5 | 1.1.1.4 |

### EPIC 1.2: Path Traversal Fix

#### FEATURE 1.2.1: File Access Validation

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 1.2.1.1 | Create `validate_file_path()` utility in file_storage.py | 1 | None |
| 1.2.1.2 | Apply path validation to document download endpoint | 0.5 | 1.2.1.1 |
| 1.2.1.3 | Apply path validation to employee document download | 0.5 | 1.2.1.1 |
| 1.2.1.4 | Test: Verify valid paths work | 0.5 | 1.2.1.2-3 |
| 1.2.1.5 | Test: Verify path traversal attempts are blocked | 0.5 | 1.2.1.4 |

### EPIC 1.3: Logging Infrastructure

#### FEATURE 1.3.1: Structured Logging Setup

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 1.3.1.1 | Create logging configuration module with JSON formatter | 1 | None |
| 1.3.1.2 | Add request ID middleware for request tracing | 1 | 1.3.1.1 |
| 1.3.1.3 | Replace print statements with proper logging calls | 1 | 1.3.1.1 |
| 1.3.1.4 | Test: Verify logs are written with correct format | 0.5 | 1.3.1.1-3 |

### EPIC 1.4: Email Service

#### FEATURE 1.4.1: Email Infrastructure

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 1.4.1.1 | Create email service module with async send capability | 2 | None |
| 1.4.1.2 | Create email templates for password reset | 1 | 1.4.1.1 |
| 1.4.1.3 | Integrate email service into password reset endpoint | 1 | 1.4.1.2 |
| 1.4.1.4 | Remove print statement that exposes reset token | 0.5 | 1.4.1.3 |
| 1.4.1.5 | Test: Verify password reset flow works | 0.5 | 1.4.1.4 |

---

## PHASE 2: Backend Security

### EPIC 2.1: Data Encryption

#### FEATURE 2.1.1: Encryption TypeDecorator

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 2.1.1.1 | Create EncryptedString SQLAlchemy TypeDecorator | 2 | Phase 1 |
| 2.1.1.2 | Apply EncryptedString to EmployeeIdentity model (PAN, Aadhaar) | 1 | 2.1.1.1 |
| 2.1.1.3 | Apply EncryptedString to EmployeeBank model (account_number) | 0.5 | 2.1.1.1 |
| 2.1.1.4 | Apply EncryptedString to Vendor model (PAN, bank_details) | 0.5 | 2.1.1.1 |
| 2.1.1.5 | Apply EncryptedString to Customer model (PAN) | 0.5 | 2.1.1.1 |
| 2.1.1.6 | Create Alembic migration for encrypted fields | 1 | 2.1.1.2-5 |
| 2.1.1.7 | Create data migration script for existing unencrypted data | 2 | 2.1.1.6 |
| 2.1.1.8 | Test: Verify encryption/decryption works transparently | 1 | 2.1.1.7 |

### EPIC 2.2: Transaction Management

#### FEATURE 2.2.1: Standardize Commits

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 2.2.1.1 | Audit all endpoints for manual commit calls | 1 | Phase 1 |
| 2.2.1.2 | Remove redundant manual commits from endpoints | 2 | 2.2.1.1 |
| 2.2.1.3 | Test: Verify data persistence works correctly | 1 | 2.2.1.2 |

### EPIC 2.3: Authorization

#### FEATURE 2.3.1: Role-Based Access Control

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 2.3.1.1 | Add require_accountant to accounting endpoints | 1 | Phase 1 |
| 2.3.1.2 | Add require_accountant to vendor/customer endpoints | 1 | 2.3.1.1 |
| 2.3.1.3 | Add require_hr to employee management endpoints | 1 | 2.3.1.1 |
| 2.3.1.4 | Test: Verify role restrictions work correctly | 1 | 2.3.1.1-3 |

### EPIC 2.4: CORS Hardening

#### FEATURE 2.4.1: Restrict CORS

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 2.4.1.1 | Replace wildcard methods with explicit list | 0.5 | Phase 1 |
| 2.4.1.2 | Replace wildcard headers with explicit list | 0.5 | 2.4.1.1 |
| 2.4.1.3 | Test: Verify frontend still works with restricted CORS | 0.5 | 2.4.1.2 |

---

## PHASE 3: Frontend Fixes

### EPIC 3.1: Auth Flow Consolidation

#### FEATURE 3.1.1: Single Auth Handler

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 3.1.1.1 | Remove window.location.href redirect from client.ts | 0.5 | Phase 2 |
| 3.1.1.2 | Add 401 error handling in AuthContext | 1 | 3.1.1.1 |
| 3.1.1.3 | Update ProtectedRoute to handle loading state properly | 0.5 | 3.1.1.2 |
| 3.1.1.4 | Test: Verify login/logout flow works | 0.5 | 3.1.1.3 |
| 3.1.1.5 | Test: Verify 401 redirects to login correctly | 0.5 | 3.1.1.4 |

### EPIC 3.2: Error Handling

#### FEATURE 3.2.1: Error Boundaries

| Task ID | Task Description | Est. Hours | Dependencies |
|---------|------------------|------------|--------------|
| 3.2.1.1 | Create root error.tsx for app-wide errors | 1 | Phase 2 |
| 3.2.1.2 | Create dashboard error.tsx for dashboard errors | 0.5 | 3.2.1.1 |
| 3.2.1.3 | Add loading.tsx for Suspense boundaries | 0.5 | 3.2.1.1 |
| 3.2.1.4 | Test: Verify error boundaries catch errors gracefully | 0.5 | 3.2.1.1-3 |

---

## Test Strategy

### After Each Task
1. Run relevant unit tests
2. Manual smoke test of affected feature
3. Check for console errors/warnings

### After Each Feature
1. Run full test suite
2. Test integration with dependent features
3. Check application starts without errors

### After Each Phase
1. Full regression test
2. Security scan (for Phase 2)
3. Performance check

---

## Success Criteria

| Phase | Criteria |
|-------|----------|
| Phase 1 | App starts, logs work, no print statements, path traversal blocked |
| Phase 2 | PII encrypted, roles enforced, CORS restricted, no data loss |
| Phase 3 | Auth flow smooth, errors handled gracefully, no blank screens |

---

## Rollback Plan

Each phase can be rolled back independently:
- Phase 1: Revert config/logging (safe, no data changes)
- Phase 2: Decrypt data, revert models (has migration script)
- Phase 3: Revert frontend changes (no backend impact)

---

*Document Version: 1.0*
*Created: Based on RCA Report findings*
