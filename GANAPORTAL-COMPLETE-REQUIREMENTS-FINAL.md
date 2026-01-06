# GANAPORTAL - COMPLETE REQUIREMENTS SPECIFICATION
## AI-First ERP for Ganakys Codilla Apps (OPC) Private Limited

**Version:** 4.0 FINAL  
**Date:** January 2026  
**Status:** APPROVED FOR AUTONOMOUS BUILD  

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 1: PROJECT OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════

## 1.1 Project Identity

| Attribute | Value |
|-----------|-------|
| **Project Name** | GanaPortal |
| **Type** | AI-First ERP System |
| **Client** | Ganakys Codilla Apps (OPC) Private Limited |
| **CIN** | U72900KA2024OPC188083 |
| **Domain** | IT Services & SaaS Company |
| **Location** | Karnataka, India |
| **Target URL** | portal.ganakys.com |
| **Current Scale** | 5 employees (2026) |
| **Target Scale** | 15 employees (2027), 50 employees (2030) |

## 1.2 Vision Statement

GanaPortal is an **AI-First ERP** where artificial intelligence powers EVERY module. The AI extracts data from documents, categorizes transactions, predicts outcomes, suggests actions, and automates workflows - reducing manual work by 95% while maintaining CA oversight for compliance.

## 1.3 Build Statistics

| Metric | Count |
|--------|-------|
| **Modules** | 23 |
| **Database Tables** | 127 |
| **API Endpoints** | 267 |
| **Frontend Screens** | 68 |
| **User Roles** | 5 |
| **Compliance Rules** | 47 |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 2: TECHNOLOGY STACK (LOCKED - DO NOT CHANGE)
# ═══════════════════════════════════════════════════════════════════════════════

## 2.1 Frontend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | Next.js | 14.1.x | App Router, SSR |
| Language | TypeScript | 5.3.x | Type safety |
| Styling | Tailwind CSS | 3.4.x | Utility-first CSS |
| Components | shadcn/ui | Latest | Pre-built UI components |
| State | TanStack Query | 5.17.x | Server state management |
| Tables | TanStack Table | 8.11.x | Complex data grids |
| Forms | React Hook Form | 7.49.x | Form handling |
| Validation | Zod | 3.22.x | Schema validation |
| Charts | Recharts | 2.10.x | Data visualization |
| Icons | Lucide React | 0.303.x | Icon library |
| Date | date-fns | 3.2.x | Date manipulation |
| PDF | react-pdf | 7.x | PDF rendering |

## 2.2 Backend Stack

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Framework | FastAPI | 0.109.x | REST API |
| Language | Python | 3.11+ | Backend language |
| ORM | SQLAlchemy | 2.0.x | Database ORM (async) |
| Validation | Pydantic | 2.5.x | Data validation |
| Migrations | Alembic | 1.13.x | Schema migrations |
| Auth | PyJWT | 2.8.x | JWT tokens |
| Password | bcrypt | 4.1.x | Password hashing |
| Task Queue | Celery | 5.3.x | Background jobs |
| PDF Gen | WeasyPrint | 60.x | PDF generation |
| Excel | openpyxl | 3.1.x | Excel export |

## 2.3 Database & Cache

| Component | Technology | Version | Purpose |
|-----------|------------|---------|---------|
| Primary DB | PostgreSQL | 16 | Main data store |
| Cache | Redis | 7 | Sessions, cache, queues |
| Search | PostgreSQL FTS | - | Full-text search |
| File Storage | Local FS | - | /var/data/ganaportal/ |

## 2.4 AI Stack (Fallback Chain)

```
Priority Order:
1. Claude API (claude-3-5-sonnet-20241022) - PRIMARY
2. Gemini API (gemini-1.5-pro) - FALLBACK 1
3. OpenAI API (gpt-4-turbo) - FALLBACK 2
4. Together AI (Qwen/Qwen3-Coder-480B) - FALLBACK 3

If provider fails → automatic retry with next provider
All 4 fail → queue for manual processing
```

## 2.5 Infrastructure

| Component | Technology | Configuration |
|-----------|------------|---------------|
| Server | Hostinger VPS | 4GB RAM, 2 vCPU, Ubuntu 22.04 |
| Web Server | Nginx | Reverse proxy, SSL termination |
| SSL | Let's Encrypt | Auto-renewal via certbot |
| Containers | Docker + Compose | Production deployment |
| CI/CD | GitHub Actions | Auto-deploy on main push |
| Backup | pg_dump + rsync | Daily at 2 AM IST, 30-day retention |
| Monitoring | Prometheus + Grafana | Basic metrics |

## 2.6 External Integrations

| Service | Provider | Purpose | API |
|---------|----------|---------|-----|
| Email | AWS SES | Transactional emails | SMTP/API |
| SMS | MSG91 | DLT compliant OTP/alerts | REST API |
| Exchange Rates | RBI | Daily forex rates | REST API |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 3: USER ROLES & PERMISSIONS
# ═══════════════════════════════════════════════════════════════════════════════

## 3.1 Role Definitions

### Role: ADMIN (admin)
**Description:** Company owner/founder with full system access
**Permissions:**
- Full access to all modules
- User management
- System configuration
- View all data across company
- Approve high-value transactions
- Access audit logs

### Role: HR_MANAGER (hr)
**Description:** Human Resources manager
**Permissions:**
- Employee management (CRUD)
- Onboarding management
- Leave approval
- Timesheet approval
- Payroll processing
- Document management
- View employee reports

### Role: ACCOUNTANT (accountant)
**Description:** Finance/Accounts team member
**Permissions:**
- Chart of accounts management
- Journal entries
- Customer/Vendor management
- Invoice/Bill creation
- Payment processing
- Bank reconciliation
- GST/TDS filing preparation
- Financial reports

### Role: EMPLOYEE (employee)
**Description:** Regular employee (self-service)
**Permissions:**
- View own profile
- Update contact info
- Submit leave requests
- Submit timesheets
- View own payslips
- View own tax declarations
- Upload documents to own folder

### Role: EXTERNAL_CA (external_ca)
**Description:** External Chartered Accountant for verification
**Permissions:**
- View all financial data (read-only)
- View all compliance data
- Verify and approve transactions
- Add corrections/comments
- Generate compliance reports
- Access audit trail

## 3.2 Permission Matrix

| Module | admin | hr | accountant | employee | external_ca |
|--------|-------|-----|------------|----------|-------------|
| Dashboard | Full | HR View | Finance View | Self View | Audit View |
| Employees | CRUD | CRUD | Read | Self Only | Read |
| Documents | Full | Full | Own Dept | Own Only | Read |
| Onboarding | Full | Full | - | Self Only | - |
| Leave | Full | Approve | - | Self+Team | - |
| Timesheet | Full | Approve | - | Self | - |
| Payroll | Full | Run | View | Self Only | Verify |
| Statutory | Full | View | Prepare | - | Verify |
| Accounting | Full | - | Full | - | Verify |
| AR/Invoicing | Full | - | Full | - | Read |
| AP/Bills | Full | - | Full | - | Read |
| Banking | Full | - | Full | - | Verify |
| GST | Full | - | Full | - | Verify |
| TDS | Full | - | Full | - | Verify |
| Reports | Full | HR Reports | All Reports | - | All Reports |
| CRM | Full | - | Read | - | - |
| Projects | Full | Read | Billing | Assigned | - |
| AI Assistant | Full | Full | Full | Limited | Read |
| Settings | Full | - | - | - | - |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 4: AI-FIRST ARCHITECTURE
# ═══════════════════════════════════════════════════════════════════════════════

## 4.1 AI Confidence Thresholds

| Confidence | Range | Action | Human Involvement |
|------------|-------|--------|-------------------|
| HIGH | ≥95% | Auto-execute | None - fully automated |
| MEDIUM | 70-94% | Queue for review | Quick approve/reject (1-click) |
| LOW | <70% | Flag for manual | Full human input required |

## 4.2 AI Components

### 4.2.1 Document Processor
**Purpose:** Extract structured data from images and PDFs
**Capabilities:**
- OCR for scanned documents
- ID card extraction (Aadhaar, PAN, Passport)
- Invoice/Bill extraction (vendor, amount, GST, line items)
- Bank statement parsing
- Resume/certificate extraction

**Input:** Image (PNG, JPG), PDF
**Output:** JSON with extracted fields + confidence scores

### 4.2.2 Transaction Categorizer
**Purpose:** Automatically categorize financial transactions
**Capabilities:**
- Match vendor from description
- Suggest expense category
- Suggest GL account
- Identify recurring patterns
- Learn from corrections

**Input:** Transaction description, amount, type
**Output:** Category, GL account, vendor match, confidence

### 4.2.3 Natural Language Query Engine
**Purpose:** Convert plain English to SQL/actions
**Capabilities:**
- Answer data questions ("What's my leave balance?")
- Execute actions ("Create invoice for Client X")
- Generate reports ("Show P&L for last quarter")
- Explain data ("Why is revenue down?")

**Input:** Natural language query
**Output:** SQL query or action + result

### 4.2.4 Anomaly Detector
**Purpose:** Flag unusual transactions or patterns
**Capabilities:**
- Unusual amounts (>2 std dev)
- Timing anomalies (weekend transactions)
- Duplicate detection
- Compliance violations
- Budget overruns

**Input:** Transaction or pattern
**Output:** Alert with explanation + severity

### 4.2.5 Prediction Engine
**Purpose:** Forecast and predict outcomes
**Capabilities:**
- Cash flow forecasting
- Payment date prediction
- Lead scoring
- Project delay prediction
- Resource demand forecasting

**Input:** Historical data + current state
**Output:** Prediction + confidence interval

## 4.3 AI Features by Module

| Module | AI Features |
|--------|-------------|
| **HRMS** | Extract from ID cards, auto-fill forms, validate documents |
| **EDMS** | Auto-categorize, smart tagging, document summarization, semantic search |
| **Onboarding** | Guide through steps, validate completeness, suggest missing items |
| **Leave** | Suggest optimal dates, predict team conflicts, auto-approve routine requests |
| **Timesheet** | Auto-fill from calendar, suggest allocations, flag anomalies |
| **Payroll** | Validate calculations, flag outliers, explain variances |
| **Accounting** | 95% auto-categorization, smart reconciliation, journal suggestions |
| **AR** | Generate invoice from NL, suggest HSN/SAC, predict payment dates |
| **AP** | Extract from bill images, match to PO, suggest TDS section |
| **Banking** | Auto-reconcile (95%+ match rate), categorize, detect fraud |
| **GST** | Auto-prepare returns, validate ITC, suggest corrections |
| **TDS** | Auto-calculate, track thresholds, prepare certificates |
| **CRM** | Score leads, draft emails, suggest follow-ups, predict conversion |
| **Projects** | Estimate effort, predict delays, optimize resources, track health |
| **Reports** | Generate insights, answer queries, explain variances |
| **Quotes** | Generate from brief, suggest pricing, predict acceptance |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 5: COMPLETE MODULE SPECIFICATIONS
# ═══════════════════════════════════════════════════════════════════════════════

## MODULE 1: Infrastructure & DevOps

### 1.1 Docker Configuration
```yaml
Services:
  - backend (FastAPI)
  - frontend (Next.js)
  - db (PostgreSQL 16)
  - redis (Redis 7)
  - nginx (reverse proxy)
  - celery-worker (background tasks)
  - celery-beat (scheduled tasks)
```

### 1.2 Environment Variables
```
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/ganaportal
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=<256-bit-random>
JWT_ACCESS_EXPIRE_MINUTES=15
JWT_REFRESH_EXPIRE_DAYS=7

# AI APIs
ANTHROPIC_API_KEY=sk-ant-xxx
GOOGLE_API_KEY=xxx
OPENAI_API_KEY=sk-xxx
TOGETHER_API_KEY=xxx

# External Services
AWS_SES_ACCESS_KEY=xxx
AWS_SES_SECRET_KEY=xxx
MSG91_AUTH_KEY=xxx
MSG91_SENDER_ID=GANAKY
```

### 1.3 Nginx Configuration
- SSL termination (Let's Encrypt)
- Reverse proxy to backend (:8000) and frontend (:3000)
- Gzip compression
- Security headers (HSTS, CSP, X-Frame-Options)
- Rate limiting (100 req/min per IP)

### 1.4 Backup System
- Database: pg_dump daily at 2 AM IST
- Files: rsync to backup location
- Retention: 30 days
- Tested restore procedure

---

## MODULE 2: Authentication & Users

### 2.1 Authentication Flow
```
1. POST /api/v1/auth/login
   - Validate email + password
   - Check account active
   - Generate access_token (15 min) + refresh_token (7 days)
   - Log login event

2. All protected endpoints:
   - Require Bearer token in Authorization header
   - Validate token signature + expiry
   - Extract user_id and role

3. POST /api/v1/auth/refresh
   - Validate refresh_token
   - Issue new access_token
   - Optionally rotate refresh_token

4. POST /api/v1/auth/logout
   - Blacklist current tokens
   - Clear client storage
```

### 2.2 Password Requirements
- Minimum 8 characters
- At least 1 uppercase, 1 lowercase, 1 digit, 1 special
- bcrypt with 12 rounds
- Password history (last 5, no reuse)
- Rate limit: 5 attempts per 15 minutes

### 2.3 Session Management
- Store refresh tokens in Redis
- Track active sessions per user
- Allow "logout all devices"
- Session timeout: 30 minutes inactivity

### 2.4 Audit Logging
Log all:
- Login/logout events
- Password changes
- Role changes
- Permission changes
- Failed login attempts
- Data access for sensitive records

### 2.5 Database Tables
```sql
-- users
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role user_role NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP,
    password_changed_at TIMESTAMP,
    failed_login_attempts INT DEFAULT 0,
    locked_until TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- user_sessions
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    refresh_token_hash VARCHAR(255),
    device_info JSONB,
    ip_address INET,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- audit_logs
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    action VARCHAR(100),
    entity_type VARCHAR(50),
    entity_id UUID,
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 2.6 API Endpoints
| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /auth/login | User login | No |
| POST | /auth/refresh | Refresh tokens | No |
| POST | /auth/logout | Logout | Yes |
| GET | /auth/me | Current user info | Yes |
| POST | /auth/change-password | Change password | Yes |
| POST | /auth/forgot-password | Request reset | No |
| POST | /auth/reset-password | Reset with token | No |
| GET | /users | List users | Admin |
| POST | /users | Create user | Admin |
| GET | /users/{id} | Get user | Admin |
| PUT | /users/{id} | Update user | Admin |
| DELETE | /users/{id} | Deactivate user | Admin |
| POST | /users/{id}/activate | Activate user | Admin |

---

## MODULE 3: Employee Management (HRMS)

### 3.1 Employee Master Data

#### Personal Information
- Employee Code: GCA-YYYY-XXXX (auto-generated)
- First Name, Middle Name, Last Name
- Date of Birth, Gender
- Blood Group
- Marital Status
- Profile Photo

#### Contact Information
- Personal Email, Work Email
- Personal Phone, Emergency Contact
- Current Address (with PIN code)
- Permanent Address

#### Identity Documents
- Aadhaar Number (masked display: XXXX-XXXX-1234)
- PAN Number
- Passport Number + Expiry
- Driving License + Expiry
- Voter ID

#### Bank Details
- Bank Name, Branch
- Account Number (masked)
- IFSC Code
- Account Holder Name

#### Employment Details
- Department, Designation
- Date of Joining
- Employment Type (Full-time, Part-time, Contract)
- Reporting Manager
- Work Location
- Probation Period + Confirmation Date
- Notice Period

### 3.2 Employee Code Generation
```python
def generate_employee_code():
    year = datetime.now().year
    last = get_last_employee_code(year)
    if last:
        seq = int(last.split('-')[2]) + 1
    else:
        seq = 1
    return f"GCA-{year}-{seq:04d}"
```

### 3.3 AI Features
- **ID Card Extraction:** Upload Aadhaar/PAN image → Extract name, number, DOB
- **Resume Parsing:** Upload resume → Extract education, experience
- **Document Validation:** Check if uploaded documents are valid/readable

### 3.4 Database Tables
```sql
-- employees
CREATE TABLE employees (
    id UUID PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE NOT NULL,
    user_id UUID REFERENCES users(id),
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    gender VARCHAR(20),
    blood_group VARCHAR(10),
    marital_status VARCHAR(20),
    profile_photo_url TEXT,
    department_id UUID REFERENCES departments(id),
    designation_id UUID REFERENCES designations(id),
    reporting_manager_id UUID REFERENCES employees(id),
    date_of_joining DATE NOT NULL,
    employment_type VARCHAR(50),
    work_location VARCHAR(100),
    probation_end_date DATE,
    confirmation_date DATE,
    notice_period_days INT DEFAULT 30,
    status employee_status DEFAULT 'active',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- employee_contact
CREATE TABLE employee_contact (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id) UNIQUE,
    personal_email VARCHAR(255),
    work_email VARCHAR(255),
    personal_phone VARCHAR(20),
    emergency_contact_name VARCHAR(100),
    emergency_contact_phone VARCHAR(20),
    emergency_contact_relation VARCHAR(50),
    current_address_line1 TEXT,
    current_address_line2 TEXT,
    current_city VARCHAR(100),
    current_state VARCHAR(100),
    current_pincode VARCHAR(10),
    permanent_address_line1 TEXT,
    permanent_address_line2 TEXT,
    permanent_city VARCHAR(100),
    permanent_state VARCHAR(100),
    permanent_pincode VARCHAR(10),
    same_as_current BOOLEAN DEFAULT FALSE
);

-- employee_identity
CREATE TABLE employee_identity (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id) UNIQUE,
    aadhaar_number_encrypted BYTEA,
    aadhaar_last_four VARCHAR(4),
    pan_number VARCHAR(10),
    passport_number VARCHAR(20),
    passport_expiry DATE,
    driving_license VARCHAR(20),
    dl_expiry DATE,
    voter_id VARCHAR(20)
);

-- employee_bank
CREATE TABLE employee_bank (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id) UNIQUE,
    bank_name VARCHAR(100),
    branch_name VARCHAR(100),
    account_number_encrypted BYTEA,
    account_number_last_four VARCHAR(4),
    ifsc_code VARCHAR(11),
    account_holder_name VARCHAR(100),
    account_type VARCHAR(20)
);

-- departments
CREATE TABLE departments (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    code VARCHAR(20) UNIQUE,
    parent_id UUID REFERENCES departments(id),
    head_id UUID REFERENCES employees(id),
    is_active BOOLEAN DEFAULT TRUE
);

-- designations
CREATE TABLE designations (
    id UUID PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    level INT,
    is_active BOOLEAN DEFAULT TRUE
);
```

### 3.5 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /employees | List employees (paginated, filtered) |
| POST | /employees | Create employee |
| GET | /employees/{id} | Get employee details |
| PUT | /employees/{id} | Update employee |
| DELETE | /employees/{id} | Deactivate employee |
| GET | /employees/{id}/documents | Get employee documents |
| POST | /employees/{id}/photo | Upload profile photo |
| GET | /employees/code/next | Get next employee code |
| POST | /employees/extract-id | AI: Extract from ID card |
| GET | /departments | List departments |
| POST | /departments | Create department |
| GET | /designations | List designations |
| POST | /designations | Create designation |

---

## MODULE 4: Enterprise Document Management (EDMS)

### 4.1 Folder Structure
```
/
├── Company/
│   ├── Policies/
│   ├── Templates/
│   └── Compliance/
├── HR/
│   ├── Onboarding/
│   └── Training/
├── Finance/
│   ├── Invoices/
│   ├── Bills/
│   └── Reports/
└── Employees/
    └── {employee_code}/
        ├── Identity/
        ├── Education/
        └── Employment/
```

### 4.2 Features
- Folder hierarchy with unlimited nesting
- Role-based folder permissions
- Document versioning (keep all versions)
- Full-text search (PostgreSQL FTS)
- Bulk upload (up to 20 files)
- Bulk download as ZIP
- Document preview (PDF, images)
- Audit trail for all operations

### 4.3 AI Features
- **Auto-categorization:** Analyze document content → suggest folder
- **Smart tagging:** Extract keywords → add tags automatically
- **Summarization:** Generate 2-3 sentence summary
- **Semantic search:** "Find the leave policy" → match even if different words used

### 4.4 Database Tables
```sql
-- folders
CREATE TABLE folders (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    parent_id UUID REFERENCES folders(id),
    path TEXT, -- /Company/Policies
    owner_id UUID REFERENCES users(id),
    is_system BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- folder_permissions
CREATE TABLE folder_permissions (
    id UUID PRIMARY KEY,
    folder_id UUID REFERENCES folders(id),
    role user_role,
    user_id UUID REFERENCES users(id),
    permission permission_level, -- read, write, admin
    UNIQUE(folder_id, role, user_id)
);

-- documents
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    folder_id UUID REFERENCES folders(id),
    name VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path TEXT NOT NULL,
    file_size BIGINT,
    mime_type VARCHAR(100),
    current_version INT DEFAULT 1,
    ai_summary TEXT,
    ai_tags TEXT[],
    ai_category VARCHAR(100),
    search_vector TSVECTOR,
    uploaded_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- document_versions
CREATE TABLE document_versions (
    id UUID PRIMARY KEY,
    document_id UUID REFERENCES documents(id),
    version_number INT NOT NULL,
    file_path TEXT NOT NULL,
    file_size BIGINT,
    uploaded_by UUID REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.5 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /folders | List root folders |
| GET | /folders/{id} | Get folder with contents |
| POST | /folders | Create folder |
| PUT | /folders/{id} | Rename/move folder |
| DELETE | /folders/{id} | Delete folder (if empty) |
| GET | /folders/{id}/permissions | Get folder permissions |
| POST | /folders/{id}/permissions | Set permissions |
| GET | /documents | Search documents |
| GET | /documents/{id} | Get document metadata |
| GET | /documents/{id}/download | Download document |
| GET | /documents/{id}/preview | Get preview URL |
| POST | /documents | Upload document |
| PUT | /documents/{id} | Update metadata |
| DELETE | /documents/{id} | Delete document |
| GET | /documents/{id}/versions | List versions |
| POST | /documents/{id}/versions | Upload new version |
| POST | /documents/bulk-upload | Upload multiple |
| POST | /documents/bulk-download | Download as ZIP |
| POST | /documents/ai/categorize | AI categorization |
| POST | /documents/ai/summarize | AI summarization |

---

## MODULE 5: Employee Onboarding

### 5.1 8-Step Onboarding Wizard

| Step | Name | Fields | Validation |
|------|------|--------|------------|
| 1 | Personal Info | Name, DOB, Gender, Blood Group | Required |
| 2 | Contact Details | Email, Phone, Address | Email format, phone format |
| 3 | Identity Documents | Aadhaar, PAN, Passport | Document upload, AI extraction |
| 4 | Bank Details | Bank, Account, IFSC | IFSC validation |
| 5 | Education | Degree, Institution, Year | At least 1 entry |
| 6 | Previous Employment | Company, Role, Duration | Optional |
| 7 | Document Upload | Required documents checklist | All required uploaded |
| 8 | Review & Submit | Summary of all data | HR approval |

### 5.2 Document Checklist
**Mandatory:**
- Aadhaar Card (front & back)
- PAN Card
- 10th Marksheet
- 12th Marksheet
- Highest Degree Certificate
- Relieving Letter (if applicable)
- 3 months salary slips (if applicable)
- Cancelled cheque

**Optional:**
- Passport
- Driving License
- Address Proof
- Additional certificates

### 5.3 Workflow
```
Employee submits → HR reviews → Approve/Reject/Request changes
                              ↓
                         If Approved → Employee active
                         If Rejected → Notify with reason
                         If Changes → Employee updates → Re-submit
```

### 5.4 AI Features
- Guide employees through each step
- Validate document uploads (readable, correct type)
- Extract data from uploaded documents
- Flag missing or incomplete information
- Suggest corrections

### 5.5 Database Tables
```sql
-- onboarding_progress
CREATE TABLE onboarding_progress (
    id UUID PRIMARY KEY,
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
    submitted_at TIMESTAMP,
    reviewed_by UUID REFERENCES users(id),
    reviewed_at TIMESTAMP,
    status onboarding_status DEFAULT 'in_progress',
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- employee_education
CREATE TABLE employee_education (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    degree VARCHAR(100),
    specialization VARCHAR(100),
    institution VARCHAR(200),
    university VARCHAR(200),
    year_of_passing INT,
    percentage DECIMAL(5,2),
    grade VARCHAR(10),
    document_id UUID REFERENCES documents(id)
);

-- employee_previous_employment
CREATE TABLE employee_previous_employment (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    company_name VARCHAR(200),
    designation VARCHAR(100),
    start_date DATE,
    end_date DATE,
    last_ctc DECIMAL(12,2),
    reason_for_leaving TEXT,
    relieving_letter_id UUID REFERENCES documents(id)
);
```

---

## MODULE 6: Leave Management

### 6.1 Leave Types

| Code | Name | Annual Quota | Carry Forward | Encashable |
|------|------|--------------|---------------|------------|
| CL | Casual Leave | 12 | No | No |
| SL | Sick Leave | 12 | No | No |
| EL | Earned Leave | 15 | Yes (max 30) | Yes |
| ML | Maternity Leave | 182 days | No | No |
| PL | Paternity Leave | 15 days | No | No |
| LOP | Loss of Pay | Unlimited | No | No |
| CO | Comp-Off | Earned | Expires 30 days | No |
| WFH | Work from Home | Unlimited | No | No |

### 6.2 Holiday Calendar
- Karnataka state holidays (mandatory)
- National holidays (mandatory)
- Company-specific holidays (configurable)
- Restricted holidays (choose X from list)

### 6.3 Leave Workflow
```
Employee applies → Manager approves/rejects
                 ↓
            If Approved → Deduct balance
            If Rejected → Notify with reason
            
Auto-approve rules:
- WFH: Always auto-approve
- CL/SL ≤ 2 days with 3+ days notice: Auto-approve if balance available
```

### 6.4 AI Features
- Suggest optimal leave dates (avoid team conflicts)
- Predict team availability
- Auto-approve routine requests
- Flag unusual patterns (frequent Mondays/Fridays)

### 6.5 Database Tables
```sql
-- leave_types
CREATE TABLE leave_types (
    id UUID PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    annual_quota INT,
    carry_forward BOOLEAN DEFAULT FALSE,
    max_carry_forward INT,
    is_encashable BOOLEAN DEFAULT FALSE,
    requires_document BOOLEAN DEFAULT FALSE,
    min_days INT DEFAULT 0.5,
    max_days INT,
    advance_notice_days INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE
);

-- holidays
CREATE TABLE holidays (
    id UUID PRIMARY KEY,
    date DATE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type holiday_type, -- national, state, company, restricted
    is_optional BOOLEAN DEFAULT FALSE,
    year INT,
    UNIQUE(date, name)
);

-- leave_balances
CREATE TABLE leave_balances (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
    year INT,
    opening_balance DECIMAL(4,1) DEFAULT 0,
    accrued DECIMAL(4,1) DEFAULT 0,
    used DECIMAL(4,1) DEFAULT 0,
    pending DECIMAL(4,1) DEFAULT 0,
    lapsed DECIMAL(4,1) DEFAULT 0,
    closing_balance DECIMAL(4,1) GENERATED ALWAYS AS (opening_balance + accrued - used - lapsed) STORED,
    UNIQUE(employee_id, leave_type_id, year)
);

-- leave_requests
CREATE TABLE leave_requests (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    leave_type_id UUID REFERENCES leave_types(id),
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    days DECIMAL(4,1) NOT NULL,
    reason TEXT,
    document_id UUID REFERENCES documents(id),
    status leave_status DEFAULT 'pending',
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### 6.6 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /leave-types | List leave types |
| GET | /holidays | List holidays for year |
| GET | /leave/balance | Get current user's balance |
| GET | /leave/balance/{employee_id} | Get employee's balance |
| GET | /leave/requests | List leave requests |
| POST | /leave/requests | Submit leave request |
| GET | /leave/requests/{id} | Get request details |
| PUT | /leave/requests/{id}/approve | Approve request |
| PUT | /leave/requests/{id}/reject | Reject request |
| DELETE | /leave/requests/{id} | Cancel request |
| GET | /leave/calendar | Team leave calendar |
| POST | /leave/ai/suggest-dates | AI: Suggest optimal dates |

---

## MODULE 7: Timesheet Management

### 7.1 Timesheet Structure
- Weekly timesheet (Monday to Sunday)
- Daily entries with hours
- Project + Task allocation
- Billable vs Non-billable
- Submission + Approval workflow

### 7.2 Time Entry Rules
- Minimum 8 hours per working day
- Maximum 12 hours per day
- Maximum 50 hours per week
- Cannot exceed project allocated hours
- Cannot log time for future dates

### 7.3 Database Tables
```sql
-- timesheets
CREATE TABLE timesheets (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    week_start_date DATE NOT NULL,
    week_end_date DATE NOT NULL,
    total_hours DECIMAL(5,2) DEFAULT 0,
    billable_hours DECIMAL(5,2) DEFAULT 0,
    status timesheet_status DEFAULT 'draft',
    submitted_at TIMESTAMP,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP,
    rejection_reason TEXT,
    UNIQUE(employee_id, week_start_date)
);

-- timesheet_entries
CREATE TABLE timesheet_entries (
    id UUID PRIMARY KEY,
    timesheet_id UUID REFERENCES timesheets(id),
    project_id UUID REFERENCES projects(id),
    task_id UUID REFERENCES tasks(id),
    date DATE NOT NULL,
    hours DECIMAL(4,2) NOT NULL,
    is_billable BOOLEAN DEFAULT TRUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## MODULE 8: Payroll System

### 8.1 Salary Components

#### Earnings
| Code | Name | Type | Taxable | PF Applicable |
|------|------|------|---------|---------------|
| BASIC | Basic Salary | Fixed | Yes | Yes |
| HRA | House Rent Allowance | Fixed | Partially | No |
| SPECIAL | Special Allowance | Fixed | Yes | No |
| CONV | Conveyance Allowance | Fixed | Yes | No |
| MED | Medical Allowance | Fixed | Yes | No |
| BONUS | Performance Bonus | Variable | Yes | No |
| INCEN | Incentive | Variable | Yes | No |
| OT | Overtime | Variable | Yes | No |

#### Deductions
| Code | Name | Type | Formula |
|------|------|------|---------|
| PF | Provident Fund | Statutory | See Section 6.1 |
| ESI | Employee State Insurance | Statutory | See Section 6.2 |
| PT | Professional Tax | Statutory | See Section 6.3 |
| TDS | Tax Deducted at Source | Statutory | See Section 6.4 |
| LOP | Loss of Pay | Variable | (Gross / Working Days) × LOP Days |
| ADVANCE | Salary Advance | Recovery | As per schedule |
| LOAN | Loan EMI | Recovery | As per schedule |

### 8.2 CTC Structure (Typical)
```
CTC = Gross Salary + Employer PF + Employer ESI

Gross Salary:
  Basic:    40% of CTC
  HRA:      40% of Basic (16% of CTC)
  Special:  Remaining after all components

Example for 6 LPA:
  CTC:      ₹6,00,000
  Monthly:  ₹50,000

  Basic:    ₹20,000 (40%)
  HRA:      ₹8,000 (40% of Basic)
  Special:  ₹17,400
  Gross:    ₹45,400
  
  Employer PF:  ₹2,400 (12% of Basic)
  Employer ESI: ₹1,476 (if applicable)
```

### 8.3 Payroll Processing
```
1. Select month/year
2. Fetch active employees
3. For each employee:
   a. Calculate working days (calendar - holidays - leaves)
   b. Calculate earnings (fixed + variable - LOP)
   c. Calculate PF, ESI, PT
   d. Calculate TDS
   e. Calculate net salary
4. Generate payslips
5. Generate bank transfer file
6. Finalize payroll
```

### 8.4 Database Tables
```sql
-- salary_components
CREATE TABLE salary_components (
    id UUID PRIMARY KEY,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    type component_type, -- earning, deduction
    calculation_type calc_type, -- fixed, percentage, formula
    is_taxable BOOLEAN DEFAULT TRUE,
    is_pf_applicable BOOLEAN DEFAULT FALSE,
    is_esi_applicable BOOLEAN DEFAULT FALSE,
    display_order INT,
    is_active BOOLEAN DEFAULT TRUE
);

-- employee_salary
CREATE TABLE employee_salary (
    id UUID PRIMARY KEY,
    employee_id UUID REFERENCES employees(id),
    effective_from DATE NOT NULL,
    effective_to DATE,
    ctc_annual DECIMAL(12,2) NOT NULL,
    ctc_monthly DECIMAL(12,2) NOT NULL,
    gross_monthly DECIMAL(12,2) NOT NULL,
    is_current BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

-- employee_salary_components
CREATE TABLE employee_salary_components (
    id UUID PRIMARY KEY,
    employee_salary_id UUID REFERENCES employee_salary(id),
    component_id UUID REFERENCES salary_components(id),
    amount DECIMAL(12,2) NOT NULL,
    percentage DECIMAL(5,2)
);

-- payroll_runs
CREATE TABLE payroll_runs (
    id UUID PRIMARY KEY,
    month INT NOT NULL,
    year INT NOT NULL,
    status payroll_status DEFAULT 'draft',
    total_employees INT,
    total_gross DECIMAL(14,2),
    total_deductions DECIMAL(14,2),
    total_net DECIMAL(14,2),
    processed_by UUID REFERENCES users(id),
    processed_at TIMESTAMP,
    finalized_by UUID REFERENCES users(id),
    finalized_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(month, year)
);

-- payslips
CREATE TABLE payslips (
    id UUID PRIMARY KEY,
    payroll_run_id UUID REFERENCES payroll_runs(id),
    employee_id UUID REFERENCES employees(id),
    month INT NOT NULL,
    year INT NOT NULL,
    working_days INT,
    days_worked DECIMAL(4,1),
    lop_days DECIMAL(4,1) DEFAULT 0,
    
    -- Earnings
    basic DECIMAL(10,2),
    hra DECIMAL(10,2),
    special_allowance DECIMAL(10,2),
    other_earnings JSONB,
    gross_salary DECIMAL(10,2),
    
    -- Deductions
    pf_employee DECIMAL(10,2),
    esi_employee DECIMAL(10,2),
    professional_tax DECIMAL(10,2),
    tds DECIMAL(10,2),
    other_deductions JSONB,
    total_deductions DECIMAL(10,2),
    
    -- Net
    net_salary DECIMAL(10,2),
    
    -- Employer contributions
    pf_employer DECIMAL(10,2),
    esi_employer DECIMAL(10,2),
    
    pdf_url TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(employee_id, month, year)
);

-- payslip_components
CREATE TABLE payslip_components (
    id UUID PRIMARY KEY,
    payslip_id UUID REFERENCES payslips(id),
    component_id UUID REFERENCES salary_components(id),
    amount DECIMAL(10,2)
);
```

### 8.5 API Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /salary-components | List components |
| GET | /employees/{id}/salary | Get salary structure |
| POST | /employees/{id}/salary | Create/revise salary |
| GET | /payroll/runs | List payroll runs |
| POST | /payroll/runs | Create payroll run |
| GET | /payroll/runs/{id} | Get run details |
| POST | /payroll/runs/{id}/process | Process payroll |
| POST | /payroll/runs/{id}/finalize | Finalize payroll |
| GET | /payslips | List payslips |
| GET | /payslips/{id} | Get payslip |
| GET | /payslips/{id}/pdf | Download payslip PDF |
| GET | /payroll/runs/{id}/bank-file | Download bank transfer file |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 6: INDIA COMPLIANCE - EXACT FORMULAS
# ═══════════════════════════════════════════════════════════════════════════════

## 6.1 Provident Fund (PF)

### 6.1.1 PF Wage Definition
```
PF Wage = Basic Salary + Dearness Allowance (DA)

Note: DA is typically 0 for IT companies. If no DA:
PF Wage = Basic Salary
```

### 6.1.2 Employee Contribution
```
Employee PF = PF Wage × 12%

Rounding: ROUND_HALF_UP to nearest rupee
```

### 6.1.3 Employer Contribution (Split)
```
Total Employer Contribution = 12% of PF Wage

Split as:
1. EPS (Employee Pension Scheme):
   IF PF Wage ≤ ₹15,000:
       EPS = PF Wage × 8.33%
   ELSE:
       EPS = ₹15,000 × 8.33% = ₹1,250 (capped)

2. EPF (Employee Provident Fund):
   EPF = (PF Wage × 12%) - EPS

Example calculations:
┌────────────┬──────────────┬──────────────┬──────────────┐
│ PF Wage    │ Employee PF  │ Employer EPS │ Employer EPF │
├────────────┼──────────────┼──────────────┼──────────────┤
│ ₹12,000    │ ₹1,440       │ ₹1,000       │ ₹440         │
│ ₹15,000    │ ₹1,800       │ ₹1,250       │ ₹550         │
│ ₹20,000    │ ₹2,400       │ ₹1,250       │ ₹1,150       │
│ ₹25,000    │ ₹3,000       │ ₹1,250       │ ₹1,750       │
│ ₹50,000    │ ₹6,000       │ ₹1,250       │ ₹4,750       │
└────────────┴──────────────┴──────────────┴──────────────┘
```

### 6.1.4 Admin Charges (Employer)
```
Admin Charges = PF Wage × 0.50%
EDLI (Insurance) = PF Wage × 0.50%

These are additional employer costs, not deducted from employee.
```

### 6.1.5 PF ECR File Format
```
ECR (Electronic Challan cum Return) format for EPFO:
- UAN, Member Name, Gross Wages, EPF Wages, EPS Wages
- EPF Contribution (EE), EPS Contribution, EPF Contribution (ER)
- NCP Days, Refund Amount
```

### 6.1.6 Due Date
```
PF Payment: 15th of following month
PF Return (ECR): 15th of following month
```

---

## 6.2 Employee State Insurance (ESI)

### 6.2.1 Applicability
```
ESI is applicable IF:
  Gross Salary ≤ ₹21,000 per month

Once applicable, continue for the contribution period even if 
salary exceeds threshold later.
```

### 6.2.2 Contribution Rates
```
Employee Contribution = Gross Salary × 0.75%
Employer Contribution = Gross Salary × 3.25%
Total Contribution = 4% of Gross Salary

Gross Salary includes:
- Basic + DA + HRA + All Allowances
- Excludes: Reimbursements, Bonus (if not monthly)

Example calculations:
┌────────────┬────────────┬──────────────┬──────────────┐
│ Gross      │ Applicable │ Employee ESI │ Employer ESI │
├────────────┼────────────┼──────────────┼──────────────┤
│ ₹15,000    │ Yes        │ ₹113         │ ₹488         │
│ ₹18,000    │ Yes        │ ₹135         │ ₹585         │
│ ₹21,000    │ Yes        │ ₹158         │ ₹683         │
│ ₹25,000    │ No         │ ₹0           │ ₹0           │
│ ₹30,000    │ No         │ ₹0           │ ₹0           │
└────────────┴────────────┴──────────────┴──────────────┘
```

### 6.2.3 Due Date
```
ESI Payment: 15th of following month
ESI Return: Half-yearly (October & April)
```

---

## 6.3 Professional Tax (Karnataka)

### 6.3.1 Slabs
```
Karnataka Professional Tax Slabs:

IF Gross Salary ≤ ₹15,000:
    PT = ₹0

IF Gross Salary > ₹15,000:
    PT = ₹200 per month
    
February Adjustment:
    PT = ₹300 (to make annual total ₹2,500)

Annual Calculation:
    11 months × ₹200 = ₹2,200
    1 month (Feb) × ₹300 = ₹300
    Total = ₹2,500
```

### 6.3.2 Implementation
```python
def calculate_pt(gross_salary: Decimal, month: int) -> Decimal:
    if gross_salary <= Decimal("15000"):
        return Decimal("0")
    
    if month == 2:  # February
        return Decimal("300")
    else:
        return Decimal("200")
```

---

## 6.4 Tax Deducted at Source (TDS) - Salary

### 6.4.1 New Tax Regime (Default from FY 2024-25)
```
Standard Deduction: ₹75,000 per annum

Taxable Income = Gross Annual Income - Standard Deduction

Tax Slabs (New Regime):
┌─────────────────────────┬──────────┐
│ Income Slab             │ Tax Rate │
├─────────────────────────┼──────────┤
│ Up to ₹3,00,000         │ 0%       │
│ ₹3,00,001 - ₹7,00,000   │ 5%       │
│ ₹7,00,001 - ₹10,00,000  │ 10%      │
│ ₹10,00,001 - ₹12,00,000 │ 15%      │
│ ₹12,00,001 - ₹15,00,000 │ 20%      │
│ Above ₹15,00,000        │ 30%      │
└─────────────────────────┴──────────┘

Health & Education Cess = 4% of total tax

Example: Annual Gross = ₹12,00,000
- Standard Deduction = ₹75,000
- Taxable Income = ₹11,25,000
- Tax calculation:
  - 0-3L: ₹0
  - 3-7L: ₹20,000 (4L × 5%)
  - 7-10L: ₹30,000 (3L × 10%)
  - 10-11.25L: ₹18,750 (1.25L × 15%)
  - Total Tax: ₹68,750
  - Cess (4%): ₹2,750
  - Total: ₹71,500
  - Monthly TDS: ₹5,958
```

### 6.4.2 Old Tax Regime (Optional)
```
Tax Slabs (Old Regime):
┌─────────────────────────┬──────────┐
│ Income Slab             │ Tax Rate │
├─────────────────────────┼──────────┤
│ Up to ₹2,50,000         │ 0%       │
│ ₹2,50,001 - ₹5,00,000   │ 5%       │
│ ₹5,00,001 - ₹10,00,000  │ 20%      │
│ Above ₹10,00,000        │ 30%      │
└─────────────────────────┴──────────┘

Standard Deduction: ₹50,000

Deductions Available:
- 80C: Up to ₹1,50,000 (PF, PPF, ELSS, LIC, NSC, etc.)
- 80D: Up to ₹25,000 (Health insurance premium)
- 24(b): Up to ₹2,00,000 (Home loan interest)
- HRA Exemption: As per formula

Health & Education Cess = 4% of total tax
```

### 6.4.3 TDS Calculation (Monthly)
```python
def calculate_monthly_tds(annual_gross: Decimal, regime: str, 
                          declarations: dict) -> Decimal:
    if regime == "new":
        std_deduction = Decimal("75000")
        taxable = annual_gross - std_deduction
        tax = calculate_new_regime_tax(taxable)
    else:
        std_deduction = Decimal("50000")
        deductions = sum_80c_80d_etc(declarations)
        hra_exempt = calculate_hra_exemption(declarations)
        taxable = annual_gross - std_deduction - deductions - hra_exempt
        tax = calculate_old_regime_tax(taxable)
    
    cess = tax * Decimal("0.04")
    total_tax = tax + cess
    monthly_tds = total_tax / 12
    
    return monthly_tds.quantize(Decimal("1"), ROUND_HALF_UP)
```

---

## 6.5 TDS on Vendor Payments

### 6.5.1 Section 194C - Contractors
```
Rate:
- Individual/HUF: 1%
- Others (Company, Firm, etc.): 2%

Threshold:
- Single payment: ₹30,000
- Annual aggregate: ₹1,00,000

No TDS if:
- Vendor has valid lower deduction certificate
- Vendor provides Form 15G/15H
```

### 6.5.2 Section 194J - Professional/Technical Services
```
Rate: 10%
Threshold: ₹30,000 per annum

Covers:
- Legal services
- Medical services
- Engineering services
- Accounting services
- Technical services
- Advertising services
- IT services (from vendors)
```

### 6.5.3 Section 194H - Commission/Brokerage
```
Rate: 5%
Threshold: ₹15,000 per annum
```

### 6.5.4 Section 194I - Rent
```
Rate:
- Plant & Machinery: 2%
- Land & Building: 10%

Threshold: ₹2,40,000 per annum
```

### 6.5.5 TDS Implementation
```sql
-- tds_sections
CREATE TABLE tds_sections (
    id UUID PRIMARY KEY,
    section VARCHAR(10) NOT NULL,
    name VARCHAR(100) NOT NULL,
    rate_individual DECIMAL(5,2),
    rate_company DECIMAL(5,2),
    threshold_single DECIMAL(12,2),
    threshold_annual DECIMAL(12,2),
    is_active BOOLEAN DEFAULT TRUE
);

-- Sample data
INSERT INTO tds_sections VALUES
('194C', 'Contractor', 1.00, 2.00, 30000, 100000),
('194J', 'Professional Services', 10.00, 10.00, 0, 30000),
('194H', 'Commission', 5.00, 5.00, 0, 15000),
('194I-P', 'Rent - Plant & Machinery', 2.00, 2.00, 0, 240000),
('194I-L', 'Rent - Land & Building', 10.00, 10.00, 0, 240000);
```

---

## 6.6 GST (Goods and Services Tax)

### 6.6.1 GST Rates for IT Services
```
HSN/SAC Codes for IT Services:
- 998311: Management consulting services
- 998312: Business consulting services
- 998313: Information technology consulting
- 998314: IT design and development
- 998315: IT infrastructure management
- 998316: IT support services
- 998319: Other IT services
- 9983: Information technology services (general)

Rate: 18% (standard for IT services)
```

### 6.6.2 GST Calculation
```
INTRA-STATE (Seller and Buyer in same state):
  CGST = 9%
  SGST = 9%
  Total = 18%

INTER-STATE (Seller and Buyer in different states):
  IGST = 18%

EXPORT (LUT):
  GST = 0% (with Letter of Undertaking)

Example:
Invoice Amount (Pre-GST): ₹1,00,000
If same state (Karnataka to Karnataka):
  CGST: ₹9,000
  SGST: ₹9,000
  Total: ₹1,18,000

If different state (Karnataka to Maharashtra):
  IGST: ₹18,000
  Total: ₹1,18,000
```

### 6.6.3 GSTR-1 (Outward Supplies)
```
Due Date: 11th of following month

Sections:
- B2B: Business to Business invoices (with GSTIN)
- B2CL: B2C Large (>₹2.5L, inter-state)
- B2CS: B2C Small (<₹2.5L or intra-state)
- CDNR: Credit/Debit Notes (B2B)
- CDNUR: Credit/Debit Notes (B2C)
- EXP: Exports
- AT: Advance Received
- ATADJ: Advance Adjusted
- HSN: HSN Summary
- DOCS: Document Summary
```

### 6.6.4 GSTR-3B (Summary Return)
```
Due Date: 20th of following month

Sections:
3.1: Outward supplies
3.2: Inter-state supplies to unregistered
4: ITC (Input Tax Credit)
5: Exempt/nil rated/non-GST supplies
6: Tax payable and paid
```

---

## 6.7 Compliance Calendar

| Due Date | Compliance | Description |
|----------|------------|-------------|
| 7th | TDS Payment | Monthly TDS deposit |
| 11th | GSTR-1 | Outward supplies return |
| 15th | PF Payment | PF challan + ECR |
| 15th | ESI Payment | ESI challan |
| 20th | GSTR-3B | Monthly GST summary |
| 30th | TDS Return | Quarterly 24Q/26Q |
| 15th June | Form 16 | Annual TDS certificate |
| 31st Oct | ESI Return | Half-yearly return |
| 31st Dec | GSTR-9 | Annual return |

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 7: COMPLETE DATABASE SCHEMA (127 Tables)
# ═══════════════════════════════════════════════════════════════════════════════

## 7.1 Authentication & Users (3 tables)
1. users
2. user_sessions
3. audit_logs

## 7.2 Organization (6 tables)
4. company_profile
5. company_statutory
6. company_bank_accounts
7. authorized_signatories
8. departments
9. designations

## 7.3 Employees (9 tables)
10. employees
11. employee_contact
12. employee_identity
13. employee_bank
14. employee_employment
15. employee_documents
16. employee_education
17. employee_previous_employment
18. employee_nominees

## 7.4 Document Management (4 tables)
19. folders
20. folder_permissions
21. documents
22. document_versions

## 7.5 Onboarding (2 tables)
23. onboarding_progress
24. onboarding_documents_checklist

## 7.6 Leave Management (5 tables)
25. leave_types
26. holidays
27. leave_balances
28. leave_requests
29. leave_encashments

## 7.7 Timesheet (3 tables)
30. timesheets
31. timesheet_entries
32. timesheet_approvals

## 7.8 Payroll (15 tables)
33. salary_components
34. employee_salary
35. employee_salary_components
36. tax_declarations
37. tax_declaration_items
38. payroll_runs
39. payslips
40. payslip_components
41. payslip_adjustments
42. salary_advances
43. salary_advance_recoveries
44. loans
45. loan_emis
46. arrears
47. reimbursements

## 7.9 Statutory (8 tables)
48. statutory_settings
49. pf_monthly_data
50. pf_ecr_files
51. esi_monthly_data
52. esi_return_files
53. tds_salary_monthly
54. tds_24q_files
55. form16_data

## 7.10 Chart of Accounts & GL (12 tables)
56. account_groups
57. accounts
58. accounting_periods
59. fiscal_years
60. journal_entries
61. journal_entry_lines
62. recurring_entries
63. recurring_entry_lines
64. period_close_status
65. opening_balances
66. ledger_transactions
67. cost_centers

## 7.11 Multi-Currency (3 tables)
68. currencies
69. exchange_rates
70. forex_transactions

## 7.12 Customers & AR (8 tables)
71. customers
72. customer_contacts
73. customer_addresses
74. invoices
75. invoice_line_items
76. receipts
77. receipt_allocations
78. lut_records

## 7.13 Vendors & AP (8 tables)
79. vendors
80. vendor_contacts
81. vendor_addresses
82. bills
83. bill_line_items
84. payments
85. payment_allocations
86. tds_certificates

## 7.14 Banking (7 tables)
87. bank_accounts
88. bank_transactions
89. bank_statements
90. bank_statement_lines
91. bank_reconciliations
92. reconciliation_matches
93. petty_cash_entries

## 7.15 GST (6 tables)
94. hsn_sac_codes
95. gst_returns
96. gstr1_b2b
97. gstr1_b2cs
98. gstr3b_data
99. gst_reconciliation

## 7.16 TDS on Vendors (4 tables)
100. tds_sections
101. vendor_tds_tracking
102. tds_payments
103. tds_26q_data

## 7.17 CRM (5 tables)
104. leads
105. lead_sources
106. lead_activities
107. lead_scores
108. pipelines

## 7.18 Projects (9 tables)
109. projects
110. project_types
111. milestones
112. tasks
113. task_assignments
114. resource_allocations
115. project_billings
116. wbs_templates
117. wbs_template_items

## 7.19 AI (7 tables)
118. ai_providers
119. ai_requests
120. ai_corrections
121. ai_confidence_rules
122. transaction_patterns
123. ai_processing_queue
124. ai_suggestions

## 7.20 Compliance (3 tables)
125. compliance_categories
126. compliance_items
127. compliance_tracker

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 8: API ENDPOINTS (267 Endpoints)
# ═══════════════════════════════════════════════════════════════════════════════

## Authentication (9)
- POST /auth/login
- POST /auth/refresh
- POST /auth/logout
- GET /auth/me
- POST /auth/change-password
- POST /auth/forgot-password
- POST /auth/reset-password
- POST /auth/verify-email
- POST /auth/resend-verification

## Users (7)
- GET /users
- POST /users
- GET /users/{id}
- PUT /users/{id}
- DELETE /users/{id}
- POST /users/{id}/activate
- POST /users/{id}/deactivate

## Organization (12)
- GET /company
- PUT /company
- GET /company/statutory
- PUT /company/statutory
- GET /company/bank-accounts
- POST /company/bank-accounts
- PUT /company/bank-accounts/{id}
- DELETE /company/bank-accounts/{id}
- GET /departments
- POST /departments
- GET /designations
- POST /designations

## Employees (18)
- GET /employees
- POST /employees
- GET /employees/{id}
- PUT /employees/{id}
- DELETE /employees/{id}
- GET /employees/{id}/contact
- PUT /employees/{id}/contact
- GET /employees/{id}/identity
- PUT /employees/{id}/identity
- GET /employees/{id}/bank
- PUT /employees/{id}/bank
- GET /employees/{id}/documents
- POST /employees/{id}/photo
- GET /employees/code/next
- POST /employees/ai/extract-id
- GET /employees/{id}/salary
- POST /employees/{id}/salary
- GET /employees/{id}/history

## Documents (16)
- GET /folders
- GET /folders/{id}
- POST /folders
- PUT /folders/{id}
- DELETE /folders/{id}
- GET /folders/{id}/permissions
- POST /folders/{id}/permissions
- GET /documents
- GET /documents/{id}
- GET /documents/{id}/download
- GET /documents/{id}/preview
- POST /documents
- PUT /documents/{id}
- DELETE /documents/{id}
- GET /documents/{id}/versions
- POST /documents/{id}/versions

## Onboarding (8)
- GET /onboarding/progress
- PUT /onboarding/step/{step}
- POST /onboarding/submit
- GET /onboarding/pending
- POST /onboarding/{id}/approve
- POST /onboarding/{id}/reject
- POST /onboarding/{id}/request-changes
- GET /onboarding/checklist

## Leave (14)
- GET /leave-types
- POST /leave-types
- GET /holidays
- POST /holidays
- GET /leave/balance
- GET /leave/balance/{employee_id}
- GET /leave/requests
- POST /leave/requests
- GET /leave/requests/{id}
- PUT /leave/requests/{id}/approve
- PUT /leave/requests/{id}/reject
- DELETE /leave/requests/{id}
- GET /leave/calendar
- POST /leave/ai/suggest-dates

## Timesheet (10)
- GET /timesheets
- GET /timesheets/current
- POST /timesheets
- GET /timesheets/{id}
- PUT /timesheets/{id}
- POST /timesheets/{id}/submit
- POST /timesheets/{id}/approve
- POST /timesheets/{id}/reject
- GET /timesheets/report
- POST /timesheets/ai/suggest

## Payroll (20)
- GET /salary-components
- POST /salary-components
- GET /payroll/runs
- POST /payroll/runs
- GET /payroll/runs/{id}
- POST /payroll/runs/{id}/process
- POST /payroll/runs/{id}/finalize
- DELETE /payroll/runs/{id}
- GET /payslips
- GET /payslips/{id}
- GET /payslips/{id}/pdf
- GET /payroll/runs/{id}/bank-file
- GET /payroll/summary
- POST /tax-declarations
- GET /tax-declarations/{employee_id}
- PUT /tax-declarations/{id}
- POST /salary-advances
- GET /salary-advances
- POST /loans
- GET /loans

## Statutory (16)
- GET /statutory/settings
- PUT /statutory/settings
- GET /statutory/pf/monthly
- POST /statutory/pf/ecr
- GET /statutory/pf/ecr/{id}/download
- GET /statutory/esi/monthly
- POST /statutory/esi/return
- GET /statutory/tds/monthly
- POST /statutory/tds/24q
- GET /statutory/tds/24q/{id}/download
- POST /statutory/form16/generate
- GET /statutory/form16/{employee_id}
- GET /statutory/pt/monthly
- GET /statutory/calendar
- GET /statutory/reminders
- POST /statutory/ai/prepare

## Accounting (22)
- GET /accounts
- POST /accounts
- GET /accounts/{id}
- PUT /accounts/{id}
- GET /accounts/tree
- GET /account-groups
- POST /account-groups
- GET /accounting-periods
- POST /accounting-periods
- GET /journal-entries
- POST /journal-entries
- GET /journal-entries/{id}
- PUT /journal-entries/{id}
- DELETE /journal-entries/{id}
- POST /journal-entries/{id}/post
- GET /ledger/{account_id}
- GET /trial-balance
- POST /period/{id}/close
- GET /recurring-entries
- POST /recurring-entries
- GET /cost-centers
- POST /cost-centers

## Customers & AR (18)
- GET /customers
- POST /customers
- GET /customers/{id}
- PUT /customers/{id}
- GET /invoices
- POST /invoices
- GET /invoices/{id}
- PUT /invoices/{id}
- DELETE /invoices/{id}
- GET /invoices/{id}/pdf
- POST /invoices/{id}/email
- POST /invoices/ai/generate
- GET /receipts
- POST /receipts
- GET /receipts/{id}
- GET /ar/aging
- GET /ar/outstanding
- POST /lut

## Vendors & AP (18)
- GET /vendors
- POST /vendors
- GET /vendors/{id}
- PUT /vendors/{id}
- GET /bills
- POST /bills
- GET /bills/{id}
- PUT /bills/{id}
- DELETE /bills/{id}
- POST /bills/ai/extract
- GET /payments
- POST /payments
- GET /payments/{id}
- GET /ap/aging
- GET /ap/outstanding
- GET /tds/certificates
- POST /tds/certificates
- GET /vendor/{id}/tds-summary

## Banking (14)
- GET /bank-accounts
- POST /bank-accounts
- GET /bank-accounts/{id}
- PUT /bank-accounts/{id}
- GET /bank-accounts/{id}/transactions
- POST /bank-accounts/{id}/import
- GET /bank-accounts/{id}/reconciliation
- POST /bank-accounts/{id}/reconcile
- POST /bank/ai/categorize
- POST /bank/ai/match
- GET /petty-cash
- POST /petty-cash
- GET /petty-cash/balance
- POST /petty-cash/replenish

## GST (12)
- GET /hsn-sac
- POST /hsn-sac
- GET /gst/returns
- GET /gst/gstr1/{period}
- POST /gst/gstr1/{period}/generate
- GET /gst/gstr1/{period}/download
- GET /gst/gstr3b/{period}
- POST /gst/gstr3b/{period}/generate
- GET /gst/gstr3b/{period}/download
- GET /gst/reconciliation
- POST /gst/ai/validate
- GET /gst/summary

## TDS Vendors (8)
- GET /tds/sections
- GET /tds/vendor-tracking
- GET /tds/vendor/{id}/summary
- POST /tds/26q/generate
- GET /tds/26q/{id}/download
- GET /tds/payments
- POST /tds/payments
- GET /tds/pending

## Reports (12)
- GET /reports/trial-balance
- GET /reports/profit-loss
- GET /reports/balance-sheet
- GET /reports/cash-flow
- GET /reports/ar-aging
- GET /reports/ap-aging
- GET /reports/gst-summary
- GET /reports/tds-summary
- GET /reports/payroll-summary
- GET /reports/leave-summary
- POST /reports/custom
- POST /reports/ai/insights

## CRM (10)
- GET /leads
- POST /leads
- GET /leads/{id}
- PUT /leads/{id}
- POST /leads/{id}/convert
- GET /leads/{id}/activities
- POST /leads/{id}/activities
- GET /pipeline
- POST /leads/ai/score
- POST /leads/ai/email

## Projects (16)
- GET /projects
- POST /projects
- GET /projects/{id}
- PUT /projects/{id}
- GET /projects/{id}/milestones
- POST /projects/{id}/milestones
- GET /projects/{id}/tasks
- POST /projects/{id}/tasks
- GET /tasks/{id}
- PUT /tasks/{id}
- GET /tasks/{id}/assignments
- POST /tasks/{id}/assignments
- GET /projects/{id}/billing
- POST /projects/{id}/billing
- GET /wbs-templates
- POST /wbs-templates

## AI (10)
- POST /ai/query
- POST /ai/process-document
- GET /ai/daily-briefing
- POST /ai/categorize
- GET /ai/suggestions
- POST /ai/execute
- GET /ai/queue
- POST /ai/correct
- GET /ai/patterns
- GET /ai/providers

## Settings (8)
- GET /settings/general
- PUT /settings/general
- GET /settings/email
- PUT /settings/email
- GET /settings/notifications
- PUT /settings/notifications
- GET /settings/integrations
- PUT /settings/integrations

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 9: FRONTEND SCREENS (68 Screens)
# ═══════════════════════════════════════════════════════════════════════════════

## Authentication (4)
1. Login Page
2. Forgot Password
3. Reset Password
4. Email Verification

## Dashboards (5)
5. Admin Dashboard
6. HR Dashboard
7. Accountant Dashboard
8. Employee Dashboard
9. CA Dashboard

## Employees (8)
10. Employee List
11. Employee Detail View
12. Employee Create/Edit Form
13. Employee Documents
14. Employee Salary History
15. Employee Payslips
16. Org Chart
17. Directory

## Onboarding (3)
18. Onboarding Wizard (8-step)
19. Onboarding Approvals
20. Document Checklist

## Documents (4)
21. Folder Browser
22. Document Viewer
23. Upload Modal
24. Search Results

## Leave (5)
25. Leave Dashboard
26. Leave Request Form
27. Leave Approvals
28. Leave Calendar
29. Holiday Calendar

## Timesheet (4)
30. Timesheet Grid
31. Timesheet Approval
32. Timesheet Report
33. Project Allocation

## Payroll (7)
34. Payroll Dashboard
35. Salary Structure Setup
36. Tax Declaration Form
37. Payroll Run
38. Payslip View
39. Bank File Generation
40. Form 16 View

## Statutory (4)
41. Statutory Settings
42. PF ECR Generation
43. ESI Return
44. TDS Returns

## Accounting (6)
45. Chart of Accounts
46. Journal Entry Form
47. Ledger View
48. Trial Balance
49. Period Close
50. Recurring Entries

## Customers & Invoicing (5)
51. Customer List
52. Customer Form
53. Invoice List
54. Invoice Form
55. Receipt Entry

## Vendors & Bills (5)
56. Vendor List
57. Vendor Form
58. Bill List
59. Bill Form
60. Payment Entry

## Banking (3)
61. Bank Accounts
62. Transaction Import
63. Reconciliation

## Reports (4)
64. Financial Reports
65. P&L Statement
66. Balance Sheet
67. Cash Flow

## Other (5)
68. Settings

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 10: NON-FUNCTIONAL REQUIREMENTS
# ═══════════════════════════════════════════════════════════════════════════════

## 10.1 Performance
- API response time: <500ms (95th percentile)
- Page load time: <3 seconds
- Database query time: <100ms
- File upload: Support up to 10MB
- Concurrent users: 50

## 10.2 Security
- HTTPS only (TLS 1.3)
- JWT authentication with short-lived tokens
- Password hashing with bcrypt (12 rounds)
- Rate limiting (100 requests/minute)
- SQL injection prevention (ORM)
- XSS prevention (React escaping)
- CSRF protection
- Sensitive data encryption (AES-256)
- Audit logging for all sensitive operations
- PII masking in logs

## 10.3 Availability
- Uptime: 99.5%
- Backup: Daily at 2 AM IST
- Recovery Time Objective (RTO): 4 hours
- Recovery Point Objective (RPO): 24 hours

## 10.4 Scalability
- Horizontal scaling via Docker
- Database connection pooling
- Redis caching for frequent queries
- CDN for static assets (future)

## 10.5 Compliance
- DPDP Act 2023 (India)
- Data residency in India
- Right to erasure support
- Consent management
- Data export capability

## 10.6 Testing
- Backend unit test coverage: ≥80%
- Frontend unit test coverage: ≥60%
- Integration tests for critical paths
- E2E tests for user flows
- Compliance tests for all calculations

---

# ═══════════════════════════════════════════════════════════════════════════════
# PART 11: ACCEPTANCE CRITERIA
# ═══════════════════════════════════════════════════════════════════════════════

## Task Complete Checklist
- [ ] Code written and compiles
- [ ] Unit tests pass
- [ ] No linting errors
- [ ] API documentation updated
- [ ] Database migration created (if needed)

## Module Complete Checklist
- [ ] All endpoints functional
- [ ] All screens rendering
- [ ] Test coverage ≥80%
- [ ] No critical bugs
- [ ] Performance targets met

## Project Complete Checklist
- [ ] All 23 modules complete
- [ ] All 267 endpoints working
- [ ] All 68 screens functional
- [ ] All AI features operational
- [ ] All compliance calculations correct (verified with test cases)
- [ ] Performance: API <500ms, page load <3s
- [ ] Security audit passed
- [ ] Production at portal.ganakys.com
- [ ] CA verification passed

---

# ═══════════════════════════════════════════════════════════════════════════════
# APPENDIX A: ENUMERATION VALUES
# ═══════════════════════════════════════════════════════════════════════════════

```sql
-- User roles
CREATE TYPE user_role AS ENUM ('admin', 'hr', 'accountant', 'employee', 'external_ca');

-- Employee status
CREATE TYPE employee_status AS ENUM ('active', 'inactive', 'terminated', 'on_notice');

-- Onboarding status
CREATE TYPE onboarding_status AS ENUM ('in_progress', 'submitted', 'approved', 'rejected', 'changes_requested');

-- Leave status
CREATE TYPE leave_status AS ENUM ('pending', 'approved', 'rejected', 'cancelled');

-- Timesheet status
CREATE TYPE timesheet_status AS ENUM ('draft', 'submitted', 'approved', 'rejected');

-- Payroll status
CREATE TYPE payroll_status AS ENUM ('draft', 'processing', 'processed', 'finalized');

-- Invoice status
CREATE TYPE invoice_status AS ENUM ('draft', 'sent', 'partially_paid', 'paid', 'overdue', 'cancelled');

-- Bill status
CREATE TYPE bill_status AS ENUM ('draft', 'pending', 'partially_paid', 'paid', 'cancelled');

-- Project status
CREATE TYPE project_status AS ENUM ('planning', 'active', 'on_hold', 'completed', 'cancelled');

-- Task status
CREATE TYPE task_status AS ENUM ('todo', 'in_progress', 'review', 'done');

-- Lead status
CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost');
```

---

# ═══════════════════════════════════════════════════════════════════════════════
# APPENDIX B: SAMPLE DATA FOR TESTING
# ═══════════════════════════════════════════════════════════════════════════════

## Company
```json
{
  "name": "Ganakys Codilla Apps (OPC) Private Limited",
  "cin": "U72900KA2024OPC188083",
  "pan": "AAFCG1234A",
  "gstin": "29AAFCG1234A1Z5",
  "address": "Bangalore, Karnataka 560001",
  "email": "contact@ganakys.com",
  "phone": "+91-9876543210",
  "pf_establishment_code": "KABAL0012345000",
  "esi_code": "53001234567890123"
}
```

## Test Employees
```json
[
  {
    "employee_code": "GCA-2026-0001",
    "name": "Jineesh TS",
    "role": "admin",
    "department": "Management",
    "designation": "Founder & CEO",
    "ctc": 1200000,
    "basic": 40000
  },
  {
    "employee_code": "GCA-2026-0002",
    "name": "Test Employee",
    "role": "employee",
    "department": "Engineering",
    "designation": "Software Developer",
    "ctc": 600000,
    "basic": 20000
  }
]
```

---

**END OF COMPLETE REQUIREMENTS DOCUMENT**

*This document contains everything needed for autonomous development by the 147-agent army.*
