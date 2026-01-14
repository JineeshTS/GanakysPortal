# GANAPORTAL MASTER DELIVERY PLAN
## Coordinated 155-Agent Army Execution

**Version:** 1.0
**Date:** January 2026
**Source of Truth:** `/var/ganaportal/docs/REQUIREMENTS-V4-FINAL.md` (2,390 lines)

---

# CRITICAL: SINGLE SOURCE OF TRUTH

```
ALL AGENTS MUST USE: /var/ganaportal/docs/REQUIREMENTS-V4-FINAL.md

DO NOT USE: /var/ganaportal/docs/REQUIREMENTS.md (incomplete - 1,080 lines only)
```

---

# PHASE 0: COMMAND & CONTROL INITIALIZATION

## 0.1 Command Chain Activation

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CMD-001: SUPREME ORCHESTRATOR                     │
│                    (Master Controller - Always Active)               │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CMD-002: PHASE CONTROLLER                         │
│                    (Manages Phase Transitions)                       │
└─────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    CMD-003: CONFLICT RESOLVER                        │
│                    (Handles Agent Conflicts)                         │
└─────────────────────────────────────────────────────────────────────┘
```

## 0.2 Agent Communication Protocol

All agents communicate via:
- **Input:** JSON files in `/var/ganaportal/artifacts/{agent_category}/`
- **Output:** JSON files in `/var/ganaportal/artifacts/{agent_category}/`
- **Status:** `/var/ganaportal/status/{agent_id}.json`
- **Logs:** `/var/ganaportal/logs/{agent_id}.log`

---

# PHASE 1: REQUIREMENTS ANALYSIS (REQ-001 to REQ-012)

## Execution Order (Sequential)

```
Step 1.1: REQ-001 (Requirements Parser)
         Input: /var/ganaportal/docs/REQUIREMENTS-V4-FINAL.md
         Output: /var/ganaportal/artifacts/requirements/parsed_requirements.json

Step 1.2: REQ-002 (Stakeholder Analyzer)
         Input: parsed_requirements.json
         Output: stakeholder_analysis.json

Step 1.3: REQ-003 (Scope Definer)
         Input: parsed_requirements.json + stakeholder_analysis.json
         Output: scope_definition.json

Step 1.4: REQ-004 (Functional Requirements) ─┬─ PARALLEL
Step 1.5: REQ-005 (Non-Functional Requirements) ─┘
         Input: scope_definition.json
         Output: functional_requirements.json, nfr_requirements.json

Step 1.6: REQ-006 (User Story Writer)
         Input: functional_requirements.json
         Output: user_stories.json

Step 1.7: REQ-007 (Acceptance Criteria Writer)
         Input: user_stories.json
         Output: acceptance_criteria.json

Step 1.8: REQ-008 (India Compliance Analyst) ─┬─ PARALLEL
Step 1.9: REQ-009 (Integration Analyst) ─────┤
Step 1.10: REQ-010 (Data Entity Analyst) ────┘
         Output: compliance_requirements.json, integration_specs.json, data_entities.json

Step 1.11: REQ-011 (Risk Assessor)
         Input: All above outputs
         Output: risk_assessment.json

Step 1.12: REQ-012 (Gap Analyzer)
         Input: All above outputs
         Output: gap_analysis.json
```

## Phase 1 Exit Criteria
- [ ] All 12 REQ agents completed
- [ ] Requirements parsed into structured JSON
- [ ] User stories created for all 23 modules
- [ ] India compliance requirements documented
- [ ] Risk assessment completed

---

# PHASE 2: WORK BREAKDOWN STRUCTURE (WBS-001 to WBS-010)

## Execution Order (Sequential)

```
Step 2.1: WBS-001 (Phase Decomposer)
         Input: gap_analysis.json + user_stories.json
         Output: /var/ganaportal/wbs/phases.json

Step 2.2: WBS-002 (Epic Creator)
         Input: phases.json
         Output: epics.json

Step 2.3: WBS-003 (Feature Decomposer)
         Input: epics.json
         Output: features.json

Step 2.4: WBS-004 (Story Writer)
         Input: features.json
         Output: stories.json

Step 2.5: WBS-005 (Task Atomizer) ← CRITICAL
         Input: stories.json
         Output: tasks.json (ALL tasks 4-8 hours)

Step 2.6: WBS-006 (Task Estimator)
         Input: tasks.json
         Output: estimated_tasks.json

Step 2.7: WBS-007 (Dependency Mapper)
         Input: estimated_tasks.json
         Output: task_dependencies.json

Step 2.8: WBS-008 (Critical Path Calculator)
         Input: task_dependencies.json
         Output: critical_path.json

Step 2.9: WBS-009 (Resource Allocator)
         Input: critical_path.json + agent_capabilities.json
         Output: resource_allocation.json (Maps tasks to agents)

Step 2.10: WBS-010 (WBS Validator)
         Input: All WBS outputs
         Output: validated_wbs.json
```

## Phase 2 Exit Criteria
- [ ] All tasks broken into 4-8 hour units
- [ ] Dependencies mapped
- [ ] Critical path identified
- [ ] Each task assigned to specific agent
- [ ] Total estimate calculated

---

# PHASE 3: ARCHITECTURE DESIGN (ARCH-001 to ARCH-015)

## Execution Order (Parallel Groups)

```
GROUP 3A (Core Architecture) - SEQUENTIAL:
Step 3.1: ARCH-001 (System Architect)
         Output: system_architecture.json + diagrams

Step 3.2: ARCH-002 (Database Architect)
         Input: data_entities.json + REQUIREMENTS-V4-FINAL.md (Part 7)
         Output: database_schema.sql (127 tables)

Step 3.3: ARCH-003 (API Architect)
         Input: functional_requirements.json + REQUIREMENTS-V4-FINAL.md (Part 8)
         Output: api_specification.yaml (267 endpoints)

GROUP 3B (Security & AI) - PARALLEL:
Step 3.4: ARCH-004 (Security Architect)
         Output: security_architecture.json

Step 3.5: ARCH-005 (AI/ML Architect)
         Input: REQUIREMENTS-V4-FINAL.md (Part 4)
         Output: ai_architecture.json

GROUP 3C (Frontend) - PARALLEL:
Step 3.6: ARCH-007 (Frontend Architect)
         Output: frontend_architecture.json

Step 3.7: ARCH-008 (Component Architect)
         Input: REQUIREMENTS-V4-FINAL.md (Part 9)
         Output: component_library.json (68 screens)

GROUP 3D (Infrastructure) - PARALLEL:
Step 3.8: ARCH-006 (Integration Architect)
         Output: integration_architecture.json

Step 3.9: ARCH-011 (Infrastructure Architect)
         Output: infrastructure_architecture.json

Step 3.10: ARCH-012 (CI/CD Architect)
         Output: cicd_pipeline.yaml

Step 3.11: ARCH-013 (Monitoring Architect)
         Output: monitoring_setup.json

GROUP 3E (Quality) - SEQUENTIAL:
Step 3.12: ARCH-009 (Performance Architect)
         Output: performance_requirements.json

Step 3.13: ARCH-010 (Scalability Architect)
         Output: scalability_plan.json

Step 3.14: ARCH-014 (Compliance Architect)
         Input: REQUIREMENTS-V4-FINAL.md (Part 6)
         Output: compliance_architecture.json

Step 3.15: ARCH-015 (Data Flow Architect)
         Output: data_flow_diagrams.json
```

## Phase 3 Exit Criteria
- [ ] Database schema with 127 tables
- [ ] API spec with 267 endpoints
- [ ] Component library for 68 screens
- [ ] Security architecture approved
- [ ] AI fallback chain designed
- [ ] CI/CD pipeline defined

---

# PHASE 4: BACKEND DEVELOPMENT (BE-001 to BE-043)

## Execution Order

### SPRINT 4.1: Core Infrastructure (Week 1)

```
SEQUENTIAL:
BE-001 (Backend Core Setup) → BE-002 (Database Migration) → BE-003 (Auth Agent)

THEN PARALLEL:
BE-004 (User Agent)
BE-036 (Email Service)
BE-040 (Notification Agent)
BE-041 (Scheduler Agent)
BE-042 (File Storage)
```

### SPRINT 4.2: Employee & Documents (Week 2)

```
PARALLEL:
BE-005 (Employee Agent)
BE-006 (Document Agent)

THEN:
BE-039 (Audit Trail Agent)
```

### SPRINT 4.3: Leave & Timesheet (Week 3)

```
PARALLEL:
BE-007 (Leave Agent)
BE-008 (Timesheet Agent)
```

### SPRINT 4.4: Payroll Engine (Week 4) - CRITICAL

```
SEQUENTIAL (India Compliance - MUST BE EXACT):
BE-009 (Salary Agent)
BE-010 (Tax Declaration Agent)
BE-011 (Payroll Agent) ← Master Orchestrator
  ├── BE-013 (PF Calculator) - 12% + 8.33% EPS capped at 1250
  ├── BE-014 (ESI Calculator) - 0.75% + 3.25%, threshold 21000
  ├── BE-015 (TDS Calculator) - New/Old regime with slabs
  └── BE-016 (PT Calculator) - Karnataka Rs.200/300

BE-012 (Payslip Agent)
BE-017 (Form 16 Agent)
BE-018 (Statutory Filing Agent)
```

### SPRINT 4.5: Accounting Core (Week 5)

```
SEQUENTIAL:
BE-019 (Account Agent) → BE-020 (Journal Agent) → BE-021 (Currency Agent)
```

### SPRINT 4.6: AR/AP (Week 6)

```
PARALLEL:
BE-022 (Customer Agent) + BE-023 (Invoice Agent)
BE-024 (Vendor Agent) + BE-025 (Bill Agent)

THEN:
BE-026 (Payment Agent)
```

### SPRINT 4.7: Banking & GST (Week 7)

```
PARALLEL:
BE-027 (Bank Agent) + BE-028 (Reconciliation Agent)
BE-029 (GST Agent) ← GSTR-1, GSTR-3B, ITC
```

### SPRINT 4.8: CRM & Projects (Week 8)

```
PARALLEL:
BE-031 (CRM Agent)
BE-032 (Project Agent) + BE-033 (Task Agent)
BE-034 (Quote Agent)
BE-035 (Asset Agent)
```

### SPRINT 4.9: Reports & AI (Week 9)

```
BE-030 (Report Agent)
BE-037 (PDF Generation Agent)
BE-038 (Excel Export Agent)
BE-043 (Backup Agent)
```

## Phase 4 Exit Criteria
- [ ] All 43 backend agents completed
- [ ] 267 API endpoints functional
- [ ] 127 database tables created
- [ ] All India compliance calculations verified
- [ ] Unit tests ≥80% coverage

---

# PHASE 5: FRONTEND DEVELOPMENT (FE-001 to FE-035)

## Execution Order

### SPRINT 5.1: Core Setup (Week 1)

```
SEQUENTIAL:
FE-001 (Frontend Core Setup) → FE-002 (Design System) → FE-003 (Layout Agent)
```

### SPRINT 5.2: Auth & Dashboard (Week 1-2)

```
PARALLEL:
FE-004 (Auth Pages)
FE-005 (Dashboard Agent) - 5 role-based dashboards
```

### SPRINT 5.3: Employee Module (Week 2)

```
SEQUENTIAL:
FE-006 (Employee List) → FE-007 (Employee Form) → FE-008 (Document Browser)
FE-009 (Onboarding UI) - 8-step wizard
```

### SPRINT 5.4: Leave & Timesheet (Week 3)

```
PARALLEL:
FE-010 (Leave Dashboard) + FE-011 (Leave Form)
FE-012 (Timesheet Grid)
```

### SPRINT 5.5: Payroll & Statutory (Week 4)

```
SEQUENTIAL:
FE-013 (Payroll Dashboard) → FE-014 (Payslip Viewer) → FE-015 (Tax Declaration)
FE-016 (Statutory UI) - PF/ESI/TDS forms
```

### SPRINT 5.6: Accounting (Week 5)

```
PARALLEL:
FE-017 (COA Agent)
FE-018 (Journal Form)
```

### SPRINT 5.7: AR/AP (Week 6)

```
PARALLEL:
FE-019 (Invoice List) + FE-020 (Invoice Form)
FE-021 (Bill List) + FE-022 (Bill Form)
FE-023 (Payment UI)
```

### SPRINT 5.8: Banking & GST (Week 7)

```
PARALLEL:
FE-024 (Bank Recon)
FE-025 (GST UI) - GSTR-1, GSTR-3B
FE-026 (Report UI)
```

### SPRINT 5.9: CRM & Projects (Week 8)

```
PARALLEL:
FE-027 (CRM Pipeline) + FE-028 (Lead Form)
FE-029 (Project List) + FE-030 (Task Board)
FE-031 (Quote UI)
FE-032 (Asset UI)
```

### SPRINT 5.10: Settings & CA Portal (Week 9)

```
FE-033 (Settings Agent)
FE-034 (CA Portal) - External CA read-only access
FE-035 (Table Component) - Reusable data tables
```

## Phase 5 Exit Criteria
- [ ] All 35 frontend agents completed
- [ ] 68 screens functional
- [ ] All 5 role-based dashboards working
- [ ] Mobile responsive design
- [ ] Unit tests ≥60% coverage

---

# PHASE 6: AI INTEGRATION (AI-001 to AI-012)

## Execution Order

### SPRINT 6.1: Core AI (Week 1)

```
SEQUENTIAL:
AI-001 (AI Service Agent) ← Fallback chain: Claude → Gemini → GPT-4 → Together
AI-004 (Confidence Scorer) ← Thresholds: ≥95% auto, 70-94% review, <70% manual
```

### SPRINT 6.2: Document AI (Week 2)

```
PARALLEL:
AI-002 (Document Processor) - OCR, ID extraction, invoice extraction
AI-003 (Categorizer) - Transaction categorization, GL mapping
```

### SPRINT 6.3: Query & Chat (Week 3)

```
PARALLEL:
AI-005 (NL Query Agent) - Natural language to SQL/actions
AI-006 (Chat Interface)
```

### SPRINT 6.4: Intelligence (Week 4)

```
PARALLEL:
AI-007 (Daily Briefing) - Morning digest
AI-008 (Pattern Learner) - Learn from corrections
AI-009 (Anomaly Detector) - Flag unusual transactions
AI-010 (Suggestion Agent) - Smart recommendations
```

### SPRINT 6.5: Automation (Week 5)

```
SEQUENTIAL:
AI-011 (Auto-Action Agent) ← Execute high-confidence actions
AI-012 (AI Queue Agent) ← Queue low-confidence for review
```

## Phase 6 Exit Criteria
- [ ] All 12 AI agents completed
- [ ] Fallback chain functional (4 providers)
- [ ] Document extraction working
- [ ] 95%+ categorization accuracy
- [ ] Daily briefing generating

---

# PHASE 7: TESTING (TEST-001 to TEST-012)

## Execution Order

### SPRINT 7.1: Test Strategy (Week 1)

```
TEST-001 (Test Strategy Agent)
TEST-011 (Test Data Agent) - Generate India-specific test data
```

### SPRINT 7.2: Unit Tests (Week 2-3)

```
PARALLEL:
TEST-002 (Backend Unit Test) - pytest, ≥80% coverage
TEST-003 (Frontend Unit Test) - Vitest, ≥60% coverage
```

### SPRINT 7.3: Integration & E2E (Week 4)

```
SEQUENTIAL:
TEST-004 (Integration Test) → TEST-005 (E2E Test - Playwright)
```

### SPRINT 7.4: Compliance Tests (Week 5) - CRITICAL

```
TEST-008 (Compliance Test Agent) ← MUST VERIFY ALL CALCULATIONS:
  - PF: 12% employee, 8.33% EPS capped at 1250
  - ESI: 0.75% employee, 3.25% employer, threshold 21000
  - PT: Karnataka Rs.200/month, Rs.300 February
  - TDS: New regime slabs (0-3L: 0%, 3-7L: 5%, etc.)
  - GST: CGST/SGST 9% each or IGST 18%
```

### SPRINT 7.5: Quality & Performance (Week 6)

```
PARALLEL:
TEST-006 (Performance Test) - API <500ms, page <3s
TEST-007 (Security Test)
TEST-009 (Regression Test)
TEST-010 (UAT Test)
```

### SPRINT 7.6: Coverage Report (Week 7)

```
TEST-012 (Coverage Reporter) - Generate final coverage report
```

## Phase 7 Exit Criteria
- [ ] Backend coverage ≥80%
- [ ] Frontend coverage ≥60%
- [ ] All compliance calculations verified
- [ ] E2E tests passing
- [ ] Performance targets met

---

# PHASE 8: QUALITY ASSURANCE (QA-001 to QA-008)

## Execution Order (Parallel)

```
QA-001 (Code Review) ─────────┬─ PARALLEL
QA-002 (Security Review) ─────┤
QA-003 (Performance Review) ──┤
QA-004 (API Contract Review) ─┤
QA-005 (Database Review) ─────┤
QA-006 (UI/UX Review) ────────┤
QA-007 (Documentation Review) ┤
QA-008 (Compliance Review) ───┘ ← CA verification for India compliance
```

## Phase 8 Exit Criteria
- [ ] All code reviewed
- [ ] Security audit passed
- [ ] API contracts validated
- [ ] UI/UX approved
- [ ] CA compliance sign-off

---

# PHASE 9: DEPLOYMENT (DEP-001 to DEP-005)

## Execution Order (Sequential)

```
Step 9.1: DEP-001 (Docker Build Agent)
         Build production images

Step 9.2: DEP-002 (Migration Runner Agent)
         Run Alembic migrations

Step 9.3: DEP-003 (Nginx Config Agent)
         Configure reverse proxy, SSL

Step 9.4: DEP-004 (SSL Agent)
         Let's Encrypt certificate

Step 9.5: DEP-005 (Health Check Agent)
         Verify all services healthy
```

## Phase 9 Exit Criteria
- [ ] Docker images built
- [ ] Database migrated
- [ ] SSL configured
- [ ] Health checks passing
- [ ] portal.ganakys.com live

---

# AGENT COORDINATION RULES

## Rule 1: Input/Output Contract

Every agent MUST:
1. Read input from `/var/ganaportal/artifacts/{category}/`
2. Write output to `/var/ganaportal/artifacts/{category}/`
3. Update status in `/var/ganaportal/status/{agent_id}.json`

## Rule 2: Dependency Check

Before starting, every agent MUST:
1. Check that all dependency agents have status: `completed`
2. Validate input files exist and are valid JSON
3. Report `blocked` status if dependencies not met

## Rule 3: Requirements Reference

Every agent MUST:
1. Reference `/var/ganaportal/docs/REQUIREMENTS-V4-FINAL.md` as source of truth
2. Use exact values from requirements (no approximations)
3. Log which requirement section was used

## Rule 4: Error Handling

On error, agent MUST:
1. Set status to `failed`
2. Write error details to `/var/ganaportal/logs/{agent_id}.log`
3. Notify CMD-003 (Conflict Resolver)

## Rule 5: Completion Validation

Before marking `completed`, agent MUST:
1. Validate output against expected schema
2. Run self-tests if applicable
3. Update status with metrics (time, output size, etc.)

---

# DELIVERY METRICS

## Build Statistics (from Requirements)

| Metric | Target | Source |
|--------|--------|--------|
| Modules | 23 | REQUIREMENTS-V4-FINAL.md Part 5 |
| Database Tables | 127 | REQUIREMENTS-V4-FINAL.md Part 7 |
| API Endpoints | 267 | REQUIREMENTS-V4-FINAL.md Part 8 |
| Frontend Screens | 68 | REQUIREMENTS-V4-FINAL.md Part 9 |
| User Roles | 5 | REQUIREMENTS-V4-FINAL.md Part 3 |
| Compliance Rules | 47 | REQUIREMENTS-V4-FINAL.md Part 6 |

## Quality Targets

| Metric | Target |
|--------|--------|
| Backend Test Coverage | ≥80% |
| Frontend Test Coverage | ≥60% |
| API Response Time (p95) | <500ms |
| Page Load Time | <3s |
| Uptime | 99.5% |

---

# STATUS TRACKING

Create status file for each agent:

```json
// /var/ganaportal/status/BE-013.json
{
  "agent_id": "BE-013",
  "agent_name": "PF Calculator Agent",
  "phase": 4,
  "status": "completed",
  "started_at": "2026-01-08T10:00:00Z",
  "completed_at": "2026-01-08T14:00:00Z",
  "duration_hours": 4,
  "dependencies": ["BE-011"],
  "dependents": ["BE-011", "TEST-008"],
  "outputs": [
    "/var/ganaportal/src/backend/app/services/payroll/pf.py"
  ],
  "tests_passed": true,
  "coverage": 95.2,
  "requirements_used": [
    "REQUIREMENTS-V4-FINAL.md Section 6.1"
  ]
}
```

---

# EXECUTION COMMAND

To start the coordinated build:

```bash
# Initialize command chain
CMD-001 --init --source=/var/ganaportal/docs/REQUIREMENTS-V4-FINAL.md

# Start Phase 1
CMD-002 --phase=1 --agents=REQ-001,REQ-002,...,REQ-012

# Continue through phases
CMD-002 --phase=2 --agents=WBS-001,...,WBS-010
CMD-002 --phase=3 --agents=ARCH-001,...,ARCH-015
CMD-002 --phase=4 --agents=BE-001,...,BE-043
CMD-002 --phase=5 --agents=FE-001,...,FE-035
CMD-002 --phase=6 --agents=AI-001,...,AI-012
CMD-002 --phase=7 --agents=TEST-001,...,TEST-012
CMD-002 --phase=8 --agents=QA-001,...,QA-008
CMD-002 --phase=9 --agents=DEP-001,...,DEP-005
```

---

**END OF MASTER DELIVERY PLAN**

*This plan ensures all 155 agents work in coordination using REQUIREMENTS-V4-FINAL.md as the single source of truth.*
