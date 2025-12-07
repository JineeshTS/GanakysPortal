# GanaPortal - Complete Work Breakdown Structure (WBS)
## Unified ERP System for Ganakys Codilla Apps (OPC) Private Limited

**Project:** GanaPortal - AI-Powered ERP for IT Services Company  
**Version:** 2.0 (Consolidated)  
**Date:** December 2025  
**Client:** Ganakys Codilla Apps (OPC) Private Limited  
**Deployment:** portal.ganakys.com (Hostinger VPS)  
**Target Scale:** 5 employees (2026) → 15 employees (2027)  

---

## Executive Summary

GanaPortal is a comprehensive, AI-powered ERP system designed specifically for a small IT services and SaaS company operating in India with international clients. The system combines HRMS, document management, accounting, CRM, and project management into a unified platform.

### Core Modules

| Module | Description |
|--------|-------------|
| **HRMS** | Employee management, onboarding, leave, timesheet |
| **EDMS** | Enterprise document management with folder hierarchy |
| **Payroll** | Full India compliance - PF, ESI, TDS, PT, Form 16 |
| **Statutory** | PF ECR, ESI Return, TDS 24Q file generation |
| **Accounting** | GL, AR, AP, multi-currency, bank reconciliation |
| **GST Compliance** | GSTR-1, GSTR-3B, HSN/SAC management |
| **CRM** | Lead management, pipeline, AI-powered follow-ups |
| **Project Management** | Client & internal projects, billing, resource planning |
| **AI Layer** | Document processing, natural language queries, insights |

### Key Features

- Role-based access: Admin (Employer), HR, Accountant, Employee
- Multi-currency invoicing (INR, USD, EUR, GBP, etc.)
- Export of services compliance (LUT, FIRC tracking)
- AI-powered document extraction (bills, bank statements)
- Natural language ERP assistant
- Time & Material and Fixed Price project billing
- Resource allocation and utilization tracking
- Project profitability analysis

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS, shadcn/ui |
| Backend | FastAPI (Python 3.11+), SQLAlchemy 2.0, Pydantic v2 |
| Database | PostgreSQL 16, Redis 7 |
| AI | Claude API (claude-3.5-sonnet) |
| File Storage | Local filesystem with structured paths |
| Deployment | Docker, Nginx, Let's Encrypt SSL |
| Infrastructure | Hostinger VPS (Ubuntu 22.04) |

### Project Statistics

| Metric | Value |
|--------|-------|
| Total Phases | 30 |
| Total Tasks | 639 |
| Total Hours | 2,548 |
| Estimated Timeline | 12-14 months |

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      portal.ganakys.com                              │
│                      (Nginx + SSL)                                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────────┐              ┌─────────────────────┐       │
│  │     Next.js App     │    REST API  │     FastAPI         │       │
│  │     (Frontend)      │◄────────────►│     (Backend)       │       │
│  │     Port: 3000      │              │     Port: 8000      │       │
│  └─────────────────────┘              └──────────┬──────────┘       │
│                                                   │                  │
│         ┌────────────────────────────────────────┼─────────────┐    │
│         ▼                 ▼                      ▼             ▼    │
│  ┌───────────┐    ┌───────────┐          ┌───────────┐ ┌─────────┐ │
│  │PostgreSQL │    │   Redis   │          │  Claude   │ │  File   │ │
│  │  (Data)   │    │ (Cache)   │          │   API     │ │ Storage │ │
│  └───────────┘    └───────────┘          └───────────┘ └─────────┘ │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

### Module Integration Map

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GANAPORTAL MODULES                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐       │
│  │  HRMS   │────►│ Payroll │────►│   GL    │◄────│   AP    │       │
│  └────┬────┘     └─────────┘     └────┬────┘     └────┬────┘       │
│       │                               │               │             │
│       ▼                               ▼               ▼             │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐       │
│  │Timesheet│────►│ Project │────►│   AR    │────►│ Invoice │       │
│  └─────────┘     └────┬────┘     └─────────┘     └─────────┘       │
│                       │                                             │
│       ┌───────────────┼───────────────┐                            │
│       ▼               ▼               ▼                            │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐                       │
│  │Resource │     │ Billing │     │  EDMS   │                       │
│  │  Mgmt   │     │         │     │         │                       │
│  └─────────┘     └─────────┘     └─────────┘                       │
│                                                                      │
│  ┌──────────────────────────────────────────────────────────┐      │
│  │                    AI LAYER                               │      │
│  │  Document Processing │ Query Engine │ Insights │ Actions  │      │
│  └──────────────────────────────────────────────────────────┘      │
│                                                                      │
│  ┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐       │
│  │   CRM   │     │   GST   │     │   TDS   │     │  Bank   │       │
│  │         │     │Compliance│    │Compliance│    │  Recon  │       │
│  └─────────┘     └─────────┘     └─────────┘     └─────────┘       │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

---

## User Roles & Permissions

| Feature | Admin (Employer) | HR | Accountant | Employee |
|---------|------------------|-----|------------|----------|
| Company Setup | Full | View | View | - |
| User Management | Full | Create Employee | - | - |
| Employee Records | Full | Full | - | Self Only |
| EDMS (Folders/Docs) | Full | Full | Full | Limited |
| Leave Management | Full | Full (Approve) | - | Self + Team View |
| Timesheet | Full | Full (Approve) | View | Self |
| Payroll Processing | Full | Full | View | - |
| Payslips | Full | Full | View | Self Only |
| Statutory Filings | Full | Full | View + Download | - |
| Accounting (AR/AP) | Full | - | Full | - |
| Bank Reconciliation | Full | - | Full | - |
| GST Compliance | Full | - | View + Download | - |
| CRM | Full | - | - | - |
| Project Management | Full | View | View | Assigned Projects |
| Resource Allocation | Full | View | - | Self View |
| Reports | Full | Full | Financial Only | Self Only |

---

# PART A: HRMS & DOCUMENT MANAGEMENT

---

## PHASE 1: Discovery & Planning (1 week)

### EPIC 1.1: Requirements & Architecture

#### FEATURE 1.1.1: Requirements Documentation

##### STORY 1.1.1.1: Document Functional Requirements

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 1.1.1.1.1 | Create detailed functional requirements document covering all core modules: HRMS, EDMS, Payroll, Accounting, CRM, Project Management; include user stories for each role (Admin, HR, Accountant, Employee); document acceptance criteria for each feature | 8 |
| 1.1.1.1.2 | Create database schema design document with all tables, relationships, indexes, and constraints; include ER diagram using dbdiagram.io; document field-level encryption requirements for sensitive data (Aadhaar, PAN, bank account); specify audit trail requirements | 6 |
| 1.1.1.1.3 | Document India payroll compliance requirements: PF calculation rules (12% employee, 12% employer split into EPS 8.33% and EPF 3.67%), ESI rules (0.75% + 3.25% if gross ≤ ₹21,000), TDS slabs (old vs new regime), Professional Tax (Karnataka), Gratuity, Bonus; document all formulas with examples | 6 |
| 1.1.1.1.4 | Create wireframes for all major screens using Figma: Login, Dashboard (role-specific), EDMS folder browser, Employee onboarding wizard, Leave management, Timesheet grid, Payroll processing, Invoice creation, Project management, CRM pipeline; get stakeholder approval | 8 |

##### STORY 1.1.1.2: Define Technical Architecture

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 1.1.1.2.1 | Create technical architecture document: Next.js 14 App Router structure, FastAPI project structure with routers/services pattern, PostgreSQL schema with Alembic migrations, file storage architecture, Redis for sessions/caching, Claude API integration architecture | 6 |
| 1.1.1.2.2 | Document API design standards: REST conventions, endpoint naming (/api/v1/resource), JWT authentication, request/response format (JSON with snake_case), pagination (cursor-based), error response format, rate limiting | 4 |
| 1.1.1.2.3 | Create deployment architecture for Hostinger VPS: Docker Compose setup, Nginx reverse proxy with SSL, backup strategy (daily pg_dump + file rsync), monitoring setup, CI/CD with GitHub Actions | 4 |
| 1.1.1.2.4 | Document security requirements: password policy, JWT token management, field encryption (AES-256), audit logging, file upload validation, CORS configuration, rate limiting | 4 |

---

## PHASE 2: Infrastructure Setup (1 week)

### EPIC 2.1: Development Environment

#### FEATURE 2.1.1: Local Development Setup

##### STORY 2.1.1.1: Setup Development Environment

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 2.1.1.1.1 | Create project monorepo structure: /frontend (Next.js), /backend (FastAPI), /database (migrations, seeds), /docker (compose files), /docs, /scripts; initialize git with .gitignore | 4 |
| 2.1.1.1.2 | Create Docker Compose development configuration: postgres:16, redis:7, backend (FastAPI with hot reload), frontend (Next.js with hot reload); configure environment variables via .env | 4 |
| 2.1.1.1.3 | Initialize Next.js 14 project with App Router, TypeScript, Tailwind CSS, ESLint, Prettier; install dependencies: axios, react-hook-form, zod, @tanstack/react-query, date-fns, lucide-react, shadcn/ui | 4 |
| 2.1.1.1.4 | Initialize FastAPI project with Python 3.11+; create structure: /app/api (routers), /app/models (SQLAlchemy), /app/schemas (Pydantic), /app/services, /app/core (config, security), /app/utils; install dependencies | 4 |
| 2.1.1.1.5 | Configure Alembic for database migrations; create initial migration with schema version tracking; document migration workflow | 3 |

#### FEATURE 2.1.2: Production Environment Setup

##### STORY 2.1.2.1: Setup Hostinger VPS

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 2.1.2.1.1 | Configure Hostinger VPS: Ubuntu 22.04 LTS, Docker/Docker Compose, non-root user with sudo, SSH key auth, UFW firewall (22, 80, 443), fail2ban | 4 |
| 2.1.2.1.2 | Configure DNS: A record for portal.ganakys.com, CAA record for Let's Encrypt, verify propagation | 2 |
| 2.1.2.1.3 | Setup Nginx reverse proxy: server block for portal.ganakys.com, upstream for Next.js and FastAPI, location blocks for routing | 4 |
| 2.1.2.1.4 | Setup SSL with Let's Encrypt: certbot, HTTPS configuration, auto-renewal cron, security headers (HSTS, X-Frame-Options) | 3 |
| 2.1.2.1.5 | Create production Docker Compose: multi-stage Dockerfiles, production environment variables, restart policies, resource limits, health checks | 4 |
| 2.1.2.1.6 | Setup backup system: PostgreSQL backup script (pg_dump), document backup (rsync), daily cron at 2 AM IST, 7-day retention | 4 |
| 2.1.2.1.7 | Setup monitoring: Docker health checks, service status script, email alerts for failures, /health endpoint in FastAPI | 3 |

---

## PHASE 3: Backend Core (2 weeks)

### EPIC 3.1: Authentication & Authorization

#### FEATURE 3.1.1: User Authentication

##### STORY 3.1.1.1: Implement JWT Authentication

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.1.1.1.1 | Create `users` table migration: id (UUID), email (unique), password_hash, role ENUM ('admin', 'hr', 'accountant', 'employee'), is_active, is_email_verified, password_changed_at, failed_login_attempts, locked_until, created_at, updated_at | 4 |
| 3.1.1.1.2 | Create User SQLAlchemy model and Pydantic schemas (UserCreate, UserUpdate, UserResponse); implement password hashing with bcrypt | 4 |
| 3.1.1.1.3 | Implement POST /api/v1/auth/login: validate credentials, check is_active and locked_until, generate JWT access token (15 min) and refresh token (7 days), increment failed_login_attempts on failure, lock after 5 failures | 6 |
| 3.1.1.1.4 | Implement POST /api/v1/auth/refresh: validate refresh token, check user active, generate new access token; implement token blacklisting with Redis | 4 |
| 3.1.1.1.5 | Implement POST /api/v1/auth/logout: blacklist refresh token in Redis with TTL | 3 |
| 3.1.1.1.6 | Create JWT dependency for protected routes: extract Bearer token, decode/validate JWT, fetch user, role-based dependencies (require_admin, require_hr, require_accountant, require_employee_or_above) | 4 |
| 3.1.1.1.7 | Implement POST /api/v1/auth/change-password: validate current password, enforce password policy (8+ chars, complexity), hash and update, invalidate all refresh tokens | 4 |
| 3.1.1.1.8 | Implement password reset flow: POST /forgot-password generates reset token (Redis, 1hr TTL), sends email; POST /reset-password validates token, updates password | 5 |

#### FEATURE 3.1.2: User Management

##### STORY 3.1.2.1: Implement User CRUD

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.1.2.1.1 | Implement POST /api/v1/users (admin only): create user with email, temp password, role; send welcome email | 4 |
| 3.1.2.1.2 | Implement GET /api/v1/users (admin/HR): paginated list with filters (role, is_active, search) | 4 |
| 3.1.2.1.3 | Implement GET /api/v1/users/{id}: return user details; employees can only view self | 3 |
| 3.1.2.1.4 | Implement PATCH /api/v1/users/{id} (admin only): update role, is_active; log changes | 3 |
| 3.1.2.1.5 | Implement DELETE /api/v1/users/{id} (admin only): soft delete by setting is_active=false, invalidate sessions | 3 |

### EPIC 3.2: Employee Management

#### FEATURE 3.2.1: Employee Master Data

##### STORY 3.2.1.1: Create Employee Data Model

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.2.1.1.1 | Create `employees` table migration: id, user_id (FK unique), employee_code (unique auto-gen), first_name, middle_name, last_name, date_of_birth, gender, blood_group, marital_status, nationality, profile_photo_path, onboarding_status ENUM, onboarding_completed_at, created_at, updated_at | 4 |
| 3.2.1.1.2 | Create `employee_contact` table: personal_email, personal_phone, emergency_contact (name, phone, relation), current_address, permanent_address, is_same_as_current | 4 |
| 3.2.1.1.3 | Create `employee_identity` table: pan_number (encrypted), aadhaar_number (encrypted), passport_number (encrypted), passport_expiry, driving_license, voter_id | 4 |
| 3.2.1.1.4 | Create `employee_bank` table: bank_name, branch_name, account_number (encrypted), ifsc_code, account_type, is_primary | 3 |
| 3.2.1.1.5 | Create `employee_employment` table: department_id (FK), designation_id (FK), reporting_manager_id (FK), employment_type, date_of_joining, probation_end_date, confirmation_date, date_of_exit, exit_reason, notice_period_days, current_status | 4 |
| 3.2.1.1.6 | Create `departments` table: name, code (unique), description, head_employee_id, is_active; seed defaults (Engineering, HR, Finance, Operations) | 3 |
| 3.2.1.1.7 | Create `designations` table: name, code, department_id (nullable), level, is_active; seed defaults | 3 |

##### STORY 3.2.1.2: Implement Employee API Endpoints

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.2.1.2.1 | Create Employee SQLAlchemy model with relationships; create Pydantic schemas with nested contact, identity, bank, employment | 6 |
| 3.2.1.2.2 | Implement POST /api/v1/employees (HR/admin): create employee linked to user_id, auto-generate employee_code (GCA-YYYY-XXXX), set onboarding_status='pending' | 5 |
| 3.2.1.2.3 | Implement GET /api/v1/employees: paginated list with filters (department, designation, status, search) | 5 |
| 3.2.1.2.4 | Implement GET /api/v1/employees/{id}: full details with nested data; employees view own, HR views all | 4 |
| 3.2.1.2.5 | Implement PATCH /api/v1/employees/{id}: partial updates with audit trail | 5 |
| 3.2.1.2.6 | Implement PUT /api/v1/employees/{id}/identity: update identity documents with encryption, validate PAN/Aadhaar format | 4 |
| 3.2.1.2.7 | Implement PUT /api/v1/employees/{id}/bank: update bank details with encryption, validate IFSC format | 3 |
| 3.2.1.2.8 | Implement employee code generation service: format GCA-{YYYY}-{XXXX}, thread-safe with database sequence | 4 |

#### FEATURE 3.2.2: Employment History

##### STORY 3.2.2.1: Manage Previous Employment & Education

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.2.2.1.1 | Create `employee_previous_employment` table: company_name, designation, department, start_date, end_date, last_drawn_salary, reason_for_leaving, reference details | 3 |
| 3.2.2.1.2 | Implement CRUD for previous employment: POST, GET, PUT, DELETE endpoints | 4 |
| 3.2.2.1.3 | Create `employee_education` table: qualification_type ENUM, institution_name, board_university, field_of_study, start_year, end_year, percentage_cgpa, is_highest_qualification | 3 |
| 3.2.2.1.4 | Implement CRUD for education with auto-calculation of is_highest_qualification | 4 |

### EPIC 3.3: Document Management Core

#### FEATURE 3.3.1: Employee Document Upload

##### STORY 3.3.1.1: Employee Document Management

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 3.3.1.1.1 | Create `employee_documents` table: employee_id, document_type ENUM (20+ types: profile_photo, resume_cv, pan_card, aadhaar, passport, address_proof, education certificates, payslips, offer_letter, relieving_letter, etc.), file_name, file_path, file_size, mime_type, description, uploaded_by, is_verified, verified_by, verified_at | 4 |
| 3.3.1.1.2 | Implement file storage service: save_file(), get_file(), delete_file(); store in /var/data/gana-portal/employees/{employee_id}/{document_type}/{timestamp}_{filename}; validate file types | 5 |
| 3.3.1.1.3 | Implement POST /api/v1/employees/{id}/documents: multipart upload, validate size (10MB max), validate mime type, save file, create record | 5 |
| 3.3.1.1.4 | Implement GET /api/v1/employees/{id}/documents: list documents with metadata | 3 |
| 3.3.1.1.5 | Implement GET /api/v1/employees/{id}/documents/{doc_id}/download: stream file with correct headers, log download | 3 |
| 3.3.1.1.6 | Implement DELETE /api/v1/employees/{id}/documents/{doc_id}: delete file and record, audit log | 3 |
| 3.3.1.1.7 | Implement PATCH /api/v1/employees/{id}/documents/{doc_id}/verify (HR/admin): mark verified | 2 |

---

## PHASE 4: Enterprise Document Management - EDMS (2 weeks)

### EPIC 4.1: Folder Management

#### FEATURE 4.1.1: Folder Hierarchy

##### STORY 4.1.1.1: Implement Folder Structure

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 4.1.1.1.1 | Create `folders` table: id, name, slug, parent_id (FK nullable), path (materialized path), depth, owner_id, is_system (protected), created_at, updated_at; unique constraint on (parent_id, name) | 4 |
| 4.1.1.1.2 | Create `folder_permissions` table: folder_id, user_id (nullable), role (nullable), permission ENUM ('view', 'upload', 'edit', 'delete', 'manage'), granted_by | 3 |
| 4.1.1.1.3 | Seed default folders: 'Company Documents', 'HR Documents', 'Policies', 'Templates', 'Employee Files', 'Accounting Documents', 'Projects' | 3 |
| 4.1.1.1.4 | Implement POST /api/v1/folders: create folder, validate parent permission, generate slug, calculate path, inherit permissions | 5 |
| 4.1.1.1.5 | Implement GET /api/v1/folders: return tree structure respecting permissions, support depth parameter, include document counts | 5 |
| 4.1.1.1.6 | Implement GET /api/v1/folders/{id}: folder details with children and documents, breadcrumb path | 4 |
| 4.1.1.1.7 | Implement PATCH /api/v1/folders/{id}: update name (regenerate slug, update child paths) | 4 |
| 4.1.1.1.8 | Implement POST /api/v1/folders/{id}/move: move folder to new parent, validate no circular reference, update paths | 5 |
| 4.1.1.1.9 | Implement DELETE /api/v1/folders/{id}: fail if system folder or has contents | 3 |
| 4.1.1.1.10 | Implement PUT /api/v1/folders/{id}/permissions: manage folder permissions | 4 |

### EPIC 4.2: Document Management

#### FEATURE 4.2.1: Document Upload & Storage

##### STORY 4.2.1.1: Implement Document CRUD

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 4.2.1.1.1 | Create `documents` table: id, folder_id, name, slug, file_path, file_size, mime_type, extension, current_version, uploaded_by, description, tags (TEXT[]), is_archived, created_at, updated_at; GIN index on tags | 4 |
| 4.2.1.1.2 | Create `document_versions` table: document_id, version_number, file_path, file_size, uploaded_by, change_notes, created_at | 3 |
| 4.2.1.1.3 | Implement POST /api/v1/folders/{folder_id}/documents: upload with validation (50MB max for EDMS), save to structured path, create document and version records | 6 |
| 4.2.1.1.4 | Implement GET /api/v1/folders/{folder_id}/documents: paginated list with sorting and filtering | 4 |
| 4.2.1.1.5 | Implement GET /api/v1/documents/{id}: document details with version history | 3 |
| 4.2.1.1.6 | Implement GET /api/v1/documents/{id}/download: stream file, support version parameter, log access | 4 |
| 4.2.1.1.7 | Implement POST /api/v1/documents/{id}/versions: upload new version, increment version number | 5 |
| 4.2.1.1.8 | Implement PATCH /api/v1/documents/{id}: update name, description, tags | 3 |
| 4.2.1.1.9 | Implement POST /api/v1/documents/{id}/move: move to different folder | 4 |
| 4.2.1.1.10 | Implement DELETE /api/v1/documents/{id}: soft or hard delete based on parameter | 4 |

#### FEATURE 4.2.2: Document Search

##### STORY 4.2.2.1: Implement Search

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 4.2.2.1.1 | Implement GET /api/v1/documents/search: full-text search on name, description; filters (folder with recursive, extension, tags, date range, uploaded_by) | 6 |
| 4.2.2.1.2 | Create PostgreSQL full-text search index: tsvector column, GIN index, trigger for updates | 4 |
| 4.2.2.1.3 | Implement GET /api/v1/documents/recent: last 20 accessed/uploaded by user | 3 |

#### FEATURE 4.2.3: Bulk Download

##### STORY 4.2.3.1: Folder Download

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 4.2.3.1.1 | Implement POST /api/v1/folders/{id}/download: trigger async ZIP creation, return job_id | 5 |
| 4.2.3.1.2 | Implement background ZIP job: collect documents, create ZIP preserving structure, store with 24hr expiry | 6 |
| 4.2.3.1.3 | Implement GET /api/v1/jobs/{job_id}: job status and download URL | 3 |
| 4.2.3.1.4 | Implement POST /api/v1/documents/bulk-download: create ZIP from array of document_ids | 5 |

---

## PHASE 5: Employee Onboarding (1.5 weeks)

### EPIC 5.1: Onboarding Workflow

#### FEATURE 5.1.1: Onboarding Steps

##### STORY 5.1.1.1: Define Onboarding Process

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 5.1.1.1.1 | Create `onboarding_steps` table: employee_id, step_number, step_name, step_type ENUM (8 types), status, completed_at | 3 |
| 5.1.1.1.2 | Create step initialization service: auto-create 8 steps (Personal Info, Contact, Identity, Bank, Education, Previous Employment, Documents, Declarations) | 4 |
| 5.1.1.1.3 | Implement GET /api/v1/employees/{id}/onboarding: all steps with status, completion %, pending items | 4 |
| 5.1.1.1.4 | Implement PUT /api/v1/employees/{id}/onboarding/{step}: update step data, mark complete if all required fields filled | 5 |
| 5.1.1.1.5 | Implement POST /api/v1/employees/{id}/onboarding/complete: validate all required steps and documents, update status, notify HR | 4 |

#### FEATURE 5.1.2: Document Checklist

##### STORY 5.1.2.1: Document Requirements

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 5.1.2.1.1 | Create `document_requirements` config: document_type, is_mandatory, applies_to ENUM ('all', 'experienced', 'fresher'); seed requirements | 4 |
| 5.1.2.1.2 | Implement GET /api/v1/employees/{id}/documents/checklist: required docs based on employee type, upload status | 4 |
| 5.1.2.1.3 | Implement completion validation: prevent onboarding completion if mandatory docs missing | 3 |

### EPIC 5.2: HR Onboarding Administration

#### FEATURE 5.2.1: Onboarding Dashboard

##### STORY 5.2.1.1: Onboarding Monitoring

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 5.2.1.1.1 | Implement GET /api/v1/hr/onboarding: employees with pending/in-progress onboarding, completion %, days since created | 5 |
| 5.2.1.1.2 | Implement POST /api/v1/hr/onboarding/{employee_id}/remind: send reminder email with pending items | 3 |
| 5.2.1.1.3 | Implement POST /api/v1/hr/onboarding/{employee_id}/approve: HR verification after completion | 3 |

---

## PHASE 6: Leave Management (1.5 weeks)

### EPIC 6.1: Leave Configuration

#### FEATURE 6.1.1: Leave Types & Policies

##### STORY 6.1.1.1: Setup Leave Types

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 6.1.1.1.1 | Create `leave_types` table: name, code (unique), description, is_paid, annual_quota, can_carry_forward, max_carry_forward, requires_approval, min_notice_days, max_consecutive_days, is_active | 4 |
| 6.1.1.1.2 | Seed India leave types: CL (12), SL (6), EL (15 with carry forward 30), LOP, CO, ML (182), PL (15), BL (5), MRL (3) | 3 |
| 6.1.1.1.3 | Implement CRUD for leave types (admin only) | 4 |

#### FEATURE 6.1.2: Holiday Calendar

##### STORY 6.1.2.1: Company Holidays

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 6.1.2.1.1 | Create `holidays` table: name, date, holiday_type ENUM, is_optional, year | 3 |
| 6.1.2.1.2 | Seed 2025-2026 India national holidays + Karnataka state holidays | 2 |
| 6.1.2.1.3 | Implement CRUD for holidays (HR/admin) | 4 |
| 6.1.2.1.4 | Implement GET /api/v1/holidays/calendar: iCal or JSON calendar format | 3 |

### EPIC 6.2: Leave Balances

#### FEATURE 6.2.1: Balance Management

##### STORY 6.2.1.1: Track Leave Balances

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 6.2.1.1.1 | Create `leave_balances` table: employee_id, leave_type_id, year, opening_balance, credited, used, pending, available, lapsed, carry_forward_from_previous | 4 |
| 6.2.1.1.2 | Implement balance initialization: on join (pro-rate) and new year (with carry forward calculation) | 5 |
| 6.2.1.1.3 | Implement GET /api/v1/employees/{id}/leave-balance: all balances for current year | 4 |
| 6.2.1.1.4 | Implement POST /api/v1/employees/{id}/leave-balance/credit (HR): manual credit (e.g., comp off) | 4 |
| 6.2.1.1.5 | Implement year-end processing job: calculate carry forward, lapse remaining, create new year balances | 5 |

### EPIC 6.3: Leave Requests

#### FEATURE 6.3.1: Leave Application

##### STORY 6.3.1.1: Apply for Leave

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 6.3.1.1.1 | Create `leave_requests` table: employee_id, leave_type_id, start_date, end_date, start_half, end_half, total_days, reason, status ENUM, applied_on, approved_by, approved_on, rejection_reason | 4 |
| 6.3.1.1.2 | Implement leave day calculation: exclude weekends and holidays, handle half-days | 5 |
| 6.3.1.1.3 | Implement POST /api/v1/leave-requests: validate dates, calculate days, check balance, check policies, create request, deduct from pending, notify manager | 6 |
| 6.3.1.1.4 | Implement GET /api/v1/leave-requests: paginated with filters; employees see own, managers see team, HR sees all | 4 |
| 6.3.1.1.5 | Implement GET /api/v1/leave-requests/{id}: full details | 3 |
| 6.3.1.1.6 | Implement POST /api/v1/leave-requests/{id}/cancel: cancel if pending/approved and future; restore balance | 3 |

#### FEATURE 6.3.2: Leave Approval

##### STORY 6.3.2.1: Approval Workflow

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 6.3.2.1.1 | Implement GET /api/v1/leave-requests/pending-approval: requests from direct reports | 4 |
| 6.3.2.1.2 | Implement POST /api/v1/leave-requests/{id}/approve: update status, move pending to used, notify employee | 4 |
| 6.3.2.1.3 | Implement POST /api/v1/leave-requests/{id}/reject: require reason, restore balance, notify employee | 4 |
| 6.3.2.1.4 | Implement team leave calendar: GET /api/v1/teams/{manager_id}/leave-calendar | 4 |

---

## PHASE 7: Timesheet Management (1 week)

### EPIC 7.1: Project Setup

#### FEATURE 7.1.1: Project Management (Basic)

##### STORY 7.1.1.1: Manage Projects

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 7.1.1.1.1 | Create `projects` table: name, code (unique), client_name, description, project_manager_id, start_date, end_date, status ENUM, is_billable, hourly_rate, budget_hours | 4 |
| 7.1.1.1.2 | Create `project_members` table: project_id, employee_id, role, allocation_percentage, start_date, end_date, is_active | 3 |
| 7.1.1.1.3 | Implement CRUD for projects (HR/admin/PM) | 5 |
| 7.1.1.1.4 | Implement project member management endpoints | 4 |
| 7.1.1.1.5 | Implement GET /api/v1/employees/{id}/projects: projects assigned to employee | 3 |

### EPIC 7.2: Timesheet Entry

#### FEATURE 7.2.1: Time Logging

##### STORY 7.2.1.1: Daily Time Entry

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 7.2.1.1.1 | Create `timesheets` table: employee_id, week_start_date (Monday), status ENUM, total_hours, submitted_at, approved_by, approved_at, rejection_reason | 4 |
| 7.2.1.1.2 | Create `timesheet_entries` table: timesheet_id, project_id, entry_date, hours, description, task_type ENUM, is_billable | 3 |
| 7.2.1.1.3 | Implement GET /api/v1/timesheets/current: current week timesheet, auto-create if not exists | 5 |
| 7.2.1.1.4 | Implement POST /api/v1/timesheets/{id}/entries: add/update entry, validate hours ≤24/day, recalculate totals | 5 |
| 7.2.1.1.5 | Implement PUT /api/v1/timesheets/{id}/entries/{entry_id}: update entry (only if draft) | 3 |
| 7.2.1.1.6 | Implement DELETE /api/v1/timesheets/{id}/entries/{entry_id}: delete entry (only if draft) | 2 |
| 7.2.1.1.7 | Implement GET /api/v1/timesheets: paginated list with filters | 4 |

#### FEATURE 7.2.2: Submission & Approval

##### STORY 7.2.2.1: Submit and Approve

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 7.2.2.1.1 | Implement POST /api/v1/timesheets/{id}/submit: validate, change status, notify manager | 4 |
| 7.2.2.1.2 | Implement GET /api/v1/timesheets/pending-approval: for managers | 4 |
| 7.2.2.1.3 | Implement POST /api/v1/timesheets/{id}/approve | 3 |
| 7.2.2.1.4 | Implement POST /api/v1/timesheets/{id}/reject: with reason | 3 |
| 7.2.2.1.5 | Implement POST /api/v1/timesheets/{id}/recall: recall submitted timesheet | 2 |

### EPIC 7.3: Timesheet Reports

#### FEATURE 7.3.1: Time Reports

##### STORY 7.3.1.1: Generate Reports

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 7.3.1.1.1 | Implement GET /api/v1/reports/timesheet/summary: aggregate by filters, group by employee/project/week | 6 |
| 7.3.1.1.2 | Implement GET /api/v1/reports/timesheet/project/{id}: project time report | 4 |
| 7.3.1.1.3 | Implement GET /api/v1/reports/timesheet/export: CSV/Excel export | 4 |

---

## PHASE 8: Payroll System (3 weeks)

### EPIC 8.1: Salary Structure

#### FEATURE 8.1.1: CTC Components

##### STORY 8.1.1.1: Define Salary Structure

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.1.1.1.1 | Create `salary_components` table: name, code (unique), component_type ENUM ('earning', 'deduction', 'employer_contribution'), calculation_type, percentage_of, is_taxable, is_part_of_ctc, is_statutory, display_order, is_active | 4 |
| 8.1.1.1.2 | Seed standard India components: Basic, HRA, Special Allowance, Conveyance, Medical, LTA, PF Employee (12%), ESI Employee (0.75%), PT, TDS, PF Employer (12%), ESI Employer (3.25%), Gratuity (4.81%) | 4 |
| 8.1.1.1.3 | Implement CRUD for salary components (admin) | 4 |

#### FEATURE 8.1.2: Employee Salary Assignment

##### STORY 8.1.2.1: Assign Salary

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.1.2.1.1 | Create `employee_salary` table: employee_id (unique), annual_ctc, effective_from, effective_to, is_current, pf_opt_out, esi_applicable, created_by | 4 |
| 8.1.2.1.2 | Create `employee_salary_components` table: employee_salary_id, component_id, monthly_amount, annual_amount | 3 |
| 8.1.2.1.3 | Implement salary calculation service: from annual_ctc calculate all components (Basic 40%, HRA 50% of Basic, PF, ESI if applicable, Gratuity, Special Allowance as balance) | 8 |
| 8.1.2.1.4 | Implement POST /api/v1/employees/{id}/salary: create salary structure from CTC | 6 |
| 8.1.2.1.5 | Implement GET /api/v1/employees/{id}/salary: current structure with history | 4 |
| 8.1.2.1.6 | Implement salary revision endpoint | 4 |

### EPIC 8.2: Tax Declarations

#### FEATURE 8.2.1: IT Declarations

##### STORY 8.2.1.1: Tax Declaration Submission

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.2.1.1.1 | Create `tax_declarations` table: employee_id, financial_year, tax_regime ENUM ('old', 'new'), status, submitted_at, approved_by | 4 |
| 8.2.1.1.2 | Create `tax_declaration_items` table: declaration_id, section (80C, 80D, 24, HRA, etc.), item_name, declared_amount, actual_amount, proof_document_id, proof_status | 3 |
| 8.2.1.1.3 | Implement GET /api/v1/tax-declarations/current: current FY declaration, auto-create if not exists | 6 |
| 8.2.1.1.4 | Implement PUT /api/v1/tax-declarations/{id}/items: update declaration items with section limit validation | 5 |
| 8.2.1.1.5 | Implement POST /api/v1/tax-declarations/{id}/submit: lock for edits until proof window | 3 |
| 8.2.1.1.6 | Implement tax calculation service (old regime): gross - standard deduction - exemptions, apply slabs, add cess 4% | 6 |
| 8.2.1.1.7 | Implement tax calculation service (new regime): simplified slabs, compare with old, suggest optimal | 5 |

### EPIC 8.3: Payroll Processing

#### FEATURE 8.3.1: Monthly Payroll

##### STORY 8.3.1.1: Process Payroll

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.3.1.1.1 | Create `payroll_runs` table: month, year, status ENUM, totals (gross, deductions, net, employer_cost), employee_count, processed_by/at, approved_by/at, payment_date | 4 |
| 8.3.1.1.2 | Create `payslips` table: payroll_run_id, employee_id, employee_salary_id, month, year, gross, earnings, deductions, net, employer_contributions, working_days, days_worked, lop_days, status, pdf_path | 4 |
| 8.3.1.1.3 | Create `payslip_components` table: payslip_id, component_id, component_type, amount, ytd_amount | 3 |
| 8.3.1.1.4 | Implement LOP calculation: count approved unpaid leave, calculate deduction | 4 |
| 8.3.1.1.5 | Implement payslip generation service: fetch salary, get working days, calculate LOP, prorate earnings, calculate PF/ESI/PT/TDS, create payslip with components | 8 |
| 8.3.1.1.6 | Implement POST /api/v1/payroll/run: create run for month/year, generate payslips for all active employees | 6 |
| 8.3.1.1.7 | Implement GET /api/v1/payroll/runs: list runs with filters | 3 |
| 8.3.1.1.8 | Implement GET /api/v1/payroll/runs/{id}: run details with all payslips | 3 |
| 8.3.1.1.9 | Implement POST /api/v1/payroll/runs/{id}/approve | 3 |
| 8.3.1.1.10 | Implement POST /api/v1/payroll/runs/{id}/finalize: generate PDFs, mark paid | 4 |

#### FEATURE 8.3.2: Statutory Calculations

##### STORY 8.3.2.1: PF, ESI, PT

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.3.2.1.1 | Implement PF calculation: 12% employee on PF wage (Basic+DA, capped ₹15K), employer split (EPS 8.33% capped ₹1250, EPF remainder), admin charges | 5 |
| 8.3.2.1.2 | Implement ESI calculation: check ≤₹21K threshold, 0.75% employee + 3.25% employer, handle mid-period crossing | 4 |
| 8.3.2.1.3 | Implement PT calculation: Karnataka rules (>₹15K = ₹200/month, Feb = ₹300) | 4 |

### EPIC 8.4: Payslip Generation

#### FEATURE 8.4.1: Payslip PDF

##### STORY 8.4.1.1: Generate Payslips

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.4.1.1.1 | Create payslip PDF template: company header, employee details, pay period, earnings table, deductions table, net pay in words, employer contributions, leave balance | 6 |
| 8.4.1.1.2 | Implement POST /api/v1/payslips/{id}/generate-pdf: render and save PDF | 5 |
| 8.4.1.1.3 | Implement GET /api/v1/payslips/{id}/download: stream PDF | 3 |
| 8.4.1.1.4 | Implement bulk PDF generation for payroll run | 4 |
| 8.4.1.1.5 | Implement email distribution of payslips | 4 |

#### FEATURE 8.4.2: Employee Payslip Access

##### STORY 8.4.2.1: View Payslips

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.4.2.1.1 | Implement GET /api/v1/employees/{id}/payslips: list with year filter | 3 |
| 8.4.2.1.2 | Implement GET /api/v1/employees/{id}/payslips/{payslip_id}: details with components | 3 |
| 8.4.2.1.3 | Implement YTD calculation service | 4 |

### EPIC 8.5: Form 16

#### FEATURE 8.5.1: Form 16 Generation

##### STORY 8.5.1.1: Generate Form 16

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 8.5.1.1.1 | Create `form16_data` table: employee_id, financial_year, part_a_generated, part_b_generated, gross_salary, exemptions_json, taxable_income, tax_computed, tds_deducted, refund_due, pdf_path | 4 |
| 8.5.1.1.2 | Implement Form 16 Part B calculation: aggregate FY data, exempt allowances, Chapter VI-A deductions, compute tax, compare with TDS | 8 |
| 8.5.1.1.3 | Create Form 16 PDF template per IT department format | 6 |
| 8.5.1.1.4 | Implement POST /api/v1/form16/generate/{employee_id}/{fy} | 5 |
| 8.5.1.1.5 | Implement bulk Form 16 generation | 4 |
| 8.5.1.1.6 | Implement GET /api/v1/employees/{id}/form16: list by FY | 3 |

---

## PHASE 9: Company Onboarding & Statutory (1 week)

### EPIC 9.1: Company Master Data

#### FEATURE 9.1.1: Company Profile

##### STORY 9.1.1.1: Company Registration

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.1.1.1.1 | Create `company_profile` table: company_name, legal_name, cin_number, company_pan, gstin, incorporation_date, registered_address, operational_address, logo_path, website, email, phone | 4 |
| 9.1.1.1.2 | Create `company_statutory` table: pf_establishment_code, pf_registration_date, esi_code, esi_registration_date, tan_number, pt_registration_number, pt_state, lwf_registration, gratuity_trust_name | 4 |
| 9.1.1.1.3 | Create `company_bank_accounts` table: account_name, bank_name, branch, account_number (encrypted), ifsc_code, swift_code, account_type, is_salary_account, is_statutory_account, is_primary | 3 |
| 9.1.1.1.4 | Create `authorized_signatories` table: employee_id, signatory_name, designation, signatory_type, pan, email, phone, is_pf_signatory, is_esi_signatory, is_tds_signatory, digital_signature_path, is_active | 4 |
| 9.1.1.1.5 | Implement GET /api/v1/company: profile with statutory details | 3 |
| 9.1.1.1.6 | Implement PUT /api/v1/company: update profile with format validation (CIN, PAN, GSTIN) | 4 |
| 9.1.1.1.7 | Implement PUT /api/v1/company/statutory: update registrations with format validation | 4 |
| 9.1.1.1.8 | Implement CRUD for company bank accounts | 4 |
| 9.1.1.1.9 | Implement CRUD for authorized signatories | 3 |
| 9.1.1.1.10 | Create first-time setup wizard: redirect to /setup/company if profile empty | 4 |

### EPIC 9.2: PF Compliance

#### FEATURE 9.2.1: PF ECR Generation

##### STORY 9.2.1.1: Generate ECR

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.2.1.1.1 | Create `pf_filings` table: month, year, filing_type, totals (employees, wages, contributions), trrn, ecr_file_path, status, acknowledgement_number | 4 |
| 9.2.1.1.2 | Create `pf_filing_details` table: pf_filing_id, employee_id, uan, member_name, pf_wages, contributions breakdown, ncp_days | 3 |
| 9.2.1.1.3 | Implement PF ECR calculation service | 6 |
| 9.2.1.1.4 | Implement ECR text file generation per EPFO format | 6 |
| 9.2.1.1.5 | Implement POST /api/v1/statutory/pf/ecr/generate | 5 |
| 9.2.1.1.6 | Implement GET /api/v1/statutory/pf/ecr: list filings | 3 |
| 9.2.1.1.7 | Implement GET /api/v1/statutory/pf/ecr/{id}: filing details | 3 |
| 9.2.1.1.8 | Implement download endpoint | 2 |
| 9.2.1.1.9 | Implement acknowledge endpoint | 2 |

### EPIC 9.3: ESI Compliance

#### FEATURE 9.3.1: ESI Return

##### STORY 9.3.1.1: Generate ESI Return

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.3.1.1.1 | Create `esi_filings` table: contribution_period, year, month, totals, challan_number, challan_date, file_path, status | 4 |
| 9.3.1.1.2 | Create `esi_filing_details` table: filing_id, employee_id, ip_number, wages, contributions, reason_code | 3 |
| 9.3.1.1.3 | Implement ESI calculation service | 5 |
| 9.3.1.1.4 | Implement ESI return file generation | 5 |
| 9.3.1.1.5 | Implement POST /api/v1/statutory/esi/return/generate | 4 |
| 9.3.1.1.6 | Implement list and download endpoints | 3 |
| 9.3.1.1.7 | Implement challan update endpoint | 2 |
| 9.3.1.1.8 | (Reserved) | 2 |

### EPIC 9.4: TDS Compliance

#### FEATURE 9.4.1: TDS 24Q Return

##### STORY 9.4.1.1: Generate 24Q

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.4.1.1.1 | Create `tds_filings` table: quarter, financial_year, form_type, totals, file_path, fvu_file_path, status, receipt_number, acknowledgement_number | 4 |
| 9.4.1.1.2 | Create `tds_filing_details` table: filing_id, employee_id, pan, name, section_code, amounts, challan details | 4 |
| 9.4.1.1.3 | Create `tds_challans` table: financial_year, challan_serial, bsr_code, deposit_date, amount, minor_head, assessment_year | 3 |
| 9.4.1.1.4 | Implement 24Q data aggregation service | 6 |
| 9.4.1.1.5 | Implement 24Q text file generation per NSDL specs | 8 |
| 9.4.1.1.6 | Implement POST /api/v1/statutory/tds/24q/generate | 5 |
| 9.4.1.1.7 | Implement TDS challan management endpoints | 4 |
| 9.4.1.1.8 | Implement list and download endpoints | 3 |
| 9.4.1.1.9 | Implement filed endpoint | 2 |
| 9.4.1.1.10 | (Reserved) | 2 |

### EPIC 9.5: Salary Bank Transfer

#### FEATURE 9.5.1: Bank File Generation

##### STORY 9.5.1.1: Generate NEFT File

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.5.1.1.1 | Create `salary_disbursements` table: payroll_run_id, disbursement_date, total_employees, total_amount, company_bank_account_id, transfer_type, file_path, status, utr_number | 4 |
| 9.5.1.1.2 | Create `salary_disbursement_details` table: disbursement_id, employee_id, payslip_id, beneficiary details, amount, status, utr, failure_reason | 3 |
| 9.5.1.1.3 | Implement NEFT file generation service | 5 |
| 9.5.1.1.4 | Implement POST /api/v1/payroll/runs/{id}/generate-bank-file | 5 |
| 9.5.1.1.5 | Implement list and download endpoints | 3 |
| 9.5.1.1.6 | Implement mark-processed endpoint | 2 |

### EPIC 9.6: Accountant Role

#### FEATURE 9.6.1: Accountant Access

##### STORY 9.6.1.1: Configure Permissions

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 9.6.1.1.1 | Update users role ENUM to include 'accountant'; update auth dependencies | 3 |
| 9.6.1.1.2 | Define accountant permissions: full EDMS, view-only payroll, view+download statutory, financial reports | 4 |
| 9.6.1.1.3 | Update API endpoints with accountant role checks | 4 |
| 9.6.1.1.4 | Create default EDMS folders for accountant: Accounting, Tax Filings, Compliance, Audit, Bank Statements, Invoices | 3 |
| 9.6.1.1.5 | Build accountant dashboard | 4 |
| 9.6.1.1.6 | Update user creation for accountant role | 3 |

---

# PART B: ACCOUNTING & AI

---

## PHASE 10: AI Core Infrastructure (1 week)

### EPIC 10.1: AI Integration

#### FEATURE 10.1.1: Claude API Integration

##### STORY 10.1.1.1: Setup AI Services

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 10.1.1.1.1 | Create AI service configuration: Claude API client, API key management, rate limiting, retry logic, cost tracking | 5 |
| 10.1.1.1.2 | Create `ai_requests` table for logging: request_type, tokens, model, latency, user_id, entity_type/id, success, error | 3 |
| 10.1.1.1.3 | Implement AI context manager: build context with company profile, chart of accounts, recent transactions; manage token limits | 5 |
| 10.1.1.1.4 | Create base AI prompt templates: document_extraction, categorization, query_engine, insight_generator | 6 |
| 10.1.1.1.5 | Implement AI response parser: parse JSON, handle malformed responses, validate schema, extract confidence scores | 4 |
| 10.1.1.1.6 | Create AI feedback mechanism: store corrections, improve prompts over time | 4 |

#### FEATURE 10.1.2: Document Processing

##### STORY 10.1.2.1: Universal Document Processor

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 10.1.2.1.1 | Implement PDF to image conversion: pdf2image/poppler, multi-page, 300 DPI | 4 |
| 10.1.2.1.2 | Implement image preprocessing: resize, contrast, skew correction | 4 |
| 10.1.2.1.3 | Create document type classifier: Claude Vision classifies (invoice, bill, statement, receipt, etc.) | 4 |
| 10.1.2.1.4 | Implement bank statement extraction prompt | 6 |
| 10.1.2.1.5 | Implement vendor bill extraction prompt | 6 |
| 10.1.2.1.6 | Implement Excel/CSV parser with AI column mapping | 5 |
| 10.1.2.1.7 | Create POST /api/v1/ai/process-document endpoint | 5 |

---

## PHASE 11: Chart of Accounts & General Ledger (1.5 weeks)

### EPIC 11.1: Chart of Accounts

#### FEATURE 11.1.1: Account Structure

##### STORY 11.1.1.1: Setup Accounts

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 11.1.1.1.1 | Create `account_groups` table: name, code, group_type ENUM, parent_id, sequence, is_system | 3 |
| 11.1.1.1.2 | Create `accounts` table: name, code (unique), account_group_id, account_type ENUM, currency, is_system, is_active, opening_balance, opening_balance_date, description | 4 |
| 11.1.1.1.3 | Seed account groups for IT services: Assets, Liabilities, Equity, Income, Expenses with subgroups | 3 |
| 11.1.1.1.4 | Seed 50-60 default accounts: banks, AR, AP, GST, TDS, revenue by type, expenses by category | 4 |
| 11.1.1.1.5 | Implement GET /api/v1/accounts: hierarchical chart with balances | 4 |
| 11.1.1.1.6 | Implement POST /api/v1/accounts | 3 |
| 11.1.1.1.7 | Implement PUT /api/v1/accounts/{id} | 3 |
| 11.1.1.1.8 | Implement account balance calculation service with caching | 4 |

### EPIC 11.2: General Ledger

#### FEATURE 11.2.1: Journal Entries

##### STORY 11.2.1.1: Implement Journal System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 11.2.1.1.1 | Create `journal_entries` table: entry_number, entry_date, reference_type ENUM, reference_id, narration, totals, status ENUM, posted_by/at, reversed_by/at, reversal_entry_id, period_id | 4 |
| 11.2.1.1.2 | Create `journal_entry_lines` table: journal_entry_id, account_id, debit, credit, currency, exchange_rate, base amounts, narration | 4 |
| 11.2.1.1.3 | Create `accounting_periods` table: name, start_date, end_date, financial_year, is_closed, closed_by/at | 3 |
| 11.2.1.1.4 | Implement validation: debit = credit, accounts exist, period not closed | 4 |
| 11.2.1.1.5 | Implement entry number generation: JV-{FY}-{SEQUENCE} | 3 |
| 11.2.1.1.6 | Implement POST /api/v1/journal-entries | 4 |
| 11.2.1.1.7 | Implement POST /api/v1/journal-entries/{id}/post | 3 |
| 11.2.1.1.8 | Implement POST /api/v1/journal-entries/{id}/reverse | 4 |
| 11.2.1.1.9 | Implement GET /api/v1/journal-entries with filters | 4 |
| 11.2.1.1.10 | Implement GET /api/v1/accounts/{id}/ledger | 4 |

#### FEATURE 11.2.2: Period Management

##### STORY 11.2.2.1: Accounting Periods

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 11.2.2.1.1 | Implement period initialization for financial year | 3 |
| 11.2.2.1.2 | Implement POST /api/v1/accounting-periods/{id}/close | 4 |
| 11.2.2.1.3 | Implement year-end closing: transfer P&L to Retained Earnings, create new year opening | 5 |

---

## PHASE 12: Multi-Currency Support (1 week)

### EPIC 12.1: Currency Management

#### FEATURE 12.1.1: Exchange Rates

##### STORY 12.1.1.1: Implement Currency System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 12.1.1.1.1 | Create `currencies` table: code, name, symbol, decimal_places, is_active; seed INR, USD, EUR, GBP, AUD, CAD, SGD, AED | 3 |
| 12.1.1.1.2 | Create `exchange_rates` table: from_currency, to_currency, rate, rate_date, source ENUM | 3 |
| 12.1.1.1.3 | Implement exchange rate service: get_rate(), convert_amount() with caching | 4 |
| 12.1.1.1.4 | Implement RBI reference rate fetcher (scheduled daily) | 5 |
| 12.1.1.1.5 | Implement GET /api/v1/exchange-rates | 3 |
| 12.1.1.1.6 | Implement POST /api/v1/exchange-rates (manual entry) | 2 |
| 12.1.1.1.7 | Implement forex gain/loss calculation service | 5 |

---

## PHASE 13: Customer Invoicing - AR (2 weeks)

### EPIC 13.1: Customer Management

#### FEATURE 13.1.1: Customer Master

##### STORY 13.1.1.1: Customer Records

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.1.1.1.1 | Create `customers` table: customer_code, customer_type, company_name, contact_person, email, phone, website, billing_address, shipping_address, is_domestic, gstin, pan, tax_id, currency, payment_terms_days, credit_limit, ar_account_id, is_active, notes | 5 |
| 13.1.1.1.2 | Implement customer code generation: CUST-{SEQ} | 2 |
| 13.1.1.1.3 | Implement POST /api/v1/customers with GSTIN validation | 4 |
| 13.1.1.1.4 | Implement GET /api/v1/customers with filters and outstanding | 4 |
| 13.1.1.1.5 | Implement GET /api/v1/customers/{id} with history | 3 |
| 13.1.1.1.6 | Implement PUT /api/v1/customers/{id} | 3 |
| 13.1.1.1.7 | Implement AI customer extraction from email/document | 4 |

### EPIC 13.2: Sales Invoicing

#### FEATURE 13.2.1: Invoice Generation

##### STORY 13.2.1.1: Create Invoices

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.2.1.1.1 | Create `invoices` table: invoice_number, invoice_type ENUM, customer_id, dates, currency, exchange_rate, supply_type, place_of_supply, is_export, lut_number, shipping_bill details, amounts (subtotal, GST breakup, total), balance_due, status ENUM, journal_entry_id, pdf_path, notes, terms | 6 |
| 13.2.1.1.2 | Create `invoice_line_items` table: invoice_id, description, hsn_sac_code, quantity, unit, rate, amount, GST breakup | 4 |
| 13.2.1.1.3 | Implement invoice number generation: INV/{FY}/{SEQ}, PI/{FY}/{SEQ}, CN/{FY}/{SEQ} | 4 |
| 13.2.1.1.4 | Implement GST calculation service: determine CGST+SGST or IGST, handle exports | 5 |
| 13.2.1.1.5 | Implement amount in words (English) | 3 |
| 13.2.1.1.6 | Implement POST /api/v1/invoices | 5 |
| 13.2.1.1.7 | Implement POST /api/v1/invoices/{id}/finalize with journal entry | 4 |
| 13.2.1.1.8 | Implement POST /api/v1/invoices/{id}/cancel with reversal | 3 |
| 13.2.1.1.9 | Implement GET /api/v1/invoices with filters | 4 |
| 13.2.1.1.10 | Implement GET /api/v1/invoices/{id} | 3 |

#### FEATURE 13.2.2: Invoice PDF

##### STORY 13.2.2.1: Generate Documents

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.2.2.1.1 | Create domestic invoice PDF template | 6 |
| 13.2.2.1.2 | Create export invoice PDF template | 5 |
| 13.2.2.1.3 | Implement POST /api/v1/invoices/{id}/generate-pdf | 4 |
| 13.2.2.1.4 | Implement POST /api/v1/invoices/{id}/send-email | 4 |

#### FEATURE 13.2.3: AI Invoicing

##### STORY 13.2.3.1: Natural Language Invoice

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.2.3.1.1 | Implement AI invoice generation prompt | 6 |
| 13.2.3.1.2 | Implement POST /api/v1/ai/generate-invoice | 4 |
| 13.2.3.1.3 | Implement AI HSN/SAC code suggestion | 4 |
| 13.2.3.1.4 | Implement recurring invoice detection | 4 |

### EPIC 13.3: Payment Receipts

#### FEATURE 13.3.1: Customer Payments

##### STORY 13.3.1.1: Payment System

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.3.1.1.1 | Create `receipts` table: receipt_number, customer_id, date, amount, currency, exchange_rate, payment_mode ENUM, reference, bank_account_id, firc details, forex_gain_loss, status, journal_entry_id | 5 |
| 13.3.1.1.2 | Create `receipt_allocations` table: receipt_id, invoice_id, allocated_amount | 3 |
| 13.3.1.1.3 | Implement receipt number generation | 2 |
| 13.3.1.1.4 | Implement POST /api/v1/receipts with allocation and forex handling | 6 |
| 13.3.1.1.5 | Implement GET /api/v1/receipts | 3 |
| 13.3.1.1.6 | Implement GET /api/v1/customers/{id}/outstanding | 4 |
| 13.3.1.1.7 | Implement AR aging report | 4 |

### EPIC 13.4: Export Compliance

#### FEATURE 13.4.1: LUT & FIRC

##### STORY 13.4.1.1: Export Documentation

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 13.4.1.1.1 | Create `lut_records` table: lut_number, financial_year, dates, arn_number, status, document_path | 3 |
| 13.4.1.1.2 | Implement LUT tracking with expiry alerts | 3 |
| 13.4.1.1.3 | Implement FIRC tracking on receipts | 3 |
| 13.4.1.1.4 | Implement export invoice validation (LUT required, FIRC warning) | 3 |
| 13.4.1.1.5 | Implement GET /api/v1/reports/export-summary | 4 |

---

## PHASE 14: Vendor Bills - AP (1.5 weeks)

### EPIC 14.1: Vendor Management

#### FEATURE 14.1.1: Vendor Master

##### STORY 14.1.1.1: Vendor Records

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 14.1.1.1.1 | Create `vendors` table: vendor_code, vendor_type, vendor_name, contact details, address, is_domestic, gstin, pan, tan, is_msme, tds_applicable, tds_section, tds_rate, currency, payment_terms_days, ap_account_id, bank_details (encrypted), is_active | 5 |
| 14.1.1.1.2 | Seed TDS sections: 194C (1%/2%), 194J (10%), 194H (5%), 194I (10%), 194Q (0.1%) | 2 |
| 14.1.1.1.3 | Implement vendor code generation | 2 |
| 14.1.1.1.4 | Implement CRUD for vendors with validation | 4 |
| 14.1.1.1.5 | Implement AI vendor extraction from bill | 4 |

### EPIC 14.2: Bill Management

#### FEATURE 14.2.1: Bill Entry

##### STORY 14.2.1.1: Record Bills

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 14.2.1.1.1 | Create `bills` table: bill_number, internal_reference, vendor_id, dates, currency, exchange_rate, supply_type, place_of_supply, amounts, tds details, net_payable, balance_due, expense_account_id, status ENUM, document_path, journal_entry_id | 6 |
| 14.2.1.1.2 | Create `bill_line_items` table | 3 |
| 14.2.1.1.3 | Implement internal reference generation | 2 |
| 14.2.1.1.4 | Implement TDS calculation with threshold tracking | 5 |
| 14.2.1.1.5 | Implement ITC eligibility check | 3 |
| 14.2.1.1.6 | Implement POST /api/v1/bills | 5 |
| 14.2.1.1.7 | Implement POST /api/v1/bills/{id}/approve with journal entry | 4 |
| 14.2.1.1.8 | Implement GET /api/v1/bills with overdue highlighting | 4 |

#### FEATURE 14.2.2: AI Bill Processing

##### STORY 14.2.2.1: Automated Entry

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 14.2.2.1.1 | Implement POST /api/v1/ai/process-bill | 6 |
| 14.2.2.1.2 | Implement vendor matching service (fuzzy match) | 4 |
| 14.2.2.1.3 | Implement AI expense categorization | 4 |
| 14.2.2.1.4 | Implement duplicate bill detection | 3 |

### EPIC 14.3: Vendor Payments

#### FEATURE 14.3.1: Payments

##### STORY 14.3.1.1: Payment to Vendors

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 14.3.1.1.1 | Create `payments` table: payment_number, vendor_id, date, amount, currency, payment_mode, reference, bank_account_id, status, tds_deducted, journal_entry_id | 4 |
| 14.3.1.1.2 | Create `payment_allocations` table | 3 |
| 14.3.1.1.3 | Implement payment number generation | 2 |
| 14.3.1.1.4 | Implement POST /api/v1/payments with TDS and journal entry | 5 |
| 14.3.1.1.5 | Implement GET /api/v1/vendors/{id}/outstanding | 3 |
| 14.3.1.1.6 | Implement AP aging report | 4 |
| 14.3.1.1.7 | Implement payment bank file generation | 4 |

---

## PHASE 15: Bank & Cash Management (1 week)

### EPIC 15.1: Bank Accounts

#### FEATURE 15.1.1: Bank Setup

##### STORY 15.1.1.1: Bank Accounts

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 15.1.1.1.1 | Create `bank_accounts` table: account_name, bank_name, branch, account_number (encrypted), ifsc_code, swift_code, account_type ENUM, currency, gl_account_id, opening_balance, current_balance, is_active | 4 |
| 15.1.1.1.2 | Implement bank account CRUD | 3 |
| 15.1.1.1.3 | Create bank transactions view | 4 |

### EPIC 15.2: Bank Reconciliation

#### FEATURE 15.2.1: AI Reconciliation

##### STORY 15.2.1.1: Statement Import & Matching

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 15.2.1.1.1 | Create `bank_statements` table: bank_account_id, dates, balances, file_path, upload_type, status | 3 |
| 15.2.1.1.2 | Create `bank_statement_lines` table: statement_id, dates, description, reference, amounts, category, matched IDs (receipt/payment/journal), match_status ENUM, match_confidence | 4 |
| 15.2.1.1.3 | Implement POST /api/v1/bank-accounts/{id}/upload-statement with AI extraction | 5 |
| 15.2.1.1.4 | Implement AI transaction categorization | 6 |
| 15.2.1.1.5 | Implement auto-matching service | 5 |
| 15.2.1.1.6 | Implement GET /api/v1/bank-statements/{id}/reconciliation | 4 |
| 15.2.1.1.7 | Implement POST /api/v1/bank-statements/{id}/lines/{line_id}/match | 3 |
| 15.2.1.1.8 | Implement POST /api/v1/bank-statements/{id}/lines/{line_id}/create-entry | 4 |
| 15.2.1.1.9 | Implement bank reconciliation report | 5 |

### EPIC 15.3: Cash Management

#### FEATURE 15.3.1: Petty Cash

##### STORY 15.3.1.1: Petty Cash

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 15.3.1.1.1 | Create `petty_cash_entries` table | 3 |
| 15.3.1.1.2 | Implement petty cash CRUD with journal entries | 4 |
| 15.3.1.1.3 | Implement AI receipt processing for petty cash | 4 |

---

## PHASE 16: GST Compliance (1 week)

### EPIC 16.1: GST Returns

#### FEATURE 16.1.1: GSTR-1

##### STORY 16.1.1.1: Outward Supplies

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 16.1.1.1.1 | Create `gst_returns` table: return_type, period, status, filing_date, acknowledgement, json_file_path | 3 |
| 16.1.1.1.2 | Implement GSTR-1 data extraction: B2B, B2CL, B2CS, EXP, CDNR, CDNUR, HSN summary | 6 |
| 16.1.1.1.3 | Implement GSTR-1 JSON generation | 5 |
| 16.1.1.1.4 | Implement GET /api/v1/gst/gstr1/{month}/{year} | 4 |
| 16.1.1.1.5 | Implement POST /api/v1/gst/gstr1/{month}/{year}/generate | 4 |
| 16.1.1.1.6 | Implement GSTR-1 validation | 4 |

#### FEATURE 16.1.2: GSTR-3B

##### STORY 16.1.2.1: Summary Return

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 16.1.2.1.1 | Implement GSTR-3B data extraction | 5 |
| 16.1.2.1.2 | Implement ITC reconciliation | 4 |
| 16.1.2.1.3 | Implement GET /api/v1/gst/gstr3b/{month}/{year} | 4 |
| 16.1.2.1.4 | Implement GST payment challan preparation | 4 |

#### FEATURE 16.1.3: HSN/SAC Master

##### STORY 16.1.3.1: Code Management

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 16.1.3.1.1 | Create `hsn_sac_codes` table; seed IT services SAC codes | 4 |
| 16.1.3.1.2 | Implement GET /api/v1/hsn-sac search | 3 |
| 16.1.3.1.3 | Implement AI HSN/SAC suggestion with learning | 4 |

---

## PHASE 17: TDS Compliance - Vendor (0.5 weeks)

### EPIC 17.1: TDS on Payments

#### FEATURE 17.1.1: TDS Tracking

##### STORY 17.1.1.1: TDS Management

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 17.1.1.1.1 | Create `tds_payments` table: section, vendor_id, bill_id, payment_id, tds_amount, date, deposit_status, challan_id, certificate details | 3 |
| 17.1.1.1.2 | Implement TDS threshold tracking | 4 |
| 17.1.1.1.3 | Implement TDS challan deposit tracking | 3 |
| 17.1.1.1.4 | Implement TDS 26Q return data generation | 5 |
| 17.1.1.1.5 | Implement TDS certificate (Form 16A) generation | 4 |
| 17.1.1.1.6 | Implement GET /api/v1/reports/tds-payable | 3 |

---

## PHASE 18: Financial Reports (1 week)

### EPIC 18.1: Financial Statements

#### FEATURE 18.1.1: Trial Balance

##### STORY 18.1.1.1: Generate Trial Balance

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 18.1.1.1.1 | Implement trial balance service | 5 |
| 18.1.1.1.2 | Implement GET /api/v1/reports/trial-balance | 4 |
| 18.1.1.1.3 | Implement trial balance PDF export | 3 |

#### FEATURE 18.1.2: Profit & Loss

##### STORY 18.1.2.1: Generate P&L

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 18.1.2.1.1 | Implement P&L service | 5 |
| 18.1.2.1.2 | Implement GET /api/v1/reports/profit-loss with comparison | 4 |
| 18.1.2.1.3 | Implement P&L PDF export | 3 |
| 18.1.2.1.4 | Implement AI P&L insights | 5 |

#### FEATURE 18.1.3: Balance Sheet

##### STORY 18.1.3.1: Generate Balance Sheet

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 18.1.3.1.1 | Implement balance sheet service | 5 |
| 18.1.3.1.2 | Implement GET /api/v1/reports/balance-sheet | 4 |
| 18.1.3.1.3 | Implement PDF export | 3 |
| 18.1.3.1.4 | Implement AI insights | 4 |

#### FEATURE 18.1.4: Cash Flow

##### STORY 18.1.4.1: Generate Cash Flow

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 18.1.4.1.1 | Implement cash flow service (indirect method) | 6 |
| 18.1.4.1.2 | Implement GET /api/v1/reports/cash-flow | 4 |
| 18.1.4.1.3 | Implement AI cash flow insights | 4 |

### EPIC 18.2: Business Reports

#### FEATURE 18.2.1: Custom Reports

##### STORY 18.2.1.1: Business Intelligence

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 18.2.1.1.1 | Implement revenue analysis report | 4 |
| 18.2.1.1.2 | Implement expense analysis report | 4 |
| 18.2.1.1.3 | Implement customer profitability report | 4 |
| 18.2.1.1.4 | Implement forex analysis report | 3 |
| 18.2.1.1.5 | Implement tax summary report | 4 |

---

## PHASE 19: CRM Module (1 week)

### EPIC 19.1: Lead Management

#### FEATURE 19.1.1: Lead Tracking

##### STORY 19.1.1.1: Lead Pipeline

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 19.1.1.1.1 | Create `leads` table: lead_code, company_name, contact details, source ENUM, country, estimated_value, currency, stage ENUM, probability, expected_close_date, lost_reason, assigned_to, converted_customer_id, last_activity_at, next_followup_date, notes | 5 |
| 19.1.1.1.2 | Create `lead_activities` table: lead_id, activity_type ENUM, date, description, outcome, next_action | 3 |
| 19.1.1.1.3 | Implement lead code generation | 2 |
| 19.1.1.1.4 | Implement CRUD for leads | 4 |
| 19.1.1.1.5 | Implement POST /api/v1/leads/{id}/activities | 3 |
| 19.1.1.1.6 | Implement stage change tracking with probability adjustment | 3 |
| 19.1.1.1.7 | Implement lead conversion | 3 |

#### FEATURE 19.1.2: AI Lead Features

##### STORY 19.1.2.1: AI CRM

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 19.1.2.1.1 | Implement AI lead scoring | 5 |
| 19.1.2.1.2 | Implement AI follow-up suggestions | 4 |
| 19.1.2.1.3 | Implement AI email draft generation | 5 |
| 19.1.2.1.4 | Implement AI lead enrichment | 4 |

### EPIC 19.2: Pipeline

#### FEATURE 19.2.1: Pipeline Views

##### STORY 19.2.1.1: Pipeline Management

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 19.2.1.1.1 | Implement GET /api/v1/crm/pipeline | 4 |
| 19.2.1.1.2 | Implement GET /api/v1/crm/forecast | 4 |
| 19.2.1.1.3 | Implement GET /api/v1/crm/dashboard | 4 |
| 19.2.1.1.4 | Implement overdue followup alerts | 3 |

---

## PHASE 20: AI ERP Assistant (1 week)

### EPIC 20.1: Conversational Interface

#### FEATURE 20.1.1: Natural Language Queries

##### STORY 20.1.1.1: AI Query Engine

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 20.1.1.1.1 | Design AI query engine: classify intent, extract parameters, execute, format response | 6 |
| 20.1.1.1.2 | Implement query intent classification | 5 |
| 20.1.1.1.3 | Implement natural language to SQL (read-only, safe) | 6 |
| 20.1.1.1.4 | Implement POST /api/v1/ai/query | 4 |
| 20.1.1.1.5 | Implement sample queries and responses | 5 |

#### FEATURE 20.1.2: AI Actions

##### STORY 20.1.2.1: Action Execution

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 20.1.2.1.1 | Implement AI action framework with confirmation | 5 |
| 20.1.2.1.2 | Implement common AI actions | 4 |
| 20.1.2.1.3 | Implement AI error handling | 3 |

#### FEATURE 20.1.3: Proactive Insights

##### STORY 20.1.3.1: Smart Alerts

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 20.1.3.1.1 | Implement daily AI briefing | 6 |
| 20.1.3.1.2 | Implement anomaly detection | 5 |
| 20.1.3.1.3 | Implement cash flow projection | 5 |
| 20.1.3.1.4 | Implement compliance reminders | 4 |

---

# PART C: PROJECT MANAGEMENT

---

## PHASE 21: Project Management Core (1.5 weeks)

### EPIC 21.1: Project Master

#### FEATURE 21.1.1: Project Setup

##### STORY 21.1.1.1: Create Projects

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 21.1.1.1.1 | Enhance `projects` table: project_code, project_name, project_type ENUM ('client_service', 'internal_product'), customer_id, description, project_manager_id, dates, status, priority, billing_type ENUM, contract_value, currency, hourly_rate, budget_hours, logged_hours, billed_hours/amount, cost_amount, health_status ENUM, completion_percentage, folder_id (EDMS link) | 6 |
| 21.1.1.1.2 | Implement project code generation: PRJ-{CUST}-{YEAR}-{SEQ} or INT-{YEAR}-{SEQ} | 3 |
| 21.1.1.1.3 | Implement EDMS folder auto-creation for projects | 4 |
| 21.1.1.1.4 | Implement POST /api/v1/projects (enhanced) | 5 |
| 21.1.1.1.5 | Implement GET /api/v1/projects with enhanced filters | 4 |
| 21.1.1.1.6 | Implement GET /api/v1/projects/{id} with summaries | 4 |
| 21.1.1.1.7 | Implement PUT /api/v1/projects/{id} | 3 |
| 21.1.1.1.8 | Implement project cloning | 4 |

### EPIC 21.2: Milestones

#### FEATURE 21.2.1: Milestone Management

##### STORY 21.2.1.1: Implement Milestones

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 21.2.1.1.1 | Create `milestones` table: project_id, name, description, sequence, dates (planned/actual), status ENUM, completion_percentage, deliverables, billing_percentage/amount, is_billable, invoice_id | 4 |
| 21.2.1.1.2 | Implement milestone CRUD | 4 |
| 21.2.1.1.3 | Implement milestone status auto-update | 3 |
| 21.2.1.1.4 | Implement milestone billing trigger | 4 |
| 21.2.1.1.5 | Implement milestone templates | 3 |

### EPIC 21.3: Task Management

#### FEATURE 21.3.1: Tasks

##### STORY 21.3.1.1: Implement Tasks

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 21.3.1.1.1 | Create `tasks` table: project_id, milestone_id, task_code, task_name, description, task_type ENUM, assigned_to/by, priority ENUM, status ENUM, dates, estimated/logged_hours, is_billable, parent_task_id, tags | 5 |
| 21.3.1.1.2 | Implement task code generation | 2 |
| 21.3.1.1.3 | Implement task CRUD | 5 |
| 21.3.1.1.4 | Implement task assignment | 3 |
| 21.3.1.1.5 | Implement task status transitions | 4 |
| 21.3.1.1.6 | Implement bulk task operations | 3 |
| 21.3.1.1.7 | Implement subtasks | 3 |
| 21.3.1.1.8 | Implement task dependencies | 4 |

#### FEATURE 21.3.2: Timesheet Integration

##### STORY 21.3.2.1: Link Tasks to Timesheet

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 21.3.2.1.1 | Enhance timesheet_entries with task_id | 2 |
| 21.3.2.1.2 | Implement task-level time logging | 3 |
| 21.3.2.1.3 | Implement hours rollup (task → milestone → project) | 3 |
| 21.3.2.1.4 | Implement GET /api/v1/tasks/{id}/time-entries | 2 |
| 21.3.2.1.5 | Implement project hours summary | 4 |

### EPIC 21.4: Project Team

#### FEATURE 21.4.1: Team Management

##### STORY 21.4.1.1: Manage Members

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 21.4.1.1.1 | Enhance project_members: role_in_project, hourly_cost_rate, hourly_bill_rate, dates, is_active | 3 |
| 21.4.1.1.2 | Implement project team CRUD | 4 |
| 21.4.1.1.3 | Implement project access control | 3 |
| 21.4.1.1.4 | Implement team member cost tracking | 4 |

---

## PHASE 22: Resource Management (1 week)

### EPIC 22.1: Resource Allocation

#### FEATURE 22.1.1: Allocation Planning

##### STORY 22.1.1.1: Implement Allocation

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 22.1.1.1.1 | Create `resource_allocations` table: employee_id, project_id, dates, allocation_percentage, planned_hours_per_week, role, is_active, notes | 4 |
| 22.1.1.1.2 | Implement allocation validation (≤100% total) | 4 |
| 22.1.1.1.3 | Implement POST /api/v1/resource-allocations | 3 |
| 22.1.1.1.4 | Implement GET /api/v1/resource-allocations | 3 |
| 22.1.1.1.5 | Implement GET /api/v1/employees/{id}/allocations | 3 |
| 22.1.1.1.6 | Implement GET /api/v1/projects/{id}/allocations | 3 |
| 22.1.1.1.7 | Implement allocation conflict detection | 3 |

### EPIC 22.2: Utilization

#### FEATURE 22.2.1: Utilization Metrics

##### STORY 22.2.1.1: Track Utilization

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 22.2.1.1.1 | Define utilization calculation | 2 |
| 22.2.1.1.2 | Implement GET /api/v1/reports/utilization | 5 |
| 22.2.1.1.3 | Implement employee utilization dashboard | 4 |
| 22.2.1.1.4 | Implement utilization targets | 3 |
| 22.2.1.1.5 | Implement bench report | 3 |

### EPIC 22.3: Capacity Planning

#### FEATURE 22.3.1: Capacity Forecasting

##### STORY 22.3.1.1: Plan Capacity

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 22.3.1.1.1 | Implement capacity calculation | 4 |
| 22.3.1.1.2 | Implement GET /api/v1/reports/capacity | 5 |
| 22.3.1.1.3 | Implement project staffing needs | 4 |
| 22.3.1.1.4 | Implement capacity vs demand chart | 4 |
| 22.3.1.1.5 | Implement resource suggestion | 4 |

---

## PHASE 23: Project Billing Integration (1 week)

### EPIC 23.1: T&M Billing

#### FEATURE 23.1.1: T&M Invoice Generation

##### STORY 23.1.1.1: Bill from Timesheet

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 23.1.1.1.1 | Create `billing_rates` table: project_id, rate_type ENUM, employee_id, task_type, hourly_rate, currency, effective_dates | 4 |
| 23.1.1.1.2 | Implement billing rate resolution | 3 |
| 23.1.1.1.3 | Implement GET /api/v1/projects/{id}/unbilled-hours | 4 |
| 23.1.1.1.4 | Implement POST /api/v1/projects/{id}/generate-tm-invoice | 6 |
| 23.1.1.1.5 | Enhance timesheet_entries with invoice_line_item_id | 2 |
| 23.1.1.1.6 | Implement unbilled hours alert | 3 |

### EPIC 23.2: Fixed Price Billing

#### FEATURE 23.2.1: Milestone Billing

##### STORY 23.2.1.1: Bill on Completion

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 23.2.1.1.1 | Implement milestone billing validation (100% total) | 2 |
| 23.2.1.1.2 | Implement GET /api/v1/projects/{id}/billable-milestones | 3 |
| 23.2.1.1.3 | Implement POST /api/v1/milestones/{id}/generate-invoice | 4 |
| 23.2.1.1.4 | Implement partial milestone billing | 3 |
| 23.2.1.1.5 | Implement project billing summary | 4 |

### EPIC 23.3: Profitability

#### FEATURE 23.3.1: Profitability Analysis

##### STORY 23.3.1.1: Calculate Profit

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 23.3.1.1.1 | Implement project cost calculation | 4 |
| 23.3.1.1.2 | Implement project revenue calculation | 3 |
| 23.3.1.1.3 | Implement GET /api/v1/projects/{id}/profitability | 4 |
| 23.3.1.1.4 | Implement GET /api/v1/reports/project-profitability | 5 |
| 23.3.1.1.5 | Implement customer profitability | 4 |
| 23.3.1.1.6 | Implement profitability alerts | 3 |

---

# PART D: FRONTEND

---

## PHASE 24: Frontend - Authentication & Core (1 week)

### EPIC 24.1: Authentication UI

#### FEATURE 24.1.1: Login Flow

##### STORY 24.1.1.1: Build Auth Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 24.1.1.1.1 | Create login page with validation | 4 |
| 24.1.1.1.2 | Implement auth context and provider | 5 |
| 24.1.1.1.3 | Create protected route wrapper with role-based access | 4 |
| 24.1.1.1.4 | Build change password page | 3 |
| 24.1.1.1.5 | Build forgot/reset password flow | 4 |

### EPIC 24.2: Dashboard

#### FEATURE 24.2.1: Role-Based Dashboards

##### STORY 24.2.1.1: Build Dashboards

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 24.2.1.1.1 | Create main layout with sidebar, header, user menu | 5 |
| 24.2.1.1.2 | Build employee dashboard | 5 |
| 24.2.1.1.3 | Build HR dashboard | 5 |
| 24.2.1.1.4 | Build admin dashboard | 4 |

---

## PHASE 25: Frontend - EDMS & Employees (1 week)

### EPIC 25.1: Document Management UI

#### FEATURE 25.1.1: EDMS Interface

##### STORY 25.1.1.1: Build EDMS

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 25.1.1.1.1 | Create folder tree component | 6 |
| 25.1.1.1.2 | Build document list view | 5 |
| 25.1.1.1.3 | Build document upload modal | 5 |
| 25.1.1.1.4 | Build folder permission modal | 4 |
| 25.1.1.1.5 | Build document search interface | 4 |
| 25.1.1.1.6 | Build folder download functionality | 3 |
| 25.1.1.1.7 | Build document preview modal | 5 |

### EPIC 25.2: Employee Management UI

#### FEATURE 25.2.1: Employee Directory

##### STORY 25.2.1.1: Employee Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 25.2.1.1.1 | Build employee directory page | 5 |
| 25.2.1.1.2 | Build employee profile page with tabs | 5 |
| 25.2.1.1.3 | Build personal info tab | 4 |
| 25.2.1.1.4 | Build employment tab | 5 |
| 25.2.1.1.5 | Build documents tab | 4 |
| 25.2.1.1.6 | Build add employee form | 5 |

#### FEATURE 25.2.2: Onboarding UI

##### STORY 25.2.2.1: Onboarding Wizard

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 25.2.2.1.1 | Build onboarding wizard | 6 |
| 25.2.2.1.2 | Build personal info step | 3 |
| 25.2.2.1.3 | Build contact step | 4 |
| 25.2.2.1.4 | Build identity step | 4 |
| 25.2.2.1.5 | Build bank step | 3 |
| 25.2.2.1.6 | Build education step | 4 |
| 25.2.2.1.7 | Build previous employment step | 4 |
| 25.2.2.1.8 | Build documents step | 4 |
| 25.2.2.1.9 | Build declarations step | 3 |

---

## PHASE 26: Frontend - Leave & Timesheet (1 week)

### EPIC 26.1: Leave UI

#### FEATURE 26.1.1: Leave Interface

##### STORY 26.1.1.1: Leave Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 26.1.1.1.1 | Build leave balance card | 4 |
| 26.1.1.1.2 | Build apply leave page | 5 |
| 26.1.1.1.3 | Build my leave requests page | 4 |
| 26.1.1.1.4 | Build leave request detail view | 3 |
| 26.1.1.1.5 | Build leave approvals page | 5 |
| 26.1.1.1.6 | Build team leave calendar | 5 |
| 26.1.1.1.7 | Build holiday calendar page | 3 |

### EPIC 26.2: Timesheet UI

#### FEATURE 26.2.1: Timesheet Interface

##### STORY 26.2.1.1: Timesheet Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 26.2.1.1.1 | Build weekly timesheet page | 6 |
| 26.2.1.1.2 | Build timesheet entry cell | 4 |
| 26.2.1.1.3 | Build timesheet actions | 3 |
| 26.2.1.1.4 | Build timesheet history page | 3 |
| 26.2.1.1.5 | Build timesheet approvals page | 4 |

---

## PHASE 27: Frontend - Payroll (1 week)

### EPIC 27.1: Payroll UI

#### FEATURE 27.1.1: Payroll Processing

##### STORY 27.1.1.1: Payroll Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 27.1.1.1.1 | Build payroll dashboard | 4 |
| 27.1.1.1.2 | Build run payroll page | 5 |
| 27.1.1.1.3 | Build payroll run detail page | 5 |
| 27.1.1.1.4 | Build salary management page | 5 |
| 27.1.1.1.5 | Build salary structure form | 4 |

#### FEATURE 27.1.2: Employee Payslip UI

##### STORY 27.1.2.1: Payslip Pages

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 27.1.2.1.1 | Build my payslips page | 3 |
| 27.1.2.1.2 | Build payslip detail view | 4 |
| 27.1.2.1.3 | Build tax declaration page | 5 |
| 27.1.2.1.4 | Build Form 16 page | 3 |

### EPIC 27.2: Settings UI

#### FEATURE 27.2.1: Settings Pages

##### STORY 27.2.1.1: Settings Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 27.2.1.1.1 | Build user settings page | 4 |
| 27.2.1.1.2 | Build admin settings | 6 |
| 27.2.1.1.3 | Build user management page | 4 |
| 27.2.1.1.4 | Build audit log viewer | 4 |

---

## PHASE 28: Frontend - Accounting (2 weeks)

### EPIC 28.1: Core Accounting UI

#### FEATURE 28.1.1: Accounting Dashboard

##### STORY 28.1.1.1: Accounting Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.1.1.1.1 | Build accounting dashboard | 5 |
| 28.1.1.1.2 | Update navigation for accounting | 3 |
| 28.1.1.1.3 | Build AI assistant chat widget | 6 |

#### FEATURE 28.1.2: Customer & Vendor UI

##### STORY 28.1.2.1: Party Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.1.2.1.1 | Build customer list page | 4 |
| 28.1.2.1.2 | Build customer detail page | 4 |
| 28.1.2.1.3 | Build customer form | 3 |
| 28.1.2.1.4 | Build vendor list and detail pages | 4 |
| 28.1.2.1.5 | Build vendor form | 3 |

#### FEATURE 28.1.3: Invoice UI

##### STORY 28.1.3.1: Invoice Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.1.3.1.1 | Build invoice list page | 5 |
| 28.1.3.1.2 | Build invoice create/edit page | 6 |
| 28.1.3.1.3 | Build invoice detail/preview page | 4 |
| 28.1.3.1.4 | Build AI invoice generator modal | 4 |
| 28.1.3.1.5 | Build credit note creation | 3 |

#### FEATURE 28.1.4: Bill UI

##### STORY 28.1.4.1: Bill Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.1.4.1.1 | Build bill list page | 4 |
| 28.1.4.1.2 | Build bill create with AI extraction | 6 |
| 28.1.4.1.3 | Build bill detail page | 4 |
| 28.1.4.1.4 | Build payment creation from bill | 4 |

### EPIC 28.2: Banking UI

#### FEATURE 28.2.1: Bank Reconciliation

##### STORY 28.2.1.1: Reconciliation Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.2.1.1.1 | Build bank accounts page | 3 |
| 28.2.1.1.2 | Build statement upload page | 5 |
| 28.2.1.1.3 | Build reconciliation interface | 8 |
| 28.2.1.1.4 | Build reconciliation summary | 3 |

### EPIC 28.3: Reports UI

#### FEATURE 28.3.1: Financial Reports

##### STORY 28.3.1.1: Report Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.3.1.1.1 | Build reports dashboard | 4 |
| 28.3.1.1.2 | Build trial balance page | 4 |
| 28.3.1.1.3 | Build P&L page | 5 |
| 28.3.1.1.4 | Build balance sheet page | 4 |
| 28.3.1.1.5 | Build cash flow page | 4 |
| 28.3.1.1.6 | Build AR/AP aging reports | 4 |

#### FEATURE 28.3.2: GST & TDS Reports

##### STORY 28.3.2.1: Compliance Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.3.2.1.1 | Build GSTR-1 page | 5 |
| 28.3.2.1.2 | Build GSTR-3B page | 4 |
| 28.3.2.1.3 | Build TDS compliance page | 4 |

### EPIC 28.4: CRM UI

#### FEATURE 28.4.1: CRM Screens

##### STORY 28.4.1.1: Lead UI

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 28.4.1.1.1 | Build lead list page (Kanban + list) | 6 |
| 28.4.1.1.2 | Build lead detail page | 5 |
| 28.4.1.1.3 | Build lead form | 3 |
| 28.4.1.1.4 | Build activity logging modal | 3 |
| 28.4.1.1.5 | Build AI email composer | 4 |
| 28.4.1.1.6 | Build pipeline dashboard | 5 |

---

## PHASE 29: Frontend - Project Management (1 week)

### EPIC 29.1: Project UI

#### FEATURE 29.1.1: Project Screens

##### STORY 29.1.1.1: Project Interface

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 29.1.1.1.1 | Build project list page | 5 |
| 29.1.1.1.2 | Build project detail page with tabs | 6 |
| 29.1.1.1.3 | Build project overview tab | 4 |
| 29.1.1.1.4 | Build milestones tab | 4 |
| 29.1.1.1.5 | Build tasks tab | 5 |
| 29.1.1.1.6 | Build task detail modal | 4 |
| 29.1.1.1.7 | Build project team tab | 4 |
| 29.1.1.1.8 | Build project time tab | 4 |
| 29.1.1.1.9 | Build project billing tab | 5 |
| 29.1.1.1.10 | Build project create/edit form | 5 |

#### FEATURE 29.1.2: My Work

##### STORY 29.1.2.1: Personal Tasks

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 29.1.2.1.1 | Build my tasks page | 4 |
| 29.1.2.1.2 | Build my work dashboard widget | 3 |
| 29.1.2.1.3 | Enhance timesheet with task selector | 3 |

### EPIC 29.2: Resource UI

#### FEATURE 29.2.1: Resource Planning

##### STORY 29.2.1.1: Resource Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 29.2.1.1.1 | Build resource allocation (Gantt-style) page | 8 |
| 29.2.1.1.2 | Build allocation modal | 3 |
| 29.2.1.1.3 | Build utilization report page | 5 |
| 29.2.1.1.4 | Build capacity planning page | 5 |
| 29.2.1.1.5 | Build bench report page | 4 |

### EPIC 29.3: Project Reports

#### FEATURE 29.3.1: Project Reports

##### STORY 29.3.1.1: Report Screens

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 29.3.1.1.1 | Build project profitability report | 4 |
| 29.3.1.1.2 | Build customer profitability report | 4 |
| 29.3.1.1.3 | Build project health dashboard | 4 |
| 29.3.1.1.4 | Add project reports to navigation | 2 |

---

## PHASE 30: Testing & Deployment (1 week)

### EPIC 30.1: Testing

#### FEATURE 30.1.1: Backend Testing

##### STORY 30.1.1.1: Write Tests

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 30.1.1.1.1 | Setup pytest with fixtures for all roles | 4 |
| 30.1.1.1.2 | Write payroll calculation tests | 6 |
| 30.1.1.1.3 | Write auth tests | 4 |
| 30.1.1.1.4 | Write leave management tests | 4 |
| 30.1.1.1.5 | Write payroll integration tests | 4 |
| 30.1.1.1.6 | Write statutory compliance tests | 4 |
| 30.1.1.1.7 | Write accounting workflow tests | 6 |
| 30.1.1.1.8 | Write project billing tests | 4 |

#### FEATURE 30.1.2: Frontend Testing

##### STORY 30.1.2.1: Component Tests

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 30.1.2.1.1 | Setup Vitest with React Testing Library | 3 |
| 30.1.2.1.2 | Write critical component tests | 4 |
| 30.1.2.1.3 | Setup Playwright for E2E tests | 5 |

### EPIC 30.2: Deployment

#### FEATURE 30.2.1: Production Deployment

##### STORY 30.2.1.1: Deploy to VPS

| Task ID | Task Description | Est. Hours |
|---------|------------------|------------|
| 30.2.1.1.1 | Create production docker-compose.yml | 4 |
| 30.2.1.1.2 | Setup CI/CD with GitHub Actions | 6 |
| 30.2.1.1.3 | Configure production nginx | 3 |
| 30.2.1.1.4 | Create database initialization script | 4 |
| 30.2.1.1.5 | Setup production monitoring | 3 |
| 30.2.1.1.6 | Create admin documentation | 4 |

---

## Summary Statistics

| Phase | Focus | Tasks | Hours |
|-------|-------|-------|-------|
| 1 | Discovery & Planning | 8 | 46 |
| 2 | Infrastructure | 12 | 43 |
| 3 | Backend Core | 40 | 156 |
| 4 | EDMS | 22 | 93 |
| 5 | Onboarding | 11 | 40 |
| 6 | Leave Management | 22 | 88 |
| 7 | Timesheet | 15 | 57 |
| 8 | Payroll | 33 | 158 |
| 9 | Company & Statutory | 52 | 185 |
| 10 | AI Infrastructure | 13 | 57 |
| 11 | Chart of Accounts & GL | 21 | 79 |
| 12 | Multi-Currency | 7 | 27 |
| 13 | Customer Invoicing (AR) | 37 | 147 |
| 14 | Vendor Bills (AP) | 24 | 98 |
| 15 | Bank & Cash | 20 | 80 |
| 16 | GST Compliance | 16 | 64 |
| 17 | TDS Compliance | 6 | 22 |
| 18 | Financial Reports | 19 | 72 |
| 19 | CRM | 17 | 68 |
| 20 | AI ERP Assistant | 16 | 62 |
| 21 | Project Management Core | 36 | 140 |
| 22 | Resource Management | 20 | 80 |
| 23 | Project Billing | 18 | 72 |
| 24 | Frontend - Auth & Core | 9 | 39 |
| 25 | Frontend - EDMS & Employees | 28 | 109 |
| 26 | Frontend - Leave & Timesheet | 13 | 54 |
| 27 | Frontend - Payroll & Settings | 16 | 65 |
| 28 | Frontend - Accounting | 46 | 176 |
| 29 | Frontend - Projects | 25 | 100 |
| 30 | Testing & Deployment | 17 | 68 |
| **TOTAL** | | **639** | **2,548** |

---

## Timeline Estimate

| Phase Group | Phases | Weeks |
|-------------|--------|-------|
| Part A: HRMS & Documents | 1-9 | 12 |
| Part B: Accounting & AI | 10-20 | 10 |
| Part C: Project Management | 21-23 | 4 |
| Part D: Frontend | 24-29 | 8 |
| Testing & Deployment | 30 | 1 |
| Buffer (15%) | - | 5 |
| **TOTAL** | | **~40 weeks** |

**With 1 developer (40 hrs/week):** ~12-14 months  
**With 2 developers:** ~6-8 months

---

*End of Comprehensive WBS Document*
