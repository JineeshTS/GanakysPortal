"""
CSR (Corporate Social Responsibility) Tracking API Endpoints
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.csr import (
    # Policy
    CSRPolicyCreate, CSRPolicyUpdate, CSRPolicyInDB,
    # Budget
    CSRBudgetCreate, CSRBudgetUpdate, CSRBudgetInDB, CSRBudgetList,
    # Project
    CSRProjectCreate, CSRProjectUpdate, CSRProjectInDB, CSRProjectList, CSRProjectApprove,
    # Disbursement
    CSRDisbursementCreate, CSRDisbursementUpdate, CSRDisbursementInDB, CSRDisbursementList,
    # Beneficiary
    CSRBeneficiaryCreate, CSRBeneficiaryUpdate, CSRBeneficiaryInDB, CSRBeneficiaryList,
    # Volunteer
    CSRVolunteerCreate, CSRVolunteerUpdate, CSRVolunteerInDB, CSRVolunteerList,
    # Impact Metric
    CSRImpactMetricCreate, CSRImpactMetricUpdate, CSRImpactMetricInDB, CSRImpactMetricList,
    # Report
    CSRReportCreate, CSRReportUpdate, CSRReportInDB, CSRReportList,
    # Dashboard
    CSRDashboardSummary,
    # Enums
    CSRCategory, CSRProjectStatus, BeneficiaryType, VolunteerStatus,
)
from app.services.csr import (
    policy_service, budget_service, project_service, disbursement_service,
    beneficiary_service, volunteer_service, impact_service, report_service,
    dashboard_service,
)

router = APIRouter()


# ============ CSR Policy ============

@router.post("/policy", response_model=CSRPolicyInDB, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy_in: CSRPolicyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create CSR policy for the company"""
    return await policy_service.create(
        db=db,
        obj_in=policy_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/policy", response_model=CSRPolicyInDB)
async def get_policy(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company's CSR policy"""
    policy = await policy_service.get_by_company(db=db, company_id=current_user.company_id)
    if not policy:
        raise HTTPException(status_code=404, detail="CSR policy not found")
    return policy


@router.put("/policy", response_model=CSRPolicyInDB)
async def update_policy(
    policy_in: CSRPolicyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update CSR policy"""
    policy = await policy_service.get_by_company(db=db, company_id=current_user.company_id)
    if not policy:
        raise HTTPException(status_code=404, detail="CSR policy not found")
    return await policy_service.update(db=db, db_obj=policy, obj_in=policy_in)


# ============ CSR Budgets ============

@router.post("/budgets", response_model=CSRBudgetInDB, status_code=status.HTTP_201_CREATED)
async def create_budget(
    budget_in: CSRBudgetCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create annual CSR budget"""
    return await budget_service.create(
        db=db,
        obj_in=budget_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/budgets", response_model=CSRBudgetList)
async def list_budgets(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    financial_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CSR budgets"""
    items, total = await budget_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        financial_year=financial_year,
    )
    pages = (total + size - 1) // size
    return CSRBudgetList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/budgets/{budget_id}", response_model=CSRBudgetInDB)
async def get_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific CSR budget"""
    budget = await budget_service.get(db=db, id=budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return budget


@router.put("/budgets/{budget_id}", response_model=CSRBudgetInDB)
async def update_budget(
    budget_id: UUID,
    budget_in: CSRBudgetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a CSR budget"""
    budget = await budget_service.get(db=db, id=budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return await budget_service.update(db=db, db_obj=budget, obj_in=budget_in)


@router.post("/budgets/{budget_id}/approve", response_model=CSRBudgetInDB)
async def approve_budget(
    budget_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a CSR budget"""
    budget = await budget_service.get(db=db, id=budget_id, company_id=current_user.company_id)
    if not budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return await budget_service.approve(db=db, db_obj=budget, user_id=current_user.id)


# ============ CSR Projects ============

@router.post("/projects", response_model=CSRProjectInDB, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_in: CSRProjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new CSR project"""
    return await project_service.create(
        db=db,
        obj_in=project_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/projects", response_model=CSRProjectList)
async def list_projects(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[CSRCategory] = None,
    status: Optional[CSRProjectStatus] = None,
    state: Optional[str] = None,
    financial_year: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CSR projects with filtering"""
    items, total = await project_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        status=status,
        state=state,
        financial_year=financial_year,
        search=search,
    )
    pages = (total + size - 1) // size
    return CSRProjectList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/projects/{project_id}", response_model=CSRProjectInDB)
async def get_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific CSR project"""
    project = await project_service.get(db=db, id=project_id, company_id=current_user.company_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/projects/{project_id}", response_model=CSRProjectInDB)
async def update_project(
    project_id: UUID,
    project_in: CSRProjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a CSR project"""
    project = await project_service.get(db=db, id=project_id, company_id=current_user.company_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project_service.update(db=db, db_obj=project, obj_in=project_in)


@router.post("/projects/{project_id}/approve", response_model=CSRProjectInDB)
async def approve_project(
    project_id: UUID,
    approval_in: CSRProjectApprove,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve or reject a CSR project"""
    project = await project_service.get(db=db, id=project_id, company_id=current_user.company_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return await project_service.approve(
        db=db,
        db_obj=project,
        user_id=current_user.id,
        approved=approval_in.approved,
    )


@router.delete("/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a CSR project"""
    project = await project_service.get(db=db, id=project_id, company_id=current_user.company_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await project_service.delete(db=db, id=project_id)


# ============ CSR Disbursements ============

@router.post("/disbursements", response_model=CSRDisbursementInDB, status_code=status.HTTP_201_CREATED)
async def create_disbursement(
    disbursement_in: CSRDisbursementCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new disbursement"""
    return await disbursement_service.create(
        db=db,
        obj_in=disbursement_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/disbursements", response_model=CSRDisbursementList)
async def list_disbursements(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List disbursements with filtering"""
    items, total = await disbursement_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        project_id=project_id,
        from_date=from_date,
        to_date=to_date,
    )
    pages = (total + size - 1) // size
    return CSRDisbursementList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/disbursements/{disbursement_id}", response_model=CSRDisbursementInDB)
async def get_disbursement(
    disbursement_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific disbursement"""
    disbursement = await disbursement_service.get(db=db, id=disbursement_id, company_id=current_user.company_id)
    if not disbursement:
        raise HTTPException(status_code=404, detail="Disbursement not found")
    return disbursement


@router.put("/disbursements/{disbursement_id}", response_model=CSRDisbursementInDB)
async def update_disbursement(
    disbursement_id: UUID,
    disbursement_in: CSRDisbursementUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a disbursement"""
    disbursement = await disbursement_service.get(db=db, id=disbursement_id, company_id=current_user.company_id)
    if not disbursement:
        raise HTTPException(status_code=404, detail="Disbursement not found")
    return await disbursement_service.update(db=db, db_obj=disbursement, obj_in=disbursement_in)


# ============ CSR Beneficiaries ============

@router.post("/beneficiaries", response_model=CSRBeneficiaryInDB, status_code=status.HTTP_201_CREATED)
async def create_beneficiary(
    beneficiary_in: CSRBeneficiaryCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new beneficiary"""
    return await beneficiary_service.create(
        db=db,
        obj_in=beneficiary_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/beneficiaries", response_model=CSRBeneficiaryList)
async def list_beneficiaries(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    beneficiary_type: Optional[BeneficiaryType] = None,
    state: Optional[str] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List beneficiaries with filtering"""
    items, total = await beneficiary_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        project_id=project_id,
        beneficiary_type=beneficiary_type,
        state=state,
        is_active=is_active,
        search=search,
    )
    pages = (total + size - 1) // size
    return CSRBeneficiaryList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/beneficiaries/{beneficiary_id}", response_model=CSRBeneficiaryInDB)
async def get_beneficiary(
    beneficiary_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific beneficiary"""
    beneficiary = await beneficiary_service.get(db=db, id=beneficiary_id, company_id=current_user.company_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return beneficiary


@router.put("/beneficiaries/{beneficiary_id}", response_model=CSRBeneficiaryInDB)
async def update_beneficiary(
    beneficiary_id: UUID,
    beneficiary_in: CSRBeneficiaryUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a beneficiary"""
    beneficiary = await beneficiary_service.get(db=db, id=beneficiary_id, company_id=current_user.company_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return await beneficiary_service.update(db=db, db_obj=beneficiary, obj_in=beneficiary_in)


@router.post("/beneficiaries/{beneficiary_id}/verify", response_model=CSRBeneficiaryInDB)
async def verify_beneficiary(
    beneficiary_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a beneficiary"""
    beneficiary = await beneficiary_service.get(db=db, id=beneficiary_id, company_id=current_user.company_id)
    if not beneficiary:
        raise HTTPException(status_code=404, detail="Beneficiary not found")
    return await beneficiary_service.verify(db=db, db_obj=beneficiary, user_id=current_user.id)


# ============ CSR Volunteers ============

@router.post("/volunteers", response_model=CSRVolunteerInDB, status_code=status.HTTP_201_CREATED)
async def create_volunteer(
    volunteer_in: CSRVolunteerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Register a volunteer for CSR activity"""
    return await volunteer_service.create(
        db=db,
        obj_in=volunteer_in,
        company_id=current_user.company_id,
    )


@router.get("/volunteers", response_model=CSRVolunteerList)
async def list_volunteers(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    employee_id: Optional[UUID] = None,
    status: Optional[VolunteerStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List volunteers with filtering"""
    items, total = await volunteer_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        project_id=project_id,
        employee_id=employee_id,
        status=status,
        from_date=from_date,
        to_date=to_date,
    )
    pages = (total + size - 1) // size
    return CSRVolunteerList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/volunteers/{volunteer_id}", response_model=CSRVolunteerInDB)
async def get_volunteer(
    volunteer_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific volunteer record"""
    volunteer = await volunteer_service.get(db=db, id=volunteer_id, company_id=current_user.company_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer record not found")
    return volunteer


@router.put("/volunteers/{volunteer_id}", response_model=CSRVolunteerInDB)
async def update_volunteer(
    volunteer_id: UUID,
    volunteer_in: CSRVolunteerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a volunteer record"""
    volunteer = await volunteer_service.get(db=db, id=volunteer_id, company_id=current_user.company_id)
    if not volunteer:
        raise HTTPException(status_code=404, detail="Volunteer record not found")
    return await volunteer_service.update(db=db, db_obj=volunteer, obj_in=volunteer_in)


# ============ CSR Impact Metrics ============

@router.post("/impact-metrics", response_model=CSRImpactMetricInDB, status_code=status.HTTP_201_CREATED)
async def create_impact_metric(
    metric_in: CSRImpactMetricCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new impact metric"""
    return await impact_service.create(
        db=db,
        obj_in=metric_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/impact-metrics", response_model=CSRImpactMetricList)
async def list_impact_metrics(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    project_id: Optional[UUID] = None,
    sdg_goal: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List impact metrics with filtering"""
    items, total = await impact_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        project_id=project_id,
        sdg_goal=sdg_goal,
    )
    pages = (total + size - 1) // size
    return CSRImpactMetricList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/impact-metrics/{metric_id}", response_model=CSRImpactMetricInDB)
async def get_impact_metric(
    metric_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific impact metric"""
    metric = await impact_service.get(db=db, id=metric_id, company_id=current_user.company_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Impact metric not found")
    return metric


@router.put("/impact-metrics/{metric_id}", response_model=CSRImpactMetricInDB)
async def update_impact_metric(
    metric_id: UUID,
    metric_in: CSRImpactMetricUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an impact metric"""
    metric = await impact_service.get(db=db, id=metric_id, company_id=current_user.company_id)
    if not metric:
        raise HTTPException(status_code=404, detail="Impact metric not found")
    return await impact_service.update(db=db, db_obj=metric, obj_in=metric_in)


# ============ CSR Reports ============

@router.post("/reports", response_model=CSRReportInDB, status_code=status.HTTP_201_CREATED)
async def create_report(
    report_in: CSRReportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new CSR report"""
    return await report_service.create(
        db=db,
        obj_in=report_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/reports", response_model=CSRReportList)
async def list_reports(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    financial_year: Optional[str] = None,
    report_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List CSR reports"""
    items, total = await report_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        financial_year=financial_year,
        report_type=report_type,
    )
    pages = (total + size - 1) // size
    return CSRReportList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/reports/{report_id}", response_model=CSRReportInDB)
async def get_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific CSR report"""
    report = await report_service.get(db=db, id=report_id, company_id=current_user.company_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.put("/reports/{report_id}", response_model=CSRReportInDB)
async def update_report(
    report_id: UUID,
    report_in: CSRReportUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a CSR report"""
    report = await report_service.get(db=db, id=report_id, company_id=current_user.company_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return await report_service.update(db=db, db_obj=report, obj_in=report_in)


@router.post("/reports/{report_id}/generate", response_model=CSRReportInDB)
async def generate_report(
    report_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate/refresh report data from projects"""
    report = await report_service.get(db=db, id=report_id, company_id=current_user.company_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return await report_service.generate(db=db, db_obj=report)


# ============ Dashboard ============

@router.get("/dashboard", response_model=CSRDashboardSummary)
async def get_dashboard(
    financial_year: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get CSR dashboard summary"""
    return await dashboard_service.get_summary(
        db=db,
        company_id=current_user.company_id,
        financial_year=financial_year,
    )
