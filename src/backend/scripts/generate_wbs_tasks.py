"""
WBS Task Generator
Generates atomic tasks for the WBS framework based on modules and phases.
Creates ~1,500 tasks following the task decomposition rules.
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import os
import uuid
from typing import List, Dict, Any

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://ganaportal_user:ganaportal123@127.0.0.1:5432/ganaportal_db"
)

# ============================================================================
# Task Templates by Agent Type
# ============================================================================

# Database Agent Tasks
DB_AGENT_TASKS = [
    {"title": "Create {entity} SQLAlchemy model", "hours": 3, "complexity": "medium"},
    {"title": "Add {entity} relationships and foreign keys", "hours": 2, "complexity": "medium"},
    {"title": "Create {entity} indexes for performance", "hours": 1, "complexity": "low"},
    {"title": "Generate Alembic migration for {entity}", "hours": 2, "complexity": "medium"},
    {"title": "Add audit columns to {entity} table", "hours": 1, "complexity": "low"},
]

# API Agent Tasks
API_AGENT_TASKS = [
    {"title": "Create Pydantic schemas for {entity}", "hours": 3, "complexity": "medium"},
    {"title": "Implement GET /api/{entity} list endpoint", "hours": 4, "complexity": "medium"},
    {"title": "Implement GET /api/{entity}/{{id}} detail endpoint", "hours": 2, "complexity": "low"},
    {"title": "Implement POST /api/{entity} create endpoint", "hours": 4, "complexity": "medium"},
    {"title": "Implement PUT /api/{entity}/{{id}} update endpoint", "hours": 3, "complexity": "medium"},
    {"title": "Implement DELETE /api/{entity}/{{id}} endpoint", "hours": 2, "complexity": "low"},
    {"title": "Add pagination and filtering to {entity} list", "hours": 3, "complexity": "medium"},
    {"title": "Add search functionality to {entity} endpoint", "hours": 2, "complexity": "low"},
]

# Service Agent Tasks
SVC_AGENT_TASKS = [
    {"title": "Implement {entity} validation service", "hours": 4, "complexity": "medium"},
    {"title": "Create {entity} business logic service", "hours": 6, "complexity": "high"},
    {"title": "Implement {entity} calculation service", "hours": 5, "complexity": "high"},
    {"title": "Add {entity} notification service integration", "hours": 3, "complexity": "medium"},
    {"title": "Create {entity} audit logging service", "hours": 2, "complexity": "low"},
]

# Page Agent Tasks
PAGE_AGENT_TASKS = [
    {"title": "Create {entity} list page component", "hours": 6, "complexity": "high"},
    {"title": "Create {entity} detail view page", "hours": 5, "complexity": "medium"},
    {"title": "Create {entity} create/edit form page", "hours": 6, "complexity": "high"},
    {"title": "Implement {entity} page data fetching", "hours": 3, "complexity": "medium"},
    {"title": "Add {entity} page loading and error states", "hours": 2, "complexity": "low"},
]

# Component Agent Tasks
COMP_AGENT_TASKS = [
    {"title": "Create {entity} table component with sorting", "hours": 5, "complexity": "medium"},
    {"title": "Create {entity} form component with validation", "hours": 6, "complexity": "high"},
    {"title": "Create {entity} filter sidebar component", "hours": 4, "complexity": "medium"},
    {"title": "Create {entity} card/tile component", "hours": 3, "complexity": "medium"},
    {"title": "Create {entity} status badge component", "hours": 2, "complexity": "low"},
    {"title": "Create {entity} action dropdown component", "hours": 2, "complexity": "low"},
]

# Test Agent Tasks
TEST_AGENT_TASKS = [
    {"title": "Write unit tests for {entity} model", "hours": 3, "complexity": "medium"},
    {"title": "Write API integration tests for {entity}", "hours": 4, "complexity": "medium"},
    {"title": "Write service layer tests for {entity}", "hours": 3, "complexity": "medium"},
    {"title": "Write E2E tests for {entity} pages", "hours": 5, "complexity": "high"},
    {"title": "Add {entity} test fixtures and factories", "hours": 2, "complexity": "low"},
]

# Documentation Agent Tasks
DOC_AGENT_TASKS = [
    {"title": "Write API documentation for {entity} endpoints", "hours": 2, "complexity": "low"},
    {"title": "Create {entity} user guide documentation", "hours": 3, "complexity": "medium"},
]

# Integration Agent Tasks
INT_AGENT_TASKS = [
    {"title": "Implement {entity} external API integration", "hours": 6, "complexity": "high"},
    {"title": "Add {entity} webhook handlers", "hours": 4, "complexity": "medium"},
]

# AI Agent Tasks
AI_AGENT_TASKS = [
    {"title": "Implement AI extraction for {entity}", "hours": 6, "complexity": "high"},
    {"title": "Add intelligent suggestions for {entity}", "hours": 5, "complexity": "high"},
    {"title": "Create anomaly detection for {entity}", "hours": 6, "complexity": "critical"},
]

# ============================================================================
# Module Feature Definitions
# ============================================================================

MODULE_FEATURES = {
    "MOD-01": {  # Subscription & Billing
        "code": "SUB",
        "entities": [
            "subscription_plan", "subscription", "billing_cycle", "invoice",
            "payment", "usage_meter", "pricing_tier", "discount"
        ],
        "ai_features": ["pricing_optimizer", "churn_predictor", "usage_analyzer"]
    },
    "MOD-02": {  # Super Admin Portal
        "code": "ADMIN",
        "entities": [
            "tenant", "tenant_config", "audit_log", "system_health",
            "feature_flag", "announcement", "support_ticket"
        ],
        "ai_features": ["health_monitor", "anomaly_detector"]
    },
    "MOD-03": {  # Digital DoA & Approvals
        "code": "DOA",
        "entities": [
            "approval_matrix", "approval_workflow", "approval_request",
            "approval_history", "delegation_rule", "escalation_rule"
        ],
        "ai_features": ["approval_predictor", "bottleneck_detector"]
    },
    "MOD-04": {  # Digital Signatures
        "code": "DSIG",
        "entities": [
            "signature_template", "signature_request", "signature_field",
            "signer", "signature_audit", "certificate", "signing_session"
        ],
        "ai_features": ["signature_position_suggester", "completion_predictor"]
    },
    "MOD-05": {  # Security Architecture
        "code": "SEC",
        "entities": [
            "security_policy", "access_control", "session_manager",
            "threat_log", "security_alert", "compliance_check"
        ],
        "ai_features": ["threat_detector", "access_anomaly_detector"]
    },
    "MOD-06": {  # AI Anomaly Detection
        "code": "ANOM",
        "entities": [
            "anomaly_rule", "anomaly_event", "anomaly_alert",
            "baseline_metric", "pattern_library"
        ],
        "ai_features": ["pattern_learner", "prediction_engine", "correlation_finder"]
    },
    "MOD-07": {  # ESG Management
        "code": "ESG",
        "entities": [
            "esg_metric", "esg_target", "esg_report", "carbon_footprint",
            "sustainability_initiative", "esg_compliance"
        ],
        "ai_features": ["esg_scorer", "trend_analyzer", "compliance_checker"]
    },
    "MOD-08": {  # HSSEQ Management
        "code": "HSE",
        "entities": [
            "incident_report", "safety_inspection", "hazard_assessment",
            "safety_training", "ppe_inventory", "emergency_drill", "near_miss"
        ],
        "ai_features": ["risk_predictor", "incident_analyzer", "trend_detector"]
    },
    "MOD-09": {  # CSR Tracking
        "code": "CSR",
        "entities": [
            "csr_project", "csr_budget", "csr_beneficiary",
            "csr_report", "csr_compliance"
        ],
        "ai_features": ["impact_analyzer", "compliance_tracker"]
    },
    "MOD-10": {  # Legal Case Management
        "code": "LEGAL",
        "entities": [
            "legal_case", "case_document", "case_milestone",
            "legal_party", "hearing", "court", "legal_expense"
        ],
        "ai_features": ["outcome_predictor", "document_analyzer", "timeline_estimator"]
    },
    "MOD-11": {  # Compliance Master
        "code": "COMP",
        "entities": [
            "compliance_requirement", "compliance_task", "compliance_calendar",
            "compliance_evidence", "compliance_report", "regulatory_update"
        ],
        "ai_features": ["deadline_tracker", "gap_analyzer", "update_monitor"]
    },
    "MOD-12": {  # Manufacturing
        "code": "MFG",
        "entities": [
            "bom", "work_order", "production_line", "quality_check",
            "material_requisition", "scrap_record", "machine_maintenance"
        ],
        "ai_features": ["demand_forecaster", "quality_predictor", "maintenance_scheduler"]
    },
    "MOD-13": {  # Supply Chain Advanced
        "code": "SCM",
        "entities": [
            "purchase_forecast", "supplier_scorecard", "reorder_rule",
            "warehouse", "bin_location", "stock_transfer", "goods_receipt"
        ],
        "ai_features": ["demand_planner", "supplier_optimizer", "stock_predictor"]
    },
    "MOD-14": {  # E-commerce & POS
        "code": "ECOM",
        "entities": [
            "product_catalog", "product_variant", "shopping_cart",
            "online_order", "pos_terminal", "pos_transaction", "loyalty_point"
        ],
        "ai_features": ["recommendation_engine", "pricing_optimizer", "fraud_detector"]
    },
    "MOD-15": {  # Advanced Analytics
        "code": "ANLY",
        "entities": [
            "dashboard", "report_template", "kpi_definition",
            "data_source", "visualization", "scheduled_report"
        ],
        "ai_features": ["insight_generator", "trend_analyzer", "prediction_engine"]
    }
}

# Phase to task mapping
PHASE_TASK_COUNTS = {
    "P01": 45,   # Discovery & Analysis
    "P02": 75,   # Architecture & Design
    "P03": 35,   # Infrastructure Setup
    "P04": 420,  # Backend Development
    "P05": 380,  # Frontend Development
    "P06": 120,  # AI Feature Integration
    "P07": 95,   # Integration & APIs
    "P08": 130,  # Testing & QA
    "P09": 65,   # Security & Compliance
    "P10": 50,   # Documentation
    "P11": 45,   # Deployment & Launch
    "P12": 35,   # Stabilization
}


async def generate_tasks():
    """Generate all WBS tasks."""
    engine = create_async_engine(DATABASE_URL, echo=False)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    tasks_generated = 0
    all_tasks = []

    async with async_session() as session:
        # Get phase and module IDs
        phases_result = await session.execute(text("SELECT id, phase_code FROM wbs_phases"))
        phases = {row[1]: row[0] for row in phases_result.fetchall()}

        modules_result = await session.execute(text("SELECT id, module_code FROM wbs_modules"))
        modules = {row[1]: row[0] for row in modules_result.fetchall()}

        print(f"Found {len(phases)} phases and {len(modules)} modules")

        # Generate tasks for each module
        for module_code, module_data in MODULE_FEATURES.items():
            if module_code not in modules:
                print(f"Skipping {module_code} - not found in database")
                continue

            module_id = modules[module_code]
            feature_code = module_data["code"]
            entities = module_data["entities"]
            ai_features = module_data.get("ai_features", [])

            task_num = 1

            # Backend tasks (P04)
            if "P04" in phases:
                phase_id = phases["P04"]

                for entity in entities:
                    # DB Agent tasks
                    for template in DB_AGENT_TASKS:
                        task_id = f"P04-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "DB-AGENT",
                            "priority": "P1" if task_num <= 3 else "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

                    # API Agent tasks
                    for template in API_AGENT_TASKS:
                        task_id = f"P04-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "API-AGENT",
                            "priority": "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

                    # Service Agent tasks
                    for template in SVC_AGENT_TASKS[:3]:  # Limit to 3 per entity
                        task_id = f"P04-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "SVC-AGENT",
                            "priority": "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

            # Frontend tasks (P05)
            if "P05" in phases:
                phase_id = phases["P05"]
                task_num = 1

                for entity in entities:
                    # Page Agent tasks
                    for template in PAGE_AGENT_TASKS:
                        task_id = f"P05-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "PAGE-AGENT",
                            "priority": "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

                    # Component Agent tasks
                    for template in COMP_AGENT_TASKS[:4]:  # Limit to 4 per entity
                        task_id = f"P05-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "COMP-AGENT",
                            "priority": "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

            # AI Feature tasks (P06)
            if "P06" in phases and ai_features:
                phase_id = phases["P06"]
                task_num = 1

                for ai_feature in ai_features:
                    for template in AI_AGENT_TASKS:
                        task_id = f"P06-{feature_code}-AI-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=ai_feature.replace("_", " ")),
                            "assigned_agent": "AI-AGENT",
                            "priority": "P1",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

            # Testing tasks (P08)
            if "P08" in phases:
                phase_id = phases["P08"]
                task_num = 1

                for entity in entities[:5]:  # Limit to first 5 entities
                    for template in TEST_AGENT_TASKS:
                        task_id = f"P08-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "TEST-AGENT",
                            "priority": "P2",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

            # Documentation tasks (P10)
            if "P10" in phases:
                phase_id = phases["P10"]
                task_num = 1

                for entity in entities[:3]:  # Limit to first 3 entities
                    for template in DOC_AGENT_TASKS:
                        task_id = f"P10-{feature_code}-{entity[:3].upper()}-T{task_num:03d}"
                        all_tasks.append({
                            "task_id": task_id,
                            "phase_id": str(phase_id),
                            "module_id": str(module_id),
                            "feature_code": feature_code,
                            "title": template["title"].format(entity=entity.replace("_", " ")),
                            "assigned_agent": "DOC-AGENT",
                            "priority": "P3",
                            "complexity": template["complexity"],
                            "estimated_hours": template["hours"]
                        })
                        task_num += 1

            print(f"Generated tasks for {module_code} ({feature_code})")

        # Insert all tasks in batches
        print(f"\nInserting {len(all_tasks)} tasks into database...")

        batch_size = 100
        for i in range(0, len(all_tasks), batch_size):
            batch = all_tasks[i:i + batch_size]
            for task in batch:
                try:
                    await session.execute(text("""
                        INSERT INTO wbs_tasks (
                            task_id, phase_id, module_id, feature_code, title,
                            assigned_agent, priority, complexity, estimated_hours,
                            status, blocking_deps, non_blocking_deps, input_files,
                            output_files, acceptance_criteria
                        ) VALUES (
                            :task_id, :phase_id, :module_id, :feature_code, :title,
                            :assigned_agent, :priority, :complexity, :estimated_hours,
                            'pending', ARRAY[]::text[], ARRAY[]::text[], ARRAY[]::text[],
                            ARRAY[]::text[], ARRAY[]::text[]
                        )
                        ON CONFLICT (task_id) DO UPDATE SET
                            title = EXCLUDED.title,
                            assigned_agent = EXCLUDED.assigned_agent,
                            priority = EXCLUDED.priority,
                            complexity = EXCLUDED.complexity,
                            estimated_hours = EXCLUDED.estimated_hours
                    """), task)
                except Exception as e:
                    print(f"Error inserting task {task['task_id']}: {e}")

            await session.commit()
            print(f"  Inserted batch {i // batch_size + 1} ({min(i + batch_size, len(all_tasks))}/{len(all_tasks)})")

        tasks_generated = len(all_tasks)

    print(f"\n{'=' * 60}")
    print(f"WBS Task Generation Complete!")
    print(f"Total tasks generated: {tasks_generated}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    asyncio.run(generate_tasks())
