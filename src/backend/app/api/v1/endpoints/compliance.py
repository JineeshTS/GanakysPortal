"""
Compliance Master API Endpoints
"""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.compliance import (
    ComplianceMasterCreate, ComplianceMasterUpdate, ComplianceMasterInDB, ComplianceMasterList,
    ComplianceTaskCreate, ComplianceTaskUpdate, ComplianceTaskInDB, ComplianceTaskList,
    ComplianceAuditCreate, ComplianceAuditUpdate, ComplianceAuditInDB, ComplianceAuditList,
    RiskAssessmentCreate, RiskAssessmentUpdate, RiskAssessmentInDB,
    CompliancePolicyCreate, CompliancePolicyUpdate, CompliancePolicyInDB, CompliancePolicyList,
    ComplianceTrainingCreate, ComplianceTrainingUpdate, ComplianceTrainingInDB, ComplianceTrainingList,
    ComplianceDashboardSummary, ComplianceCategory, ComplianceStatus, RiskLevel,
)
from app.services.compliance import (
    compliance_service, task_service, audit_service, risk_service,
    policy_service, training_service, dashboard_service,
)

router = APIRouter()


# Dashboard
@router.get("/dashboard", response_model=ComplianceDashboardSummary)
async def get_dashboard(
    financial_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance dashboard"""
    return await dashboard_service.get_summary(db, current_user.company_id, financial_year)


# Compliance Master
@router.post("/masters", response_model=ComplianceMasterInDB, status_code=status.HTTP_201_CREATED)
async def create_compliance(
    obj_in: ComplianceMasterCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await compliance_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.get("/masters", response_model=ComplianceMasterList)
async def list_compliances(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    category: Optional[ComplianceCategory] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await compliance_service.get_list(
        db, current_user.company_id, page, size, search, category, is_active
    )
    return ComplianceMasterList(items=items, total=total, page=page, size=size)


@router.get("/masters/{compliance_id}", response_model=ComplianceMasterInDB)
async def get_compliance(
    compliance_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    compliance = await compliance_service.get(db, compliance_id, current_user.company_id)
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance not found")
    return compliance


@router.put("/masters/{compliance_id}", response_model=ComplianceMasterInDB)
async def update_compliance(
    compliance_id: UUID,
    obj_in: ComplianceMasterUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    compliance = await compliance_service.get(db, compliance_id, current_user.company_id)
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance not found")
    return await compliance_service.update(db, compliance, obj_in)


# Compliance Tasks
@router.post("/tasks", response_model=ComplianceTaskInDB, status_code=status.HTTP_201_CREATED)
async def create_task(
    obj_in: ComplianceTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await task_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.get("/tasks", response_model=ComplianceTaskList)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    compliance_id: Optional[UUID] = None,
    status: Optional[ComplianceStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    assigned_to: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await task_service.get_list(
        db, current_user.company_id, page, size, compliance_id, status, from_date, to_date, assigned_to
    )
    return ComplianceTaskList(items=items, total=total, page=page, size=size)


@router.get("/tasks/{task_id}", response_model=ComplianceTaskInDB)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_service.get(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=ComplianceTaskInDB)
async def update_task(
    task_id: UUID,
    obj_in: ComplianceTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_service.get(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await task_service.update(db, task, obj_in)


@router.post("/tasks/{task_id}/complete", response_model=ComplianceTaskInDB)
async def complete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = await task_service.get(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await task_service.complete(db, task, current_user.id)


# Audits
@router.post("/audits", response_model=ComplianceAuditInDB, status_code=status.HTTP_201_CREATED)
async def create_audit(
    obj_in: ComplianceAuditCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await audit_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.get("/audits", response_model=ComplianceAuditList)
async def list_audits(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    audit_type: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await audit_service.get_list(db, current_user.company_id, page, size, audit_type, status)
    return ComplianceAuditList(items=items, total=total, page=page, size=size)


@router.get("/audits/{audit_id}", response_model=ComplianceAuditInDB)
async def get_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audit = await audit_service.get(db, audit_id, current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.put("/audits/{audit_id}", response_model=ComplianceAuditInDB)
async def update_audit(
    audit_id: UUID,
    obj_in: ComplianceAuditUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    audit = await audit_service.get(db, audit_id, current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return await audit_service.update(db, audit, obj_in)


# Policies
@router.post("/policies", response_model=CompliancePolicyInDB, status_code=status.HTTP_201_CREATED)
async def create_policy(
    obj_in: CompliancePolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await policy_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.get("/policies", response_model=CompliancePolicyList)
async def list_policies(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ComplianceCategory] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await policy_service.get_list(db, current_user.company_id, page, size, category, status)
    return CompliancePolicyList(items=items, total=total, page=page, size=size)


@router.get("/policies/{policy_id}", response_model=CompliancePolicyInDB)
async def get_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = await policy_service.get(db, policy_id, current_user.company_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.put("/policies/{policy_id}", response_model=CompliancePolicyInDB)
async def update_policy(
    policy_id: UUID,
    obj_in: CompliancePolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    policy = await policy_service.get(db, policy_id, current_user.company_id)
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return await policy_service.update(db, policy, obj_in)


# Trainings
@router.post("/trainings", response_model=ComplianceTrainingInDB, status_code=status.HTTP_201_CREATED)
async def create_training(
    obj_in: ComplianceTrainingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await training_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.get("/trainings", response_model=ComplianceTrainingList)
async def list_trainings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[ComplianceCategory] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total = await training_service.get_list(db, current_user.company_id, page, size, category, status)
    return ComplianceTrainingList(items=items, total=total, page=page, size=size)


@router.get("/trainings/{training_id}", response_model=ComplianceTrainingInDB)
async def get_training(
    training_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = await training_service.get(db, training_id, current_user.company_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return training


@router.put("/trainings/{training_id}", response_model=ComplianceTrainingInDB)
async def update_training(
    training_id: UUID,
    obj_in: ComplianceTrainingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    training = await training_service.get(db, training_id, current_user.company_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return await training_service.update(db, training, obj_in)


# Risk Assessments
@router.post("/risk-assessments", response_model=RiskAssessmentInDB, status_code=status.HTTP_201_CREATED)
async def create_risk_assessment(
    obj_in: RiskAssessmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return await risk_service.create(db, obj_in, current_user.company_id, current_user.id)


@router.put("/risk-assessments/{assessment_id}", response_model=RiskAssessmentInDB)
async def update_risk_assessment(
    assessment_id: UUID,
    obj_in: RiskAssessmentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assessment = await risk_service.get(db, assessment_id, current_user.company_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="Risk assessment not found")
    return await risk_service.update(db, assessment, obj_in)


# Generate tasks for compliance
@router.post("/masters/{compliance_id}/generate-tasks")
async def generate_compliance_tasks(
    compliance_id: UUID,
    financial_year: str = Query(..., description="Financial year e.g., 2024-25"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    compliance = await compliance_service.get(db, compliance_id, current_user.company_id)
    if not compliance:
        raise HTTPException(status_code=404, detail="Compliance not found")
    tasks = await compliance_service.generate_tasks(db, compliance, financial_year, current_user.id)
    return {"message": f"Generated {len(tasks)} tasks for FY {financial_year}"}
