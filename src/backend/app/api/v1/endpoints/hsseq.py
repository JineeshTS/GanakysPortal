"""
HSSEQ (Health, Safety, Security, Environment, Quality) Management API Endpoints
"""
from datetime import date
from typing import Optional, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.hsseq import (
    # Incidents
    HSEIncidentCreate, HSEIncidentUpdate, HSEIncidentInDB, HSEIncidentList,
    # Hazards
    HazardIdentificationCreate, HazardIdentificationUpdate, HazardIdentificationInDB, HazardIdentificationList,
    # Corrective Actions
    CorrectiveActionCreate, CorrectiveActionUpdate, CorrectiveActionInDB, CorrectiveActionList, CorrectiveActionVerify,
    # Audits
    HSEAuditCreate, HSEAuditUpdate, HSEAuditInDB, HSEAuditList, HSEAuditFindings,
    # Trainings
    HSETrainingCreate, HSETrainingUpdate, HSETrainingInDB, HSETrainingList,
    # Training Records
    TrainingRecordCreate, TrainingRecordUpdate, TrainingRecordInDB, TrainingRecordList,
    # Work Permits
    WorkPermitCreate, WorkPermitUpdate, WorkPermitInDB, WorkPermitList, WorkPermitApproval, WorkPermitComplete,
    # Inspections
    HSEInspectionCreate, HSEInspectionUpdate, HSEInspectionInDB, HSEInspectionList, HSEInspectionSubmit,
    # Safety Observations
    SafetyObservationCreate, SafetyObservationUpdate, SafetyObservationInDB, SafetyObservationList,
    # KPIs
    HSEKPICreate, HSEKPIUpdate, HSEKPIInDB, HSEKPIList,
    # Dashboard
    HSEDashboard,
    # Enums
    HSECategory, IncidentType, IncidentSeverity, IncidentStatus, HazardRiskLevel,
    AuditType, AuditStatus, TrainingType, PermitType, PermitStatus, ActionStatus, InspectionType,
)
from app.services.hsseq import (
    incident_service, hazard_service, action_service, audit_service,
    training_service, training_record_service, permit_service,
    inspection_service, observation_service, kpi_service, dashboard_service,
)

router = APIRouter()


# ============ HSE Incidents ============

@router.post("/incidents", response_model=HSEIncidentInDB, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident_in: HSEIncidentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HSE incident"""
    return await incident_service.create(
        db=db,
        obj_in=incident_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/incidents", response_model=HSEIncidentList)
async def list_incidents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    incident_type: Optional[IncidentType] = None,
    severity: Optional[IncidentSeverity] = None,
    status: Optional[IncidentStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List HSE incidents with filtering and pagination"""
    items, total = await incident_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        incident_type=incident_type,
        severity=severity,
        status=status,
        from_date=from_date,
        to_date=to_date,
        location=location,
        department=department,
        search=search,
    )
    pages = (total + size - 1) // size
    return HSEIncidentList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/incidents/{incident_id}", response_model=HSEIncidentInDB)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific HSE incident"""
    incident = await incident_service.get(db=db, id=incident_id, company_id=current_user.company_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.put("/incidents/{incident_id}", response_model=HSEIncidentInDB)
async def update_incident(
    incident_id: UUID,
    incident_in: HSEIncidentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an HSE incident"""
    incident = await incident_service.get(db=db, id=incident_id, company_id=current_user.company_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await incident_service.update(db=db, db_obj=incident, obj_in=incident_in)


@router.post("/incidents/{incident_id}/close", response_model=HSEIncidentInDB)
async def close_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Close an HSE incident"""
    incident = await incident_service.get(db=db, id=incident_id, company_id=current_user.company_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return await incident_service.close(db=db, db_obj=incident, user_id=current_user.id)


@router.delete("/incidents/{incident_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an HSE incident"""
    incident = await incident_service.get(db=db, id=incident_id, company_id=current_user.company_id)
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    await incident_service.delete(db=db, id=incident_id)


# ============ Hazard Identifications ============

@router.post("/hazards", response_model=HazardIdentificationInDB, status_code=status.HTTP_201_CREATED)
async def create_hazard(
    hazard_in: HazardIdentificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hazard identification"""
    return await hazard_service.create(
        db=db,
        obj_in=hazard_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/hazards", response_model=HazardIdentificationList)
async def list_hazards(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    risk_level: Optional[HazardRiskLevel] = None,
    is_active: Optional[bool] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hazard identifications with filtering and pagination"""
    items, total = await hazard_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        risk_level=risk_level,
        is_active=is_active,
        location=location,
        department=department,
        search=search,
    )
    pages = (total + size - 1) // size
    return HazardIdentificationList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/hazards/{hazard_id}", response_model=HazardIdentificationInDB)
async def get_hazard(
    hazard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific hazard identification"""
    hazard = await hazard_service.get(db=db, id=hazard_id, company_id=current_user.company_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    return hazard


@router.put("/hazards/{hazard_id}", response_model=HazardIdentificationInDB)
async def update_hazard(
    hazard_id: UUID,
    hazard_in: HazardIdentificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a hazard identification"""
    hazard = await hazard_service.get(db=db, id=hazard_id, company_id=current_user.company_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    return await hazard_service.update(db=db, db_obj=hazard, obj_in=hazard_in)


@router.delete("/hazards/{hazard_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_hazard(
    hazard_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a hazard identification"""
    hazard = await hazard_service.get(db=db, id=hazard_id, company_id=current_user.company_id)
    if not hazard:
        raise HTTPException(status_code=404, detail="Hazard not found")
    await hazard_service.delete(db=db, id=hazard_id)


# ============ Corrective Actions ============

@router.post("/actions", response_model=CorrectiveActionInDB, status_code=status.HTTP_201_CREATED)
async def create_action(
    action_in: CorrectiveActionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new corrective action"""
    return await action_service.create(
        db=db,
        obj_in=action_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/actions", response_model=CorrectiveActionList)
async def list_actions(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    status: Optional[ActionStatus] = None,
    priority: Optional[str] = None,
    assigned_to: Optional[UUID] = None,
    source_type: Optional[str] = None,
    source_id: Optional[UUID] = None,
    overdue_only: Optional[bool] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List corrective actions with filtering and pagination"""
    items, total = await action_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        status=status,
        priority=priority,
        assigned_to=assigned_to,
        source_type=source_type,
        source_id=source_id,
        overdue_only=overdue_only,
        search=search,
    )
    pages = (total + size - 1) // size
    return CorrectiveActionList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/actions/{action_id}", response_model=CorrectiveActionInDB)
async def get_action(
    action_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific corrective action"""
    action = await action_service.get(db=db, id=action_id, company_id=current_user.company_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.put("/actions/{action_id}", response_model=CorrectiveActionInDB)
async def update_action(
    action_id: UUID,
    action_in: CorrectiveActionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a corrective action"""
    action = await action_service.get(db=db, id=action_id, company_id=current_user.company_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return await action_service.update(db=db, db_obj=action, obj_in=action_in)


@router.post("/actions/{action_id}/verify", response_model=CorrectiveActionInDB)
async def verify_action(
    action_id: UUID,
    verify_in: CorrectiveActionVerify,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Verify a corrective action"""
    action = await action_service.get(db=db, id=action_id, company_id=current_user.company_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return await action_service.verify(
        db=db,
        db_obj=action,
        user_id=current_user.id,
        notes=verify_in.verification_notes,
        rating=verify_in.effectiveness_rating,
    )


@router.delete("/actions/{action_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_action(
    action_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a corrective action"""
    action = await action_service.get(db=db, id=action_id, company_id=current_user.company_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    await action_service.delete(db=db, id=action_id)


# ============ HSE Audits ============

@router.post("/audits", response_model=HSEAuditInDB, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit_in: HSEAuditCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HSE audit"""
    return await audit_service.create(
        db=db,
        obj_in=audit_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/audits", response_model=HSEAuditList)
async def list_audits(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    audit_type: Optional[AuditType] = None,
    category: Optional[HSECategory] = None,
    status: Optional[AuditStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List HSE audits with filtering and pagination"""
    items, total = await audit_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        audit_type=audit_type,
        category=category,
        status=status,
        from_date=from_date,
        to_date=to_date,
        location=location,
        department=department,
        search=search,
    )
    pages = (total + size - 1) // size
    return HSEAuditList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/audits/{audit_id}", response_model=HSEAuditInDB)
async def get_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific HSE audit"""
    audit = await audit_service.get(db=db, id=audit_id, company_id=current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.put("/audits/{audit_id}", response_model=HSEAuditInDB)
async def update_audit(
    audit_id: UUID,
    audit_in: HSEAuditUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an HSE audit"""
    audit = await audit_service.get(db=db, id=audit_id, company_id=current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return await audit_service.update(db=db, db_obj=audit, obj_in=audit_in)


@router.post("/audits/{audit_id}/findings", response_model=HSEAuditInDB)
async def submit_audit_findings(
    audit_id: UUID,
    findings_in: HSEAuditFindings,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit audit findings"""
    audit = await audit_service.get(db=db, id=audit_id, company_id=current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return await audit_service.submit_findings(db=db, db_obj=audit, findings=findings_in)


@router.delete("/audits/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an HSE audit"""
    audit = await audit_service.get(db=db, id=audit_id, company_id=current_user.company_id)
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    await audit_service.delete(db=db, id=audit_id)


# ============ HSE Trainings ============

@router.post("/trainings", response_model=HSETrainingInDB, status_code=status.HTTP_201_CREATED)
async def create_training(
    training_in: HSETrainingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HSE training"""
    return await training_service.create(
        db=db,
        obj_in=training_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/trainings", response_model=HSETrainingList)
async def list_trainings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    training_type: Optional[TrainingType] = None,
    is_active: Optional[bool] = None,
    mandatory: Optional[bool] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List HSE trainings with filtering and pagination"""
    items, total = await training_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        training_type=training_type,
        is_active=is_active,
        mandatory=mandatory,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    pages = (total + size - 1) // size
    return HSETrainingList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/trainings/{training_id}", response_model=HSETrainingInDB)
async def get_training(
    training_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific HSE training"""
    training = await training_service.get(db=db, id=training_id, company_id=current_user.company_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return training


@router.put("/trainings/{training_id}", response_model=HSETrainingInDB)
async def update_training(
    training_id: UUID,
    training_in: HSETrainingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an HSE training"""
    training = await training_service.get(db=db, id=training_id, company_id=current_user.company_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    return await training_service.update(db=db, db_obj=training, obj_in=training_in)


@router.delete("/trainings/{training_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training(
    training_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an HSE training"""
    training = await training_service.get(db=db, id=training_id, company_id=current_user.company_id)
    if not training:
        raise HTTPException(status_code=404, detail="Training not found")
    await training_service.delete(db=db, id=training_id)


# ============ Training Records ============

@router.post("/training-records", response_model=TrainingRecordInDB, status_code=status.HTTP_201_CREATED)
async def create_training_record(
    record_in: TrainingRecordCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new training record"""
    return await training_record_service.create(
        db=db,
        obj_in=record_in,
        company_id=current_user.company_id,
    )


@router.get("/training-records", response_model=TrainingRecordList)
async def list_training_records(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    training_id: Optional[UUID] = None,
    employee_id: Optional[UUID] = None,
    status: Optional[str] = None,
    expiring_within_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List training records with filtering and pagination"""
    items, total = await training_record_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        training_id=training_id,
        employee_id=employee_id,
        status=status,
        expiring_within_days=expiring_within_days,
    )
    pages = (total + size - 1) // size
    return TrainingRecordList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/training-records/{record_id}", response_model=TrainingRecordInDB)
async def get_training_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific training record"""
    record = await training_record_service.get(db=db, id=record_id, company_id=current_user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Training record not found")
    return record


@router.put("/training-records/{record_id}", response_model=TrainingRecordInDB)
async def update_training_record(
    record_id: UUID,
    record_in: TrainingRecordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a training record"""
    record = await training_record_service.get(db=db, id=record_id, company_id=current_user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Training record not found")
    return await training_record_service.update(db=db, db_obj=record, obj_in=record_in)


@router.delete("/training-records/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_training_record(
    record_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a training record"""
    record = await training_record_service.get(db=db, id=record_id, company_id=current_user.company_id)
    if not record:
        raise HTTPException(status_code=404, detail="Training record not found")
    await training_record_service.delete(db=db, id=record_id)


# ============ Work Permits ============

@router.post("/permits", response_model=WorkPermitInDB, status_code=status.HTTP_201_CREATED)
async def create_permit(
    permit_in: WorkPermitCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new work permit"""
    return await permit_service.create(
        db=db,
        obj_in=permit_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/permits", response_model=WorkPermitList)
async def list_permits(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    permit_type: Optional[PermitType] = None,
    status: Optional[PermitStatus] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    active_only: Optional[bool] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List work permits with filtering and pagination"""
    items, total = await permit_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        permit_type=permit_type,
        status=status,
        location=location,
        department=department,
        active_only=active_only,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    pages = (total + size - 1) // size
    return WorkPermitList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/permits/{permit_id}", response_model=WorkPermitInDB)
async def get_permit(
    permit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return permit


@router.put("/permits/{permit_id}", response_model=WorkPermitInDB)
async def update_permit(
    permit_id: UUID,
    permit_in: WorkPermitUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return await permit_service.update(db=db, db_obj=permit, obj_in=permit_in)


@router.post("/permits/{permit_id}/approve", response_model=WorkPermitInDB)
async def approve_permit(
    permit_id: UUID,
    approval_in: WorkPermitApproval,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve a work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return await permit_service.approve(
        db=db,
        db_obj=permit,
        user_id=current_user.id,
        approval_type=approval_in.approval_type,
        approved=approval_in.approved,
    )


@router.post("/permits/{permit_id}/activate", response_model=WorkPermitInDB)
async def activate_permit(
    permit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Activate a work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return await permit_service.activate(db=db, db_obj=permit)


@router.post("/permits/{permit_id}/complete", response_model=WorkPermitInDB)
async def complete_permit(
    permit_id: UUID,
    complete_in: WorkPermitComplete,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Complete a work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    return await permit_service.complete(
        db=db,
        db_obj=permit,
        user_id=current_user.id,
        notes=complete_in.completion_notes,
        area_handed_back=complete_in.area_handed_back,
    )


@router.delete("/permits/{permit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_permit(
    permit_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a work permit"""
    permit = await permit_service.get(db=db, id=permit_id, company_id=current_user.company_id)
    if not permit:
        raise HTTPException(status_code=404, detail="Permit not found")
    await permit_service.delete(db=db, id=permit_id)


# ============ HSE Inspections ============

@router.post("/inspections", response_model=HSEInspectionInDB, status_code=status.HTTP_201_CREATED)
async def create_inspection(
    inspection_in: HSEInspectionCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HSE inspection"""
    return await inspection_service.create(
        db=db,
        obj_in=inspection_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/inspections", response_model=HSEInspectionList)
async def list_inspections(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    inspection_type: Optional[InspectionType] = None,
    category: Optional[HSECategory] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    inspector_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List HSE inspections with filtering and pagination"""
    items, total = await inspection_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        inspection_type=inspection_type,
        category=category,
        status=status,
        location=location,
        department=department,
        inspector_id=inspector_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    pages = (total + size - 1) // size
    return HSEInspectionList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/inspections/{inspection_id}", response_model=HSEInspectionInDB)
async def get_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific HSE inspection"""
    inspection = await inspection_service.get(db=db, id=inspection_id, company_id=current_user.company_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return inspection


@router.put("/inspections/{inspection_id}", response_model=HSEInspectionInDB)
async def update_inspection(
    inspection_id: UUID,
    inspection_in: HSEInspectionUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an HSE inspection"""
    inspection = await inspection_service.get(db=db, id=inspection_id, company_id=current_user.company_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return await inspection_service.update(db=db, db_obj=inspection, obj_in=inspection_in)


@router.post("/inspections/{inspection_id}/submit", response_model=HSEInspectionInDB)
async def submit_inspection(
    inspection_id: UUID,
    submit_in: HSEInspectionSubmit,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Submit inspection findings"""
    inspection = await inspection_service.get(db=db, id=inspection_id, company_id=current_user.company_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    return await inspection_service.submit(db=db, db_obj=inspection, submit_data=submit_in)


@router.delete("/inspections/{inspection_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inspection(
    inspection_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an HSE inspection"""
    inspection = await inspection_service.get(db=db, id=inspection_id, company_id=current_user.company_id)
    if not inspection:
        raise HTTPException(status_code=404, detail="Inspection not found")
    await inspection_service.delete(db=db, id=inspection_id)


# ============ Safety Observations ============

@router.post("/observations", response_model=SafetyObservationInDB, status_code=status.HTTP_201_CREATED)
async def create_observation(
    observation_in: SafetyObservationCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new safety observation"""
    return await observation_service.create(
        db=db,
        obj_in=observation_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/observations", response_model=SafetyObservationList)
async def list_observations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    observation_type: Optional[str] = None,
    risk_level: Optional[HazardRiskLevel] = None,
    status: Optional[str] = None,
    location: Optional[str] = None,
    department: Optional[str] = None,
    observer_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List safety observations with filtering and pagination"""
    items, total = await observation_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        observation_type=observation_type,
        risk_level=risk_level,
        status=status,
        location=location,
        department=department,
        observer_id=observer_id,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    pages = (total + size - 1) // size
    return SafetyObservationList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/observations/{observation_id}", response_model=SafetyObservationInDB)
async def get_observation(
    observation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific safety observation"""
    observation = await observation_service.get(db=db, id=observation_id, company_id=current_user.company_id)
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    return observation


@router.put("/observations/{observation_id}", response_model=SafetyObservationInDB)
async def update_observation(
    observation_id: UUID,
    observation_in: SafetyObservationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a safety observation"""
    observation = await observation_service.get(db=db, id=observation_id, company_id=current_user.company_id)
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    return await observation_service.update(db=db, db_obj=observation, obj_in=observation_in)


@router.delete("/observations/{observation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_observation(
    observation_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a safety observation"""
    observation = await observation_service.get(db=db, id=observation_id, company_id=current_user.company_id)
    if not observation:
        raise HTTPException(status_code=404, detail="Observation not found")
    await observation_service.delete(db=db, id=observation_id)


# ============ HSE KPIs ============

@router.post("/kpis", response_model=HSEKPIInDB, status_code=status.HTTP_201_CREATED)
async def create_kpi(
    kpi_in: HSEKPICreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new HSE KPI"""
    return await kpi_service.create(
        db=db,
        obj_in=kpi_in,
        company_id=current_user.company_id,
        user_id=current_user.id,
    )


@router.get("/kpis", response_model=HSEKPIList)
async def list_kpis(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    category: Optional[HSECategory] = None,
    kpi_type: Optional[str] = None,
    period_type: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List HSE KPIs with filtering and pagination"""
    items, total = await kpi_service.get_list(
        db=db,
        company_id=current_user.company_id,
        page=page,
        size=size,
        category=category,
        kpi_type=kpi_type,
        period_type=period_type,
        from_date=from_date,
        to_date=to_date,
        search=search,
    )
    pages = (total + size - 1) // size
    return HSEKPIList(items=items, total=total, page=page, size=size, pages=pages)


@router.get("/kpis/{kpi_id}", response_model=HSEKPIInDB)
async def get_kpi(
    kpi_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific HSE KPI"""
    kpi = await kpi_service.get(db=db, id=kpi_id, company_id=current_user.company_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    return kpi


@router.put("/kpis/{kpi_id}", response_model=HSEKPIInDB)
async def update_kpi(
    kpi_id: UUID,
    kpi_in: HSEKPIUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update an HSE KPI"""
    kpi = await kpi_service.get(db=db, id=kpi_id, company_id=current_user.company_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    return await kpi_service.update(db=db, db_obj=kpi, obj_in=kpi_in)


@router.delete("/kpis/{kpi_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_kpi(
    kpi_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete an HSE KPI"""
    kpi = await kpi_service.get(db=db, id=kpi_id, company_id=current_user.company_id)
    if not kpi:
        raise HTTPException(status_code=404, detail="KPI not found")
    await kpi_service.delete(db=db, id=kpi_id)


@router.post("/kpis/calculate", status_code=status.HTTP_200_OK)
async def calculate_kpis(
    period_start: date,
    period_end: date,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate KPIs for a period"""
    await kpi_service.calculate_kpis(
        db=db,
        company_id=current_user.company_id,
        period_start=period_start,
        period_end=period_end,
    )
    return {"message": "KPIs calculated successfully"}


# ============ Dashboard ============

@router.get("/dashboard", response_model=HSEDashboard)
async def get_dashboard(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get HSE dashboard data"""
    return await dashboard_service.get_dashboard(
        db=db,
        company_id=current_user.company_id,
        from_date=from_date,
        to_date=to_date,
    )
