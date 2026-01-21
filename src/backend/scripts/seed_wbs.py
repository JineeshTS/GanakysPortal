"""
Seed WBS Data
Populates initial phases, modules, quality gates, and agent configurations
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os

# Database URL - must be set via environment variable (no hardcoded fallback for security)
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable must be set")

# ============================================================================
# Seed Data
# ============================================================================

PHASES = [
    {"phase_code": "P01", "name": "Discovery & Analysis", "start_week": 1, "end_week": 2},
    {"phase_code": "P02", "name": "Architecture & Design", "start_week": 2, "end_week": 4},
    {"phase_code": "P03", "name": "Infrastructure Setup", "start_week": 4, "end_week": 5},
    {"phase_code": "P04", "name": "Backend Development", "start_week": 5, "end_week": 20},
    {"phase_code": "P05", "name": "Frontend Development", "start_week": 10, "end_week": 24},
    {"phase_code": "P06", "name": "AI Feature Integration", "start_week": 18, "end_week": 28},
    {"phase_code": "P07", "name": "Integration & APIs", "start_week": 24, "end_week": 32},
    {"phase_code": "P08", "name": "Testing & QA", "start_week": 28, "end_week": 36},
    {"phase_code": "P09", "name": "Security & Compliance", "start_week": 32, "end_week": 38},
    {"phase_code": "P10", "name": "Documentation", "start_week": 34, "end_week": 40},
    {"phase_code": "P11", "name": "Deployment & Launch", "start_week": 40, "end_week": 44},
    {"phase_code": "P12", "name": "Stabilization", "start_week": 44, "end_week": 48},
]

MODULES = [
    {"module_code": "MOD-01", "name": "Subscription & Billing", "priority": 1, "new_tables": 8, "new_endpoints": 25, "new_pages": 8},
    {"module_code": "MOD-02", "name": "Super Admin Portal", "priority": 2, "new_tables": 5, "new_endpoints": 20, "new_pages": 12},
    {"module_code": "MOD-03", "name": "Digital DoA & Approvals", "priority": 3, "new_tables": 7, "new_endpoints": 22, "new_pages": 6},
    {"module_code": "MOD-04", "name": "Digital Signatures", "priority": 4, "new_tables": 12, "new_endpoints": 28, "new_pages": 8},
    {"module_code": "MOD-05", "name": "Security Architecture", "priority": 5, "new_tables": 8, "new_endpoints": 18, "new_pages": 5},
    {"module_code": "MOD-06", "name": "AI Anomaly Detection", "priority": 6, "new_tables": 6, "new_endpoints": 15, "new_pages": 4},
    {"module_code": "MOD-07", "name": "ESG Management", "priority": 7, "new_tables": 8, "new_endpoints": 20, "new_pages": 6},
    {"module_code": "MOD-08", "name": "HSSEQ Management", "priority": 8, "new_tables": 10, "new_endpoints": 25, "new_pages": 8},
    {"module_code": "MOD-09", "name": "CSR Tracking", "priority": 9, "new_tables": 5, "new_endpoints": 12, "new_pages": 4},
    {"module_code": "MOD-10", "name": "Legal Case Management", "priority": 10, "new_tables": 8, "new_endpoints": 18, "new_pages": 6},
    {"module_code": "MOD-11", "name": "Compliance Master", "priority": 11, "new_tables": 10, "new_endpoints": 22, "new_pages": 7},
    {"module_code": "MOD-12", "name": "Manufacturing", "priority": 12, "new_tables": 12, "new_endpoints": 30, "new_pages": 10},
    {"module_code": "MOD-13", "name": "Supply Chain Advanced", "priority": 13, "new_tables": 10, "new_endpoints": 28, "new_pages": 9},
    {"module_code": "MOD-14", "name": "E-commerce & POS", "priority": 14, "new_tables": 8, "new_endpoints": 22, "new_pages": 8},
    {"module_code": "MOD-15", "name": "Advanced Analytics", "priority": 15, "new_tables": 4, "new_endpoints": 15, "new_pages": 6},
    {"module_code": "MOD-16", "name": "Workflow Engine", "priority": 16, "new_tables": 5, "new_endpoints": 18, "new_pages": 5},
    {"module_code": "MOD-17", "name": "Integration Platform", "priority": 17, "new_tables": 4, "new_endpoints": 20, "new_pages": 5},
    {"module_code": "MOD-18", "name": "Mobile Apps", "priority": 18, "new_tables": 2, "new_endpoints": 15, "new_pages": 20},
    {"module_code": "MOD-19", "name": "Multi-Currency", "priority": 19, "new_tables": 3, "new_endpoints": 12, "new_pages": 4},
    {"module_code": "MOD-20", "name": "Fixed Assets", "priority": 20, "new_tables": 5, "new_endpoints": 15, "new_pages": 5},
    {"module_code": "MOD-21", "name": "Expense Management", "priority": 21, "new_tables": 4, "new_endpoints": 14, "new_pages": 5},
]

QUALITY_GATES = [
    {"gate_code": "G1", "name": "Requirements Complete", "is_blocking": True,
     "criteria": ["All 21 modules documented", "Gap analysis complete", "Compliance rules extracted"]},
    {"gate_code": "G2", "name": "Architecture Approved", "is_blocking": True,
     "criteria": ["Database schema designed", "API contracts defined", "Security architecture reviewed"]},
    {"gate_code": "G3", "name": "Infrastructure Ready", "is_blocking": True,
     "criteria": ["Docker containers running", "CI/CD pipeline working", "Dev/staging environments ready"]},
    {"gate_code": "G4", "name": "Backend Complete", "is_blocking": True,
     "criteria": ["All APIs responding", "80% test coverage", "No critical bugs"]},
    {"gate_code": "G5", "name": "Frontend Complete", "is_blocking": True,
     "criteria": ["All pages functional", "Responsive design verified", "Accessibility checked"]},
    {"gate_code": "G6", "name": "AI Integration Done", "is_blocking": True,
     "criteria": ["Fallback chain working", "Confidence thresholds set", "AI features tested"]},
    {"gate_code": "G7", "name": "Testing Complete", "is_blocking": True,
     "criteria": ["All unit tests passing", "Integration tests passing", "E2E tests passing"]},
    {"gate_code": "G8", "name": "Security Verified", "is_blocking": True,
     "criteria": ["Penetration test passed", "Vulnerability scan clean", "Compliance audit passed"]},
    {"gate_code": "G9", "name": "Documentation Done", "is_blocking": False,
     "criteria": ["API docs complete", "User guides written", "Admin guides written"]},
    {"gate_code": "G10", "name": "Production Ready", "is_blocking": True,
     "criteria": ["Health checks passing", "Monitoring configured", "Backup/recovery tested"]},
]

AGENT_CONFIGS = [
    {
        "agent_code": "DB-AGENT",
        "name": "Database Agent",
        "description": "Handles all database-related tasks including SQLAlchemy model creation, Alembic migrations, and schema optimization",
        "purpose": "SQLAlchemy models, Alembic migrations, schema design, index optimization",
        "triggers": ["Creating/modifying database tables", "Generating migrations", "Index optimization", "Adding relationships"],
        "output_types": ["Model files (.py)", "Migration scripts", "Schema documentation"],
        "pattern_files": ["backend/app/models/base.py", "backend/app/models/employee.py"],
        "system_prompt": """You are the Database Agent (DB-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Create SQLAlchemy 2.0 models with proper type hints
2. Generate Alembic migrations with rollback support
3. Implement soft delete patterns (deleted_at column)
4. Add audit columns (created_at, updated_at, created_by, updated_by)
5. Design indexes for query optimization
6. Implement row-level security patterns (company_id isolation)

Always follow existing patterns in the codebase. Use UUID primary keys, implement tenant isolation via company_id, and ensure all migrations are reversible."""
    },
    {
        "agent_code": "API-AGENT",
        "name": "API Agent",
        "description": "Creates FastAPI endpoints, Pydantic schemas, and OpenAPI documentation",
        "purpose": "FastAPI endpoints, Pydantic schemas, OpenAPI docs, request validation",
        "triggers": ["Creating REST endpoints", "Defining request/response schemas", "API documentation", "Pagination implementation"],
        "output_types": ["Router files (.py)", "Schema files (.py)", "OpenAPI specs"],
        "pattern_files": ["backend/app/api/v1/endpoints/employees.py", "backend/app/schemas/recruitment.py"],
        "system_prompt": """You are the API Agent (API-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Create FastAPI router modules with proper dependencies
2. Define Pydantic v2 schemas (Base, Create, Update, Response patterns)
3. Implement standardized response formats
4. Add OpenAPI documentation with examples
5. Configure authentication dependencies
6. Implement cursor-based pagination and filtering

Use async/await patterns, proper HTTP status codes, and follow RESTful conventions."""
    },
    {
        "agent_code": "SVC-AGENT",
        "name": "Service Agent",
        "description": "Implements business logic, compliance calculations, and complex workflows",
        "purpose": "Business logic, compliance calculations (PF/ESI/TDS/PT/GST), validation rules",
        "triggers": ["Implementing business rules", "Compliance calculations", "Complex workflows", "Validation logic"],
        "output_types": ["Service classes (.py)", "Calculator modules", "Utility functions"],
        "pattern_files": ["backend/app/services/banking_service.py", "backend/app/services/leave_service.py"],
        "system_prompt": """You are the Service Agent (SVC-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Create service classes with dependency injection patterns
2. Implement India compliance calculations (PF, ESI, TDS, PT, GST)
3. Handle complex business workflows
4. Implement validation logic
5. Create utility functions
6. Use async patterns for I/O operations

Critical compliance formulas must be exact:
- PF: Employee 12%, Employer EPS 8.33% (max 1250), EPF = 12% - EPS
- ESI: Employee 0.75%, Employer 3.25% (if gross <= 21000)
- TDS New Regime: 0-3L 0%, 3L-7L 5%, 7L-10L 10%, 10L-12L 15%, 12L-15L 20%, >15L 30% + 4% cess"""
    },
    {
        "agent_code": "PAGE-AGENT",
        "name": "Page Agent",
        "description": "Builds Next.js 14 pages with App Router, layouts, and data fetching",
        "purpose": "Next.js pages, layouts, server/client components, data fetching with TanStack Query",
        "triggers": ["Creating new routes/pages", "Page layouts", "Server components", "Loading/error states"],
        "output_types": ["page.tsx", "layout.tsx", "loading.tsx", "error.tsx"],
        "pattern_files": ["frontend/src/app/(dashboard)/employees/page.tsx"],
        "system_prompt": """You are the Page Agent (PAGE-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Create Next.js 14 App Router pages
2. Implement server components where applicable
3. Set up TanStack Query for data fetching
4. Implement loading and error states
5. Create page-specific layouts
6. Implement role-based access controls in UI

Use TypeScript strict mode, follow existing component patterns, and ensure responsive design."""
    },
    {
        "agent_code": "COMP-AGENT",
        "name": "Component Agent",
        "description": "Creates reusable UI components using shadcn/ui, Tailwind CSS, and React patterns",
        "purpose": "Reusable components, forms with validation, data tables, charts",
        "triggers": ["Creating shadcn/ui components", "Form components", "Data tables", "Chart components"],
        "output_types": ["Component files (.tsx)", "Hook files", "Utility functions"],
        "pattern_files": ["frontend/src/components/ui/button.tsx", "frontend/src/components/layout/data-table.tsx"],
        "system_prompt": """You are the Component Agent (COMP-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Create shadcn/ui based components
2. Implement React Hook Form + Zod validation patterns
3. Build TanStack Table implementations
4. Create Recharts-based chart components
5. Ensure WCAG accessibility compliance
6. Implement responsive design patterns

Follow existing component patterns, use proper TypeScript types, and ensure accessibility."""
    },
    {
        "agent_code": "TEST-AGENT",
        "name": "Test Agent",
        "description": "Creates comprehensive tests including unit, integration, and E2E tests",
        "purpose": "Unit tests (pytest/Jest), integration tests, E2E tests (Playwright)",
        "triggers": ["Writing pytest tests", "Jest/Vitest tests", "Playwright E2E tests", "Compliance calculation tests"],
        "output_types": ["Test files", "Test fixtures", "Coverage reports"],
        "pattern_files": ["backend/tests/unit/test_models.py", "backend/tests/compliance/test_tds_calculator.py"],
        "system_prompt": """You are the Test Agent (TEST-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Write pytest tests for backend services (target 80% coverage)
2. Write Jest + React Testing Library tests for frontend
3. Create Playwright E2E tests for critical paths
4. Test India compliance calculations with exact values
5. Generate test fixtures and factories
6. Test edge cases (ESI 21000 threshold, PF 15000, February PT adjustment)

All compliance calculations must have explicit test cases with known values."""
    },
    {
        "agent_code": "DOC-AGENT",
        "name": "Documentation Agent",
        "description": "Creates and maintains project documentation",
        "purpose": "API documentation, user guides, technical specs, architecture decisions",
        "triggers": ["API documentation", "User guides", "Technical specs", "Architecture decisions (ADRs)"],
        "output_types": ["Markdown files", "OpenAPI specs", "Diagrams"],
        "pattern_files": ["FEATURES.md", "ARCHITECTURE.md"],
        "system_prompt": """You are the Documentation Agent (DOC-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Generate OpenAPI/Swagger documentation
2. Write user guides for each module
3. Document compliance rules and calculations
4. Create developer onboarding guides
5. Maintain CHANGELOG.md
6. Document architecture decisions (ADRs)

Use clear, concise language. Include examples and screenshots where helpful."""
    },
    {
        "agent_code": "INT-AGENT",
        "name": "Integration Agent",
        "description": "Handles external service integrations",
        "purpose": "External APIs, webhooks, payment gateways, email/SMS services",
        "triggers": ["External API integration", "Webhook handlers", "Payment/SMS/Email services", "Government portal integration"],
        "output_types": ["Integration code", "API clients", "Webhook handlers"],
        "pattern_files": ["backend/app/services/ai/ai_service.py"],
        "system_prompt": """You are the Integration Agent (INT-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Implement AI provider fallback chain (Claude -> Gemini -> OpenAI -> Together)
2. Set up AWS SES / SendGrid for emails
3. Configure MSG91 for SMS (DLT compliant)
4. Implement RBI API for exchange rates
5. Handle API retry logic and circuit breakers
6. Manage API key rotation and security

Implement proper error handling, retries, and fallback mechanisms."""
    },
    {
        "agent_code": "AI-AGENT",
        "name": "AI Feature Agent",
        "description": "Implements AI-powered features including document processing and intelligent automation",
        "purpose": "Document extraction, NL queries, anomaly detection, confidence scoring",
        "triggers": ["Document extraction", "NL queries", "Anomaly detection", "Pattern learning", "Confidence scoring"],
        "output_types": ["AI service code", "Prompt templates", "Model configurations"],
        "pattern_files": ["backend/app/services/ai/document_ai.py", "backend/app/services/ai/anomaly_detection.py"],
        "system_prompt": """You are the AI Feature Agent (AI-AGENT) for the Ganakys ERP project.

Your responsibilities:
1. Implement document categorization and extraction
2. Build natural language query engine
3. Create confidence scoring algorithms
4. Implement pattern learning from corrections
5. Build anomaly detection for financial data
6. Create daily briefing generation

Use confidence thresholds: 95% auto-execute, 70-94% review queue, <70% manual.
Implement fallback chain for AI providers."""
    },
]


async def seed_wbs():
    """Seed WBS tables with initial data."""
    engine = create_async_engine(DATABASE_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Seed Phases
        print("Seeding phases...")
        for phase in PHASES:
            await session.execute(text("""
                INSERT INTO wbs_phases (phase_code, name, start_week, end_week, status)
                VALUES (:phase_code, :name, :start_week, :end_week, 'pending')
                ON CONFLICT (phase_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    start_week = EXCLUDED.start_week,
                    end_week = EXCLUDED.end_week
            """), phase)

        # Seed Modules
        print("Seeding modules...")
        for module in MODULES:
            await session.execute(text("""
                INSERT INTO wbs_modules (module_code, name, priority, new_tables, new_endpoints, new_pages, status)
                VALUES (:module_code, :name, :priority, :new_tables, :new_endpoints, :new_pages, 'pending')
                ON CONFLICT (module_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    priority = EXCLUDED.priority,
                    new_tables = EXCLUDED.new_tables,
                    new_endpoints = EXCLUDED.new_endpoints,
                    new_pages = EXCLUDED.new_pages
            """), module)

        # Seed Quality Gates
        print("Seeding quality gates...")
        for gate in QUALITY_GATES:
            # Format criteria as PostgreSQL array literal for raw SQL
            criteria_items = ", ".join(f"'{c}'" for c in gate["criteria"])
            criteria_sql = f"ARRAY[{criteria_items}]"
            # Use raw SQL with array constructor
            await session.execute(text(f"""
                INSERT INTO wbs_quality_gates (gate_code, name, is_blocking, criteria, status)
                VALUES (:gate_code, :name, :is_blocking, {criteria_sql}, 'pending')
                ON CONFLICT (gate_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    is_blocking = EXCLUDED.is_blocking,
                    criteria = {criteria_sql}
            """), {"gate_code": gate["gate_code"], "name": gate["name"], "is_blocking": gate["is_blocking"]})

        # Seed Agent Configs
        print("Seeding agent configs...")
        for agent in AGENT_CONFIGS:
            # Format arrays as PostgreSQL ARRAY[] for raw SQL
            triggers_items = ", ".join(f"'{t}'" for t in agent["triggers"])
            output_types_items = ", ".join(f"'{o}'" for o in agent["output_types"])
            pattern_files_items = ", ".join(f"'{p}'" for p in agent["pattern_files"])
            triggers_sql = f"ARRAY[{triggers_items}]"
            output_types_sql = f"ARRAY[{output_types_items}]"
            pattern_files_sql = f"ARRAY[{pattern_files_items}]"
            await session.execute(text(f"""
                INSERT INTO wbs_agent_configs (agent_code, name, description, purpose, triggers, output_types, pattern_files, system_prompt, is_active)
                VALUES (:agent_code, :name, :description, :purpose, {triggers_sql}, {output_types_sql}, {pattern_files_sql}, :system_prompt, true)
                ON CONFLICT (agent_code) DO UPDATE SET
                    name = EXCLUDED.name,
                    description = EXCLUDED.description,
                    purpose = EXCLUDED.purpose,
                    triggers = {triggers_sql},
                    output_types = {output_types_sql},
                    pattern_files = {pattern_files_sql},
                    system_prompt = EXCLUDED.system_prompt
            """), {
                "agent_code": agent["agent_code"],
                "name": agent["name"],
                "description": agent["description"],
                "purpose": agent["purpose"],
                "system_prompt": agent["system_prompt"]
            })

        await session.commit()
        print("WBS seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_wbs())
