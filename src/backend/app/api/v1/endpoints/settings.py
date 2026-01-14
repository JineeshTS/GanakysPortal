"""
Settings API Endpoints
Company, Payroll, Leave, Attendance, Email configuration management
"""
import uuid
from datetime import datetime, date
from typing import List, Optional, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.api.v1.endpoints.auth import get_current_user, TokenData
from app.models.company import CompanyProfile
from app.models.payroll import SalaryComponent  # Use existing payroll model
from app.models.leave import LeaveType, Holiday  # Use existing leave model
from app.models.settings import (
    CompanyBranch, PFSettings, ESISettings, PTSettings,
    TDSSettings, PaySchedule, WeekOffSetting,
    Shift, OvertimeRule, AttendanceConfig, GeoFenceLocation,
    EmailTemplate, Role
)
from app.schemas.settings import (
    # Company
    CompanySettingsUpdate, CompanySettingsResponse,
    BranchCreate, BranchUpdate, BranchResponse,
    # Payroll
    SalaryComponentCreate, SalaryComponentUpdate, SalaryComponentResponse,
    PFSettingsUpdate, PFSettingsResponse,
    ESISettingsUpdate, ESISettingsResponse,
    PTSettingsUpdate, PTSettingsResponse,
    TDSSettingsUpdate, TDSSettingsResponse,
    PayScheduleUpdate, PayScheduleResponse,
    PayrollSettingsResponse,
    # Leave
    LeaveTypeCreate, LeaveTypeUpdate, LeaveTypeResponse,
    HolidayCreate, HolidayUpdate, HolidayResponse,
    WeekOffSettingUpdate, WeekOffSettingResponse,
    LeaveSettingsResponse,
    # Attendance
    ShiftCreate, ShiftUpdate, ShiftResponse,
    OvertimeRuleCreate, OvertimeRuleUpdate, OvertimeRuleResponse,
    AttendanceConfigUpdate, AttendanceConfigResponse,
    GeoFenceLocationCreate, GeoFenceLocationUpdate, GeoFenceLocationResponse,
    AttendanceSettingsResponse,
    # Email
    EmailTemplateCreate, EmailTemplateUpdate, EmailTemplateResponse,
    # Role
    RoleCreate, RoleUpdate, RoleResponse,
)

router = APIRouter()


# ============================================================================
# Company Settings
# ============================================================================

@router.get("/company", response_model=CompanySettingsResponse)
async def get_company_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get company settings."""
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.put("/company", response_model=CompanySettingsResponse)
async def update_company_settings(
    data: CompanySettingsUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update company settings."""
    result = await db.execute(
        select(CompanyProfile).where(CompanyProfile.id == current_user.company_id)
    )
    company = result.scalar_one_or_none()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(company, field, value)
    company.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(company)
    return company


# ============================================================================
# Branches
# ============================================================================

@router.get("/branches", response_model=List[BranchResponse])
async def list_branches(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all company branches."""
    result = await db.execute(
        select(CompanyBranch)
        .where(CompanyBranch.company_id == current_user.company_id)
        .order_by(CompanyBranch.is_head_office.desc(), CompanyBranch.name)
    )
    return result.scalars().all()


@router.post("/branches", response_model=BranchResponse, status_code=status.HTTP_201_CREATED)
async def create_branch(
    data: BranchCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a new branch."""
    branch = CompanyBranch(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(branch)
    await db.commit()
    await db.refresh(branch)
    return branch


@router.put("/branches/{branch_id}", response_model=BranchResponse)
async def update_branch(
    branch_id: uuid.UUID,
    data: BranchUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a branch."""
    result = await db.execute(
        select(CompanyBranch).where(
            and_(CompanyBranch.id == branch_id, CompanyBranch.company_id == current_user.company_id)
        )
    )
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(branch, field, value)
    branch.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(branch)
    return branch


@router.delete("/branches/{branch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_branch(
    branch_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a branch."""
    result = await db.execute(
        select(CompanyBranch).where(
            and_(CompanyBranch.id == branch_id, CompanyBranch.company_id == current_user.company_id)
        )
    )
    branch = result.scalar_one_or_none()
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")

    await db.delete(branch)
    await db.commit()


# ============================================================================
# Salary Components
# ============================================================================

@router.get("/payroll/components", response_model=List[SalaryComponentResponse])
async def list_salary_components(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all salary components."""
    result = await db.execute(
        select(SalaryComponent)
        .where(SalaryComponent.company_id == current_user.company_id)
        .order_by(SalaryComponent.display_order, SalaryComponent.component_type)
    )
    return result.scalars().all()


@router.post("/payroll/components", response_model=SalaryComponentResponse, status_code=status.HTTP_201_CREATED)
async def create_salary_component(
    data: SalaryComponentCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a salary component."""
    component = SalaryComponent(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(component)
    await db.commit()
    await db.refresh(component)
    return component


@router.put("/payroll/components/{component_id}", response_model=SalaryComponentResponse)
async def update_salary_component(
    component_id: uuid.UUID,
    data: SalaryComponentUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a salary component."""
    result = await db.execute(
        select(SalaryComponent).where(
            and_(SalaryComponent.id == component_id, SalaryComponent.company_id == current_user.company_id)
        )
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(component, field, value)
    component.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(component)
    return component


@router.delete("/payroll/components/{component_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_salary_component(
    component_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a salary component."""
    result = await db.execute(
        select(SalaryComponent).where(
            and_(SalaryComponent.id == component_id, SalaryComponent.company_id == current_user.company_id)
        )
    )
    component = result.scalar_one_or_none()
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    if component.is_statutory:
        raise HTTPException(status_code=400, detail="Cannot delete statutory component")

    await db.delete(component)
    await db.commit()


# ============================================================================
# PF Settings
# ============================================================================

@router.get("/payroll/pf", response_model=PFSettingsResponse)
async def get_pf_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get PF settings."""
    result = await db.execute(
        select(PFSettings).where(PFSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        # Create default settings
        settings = PFSettings(company_id=current_user.company_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/payroll/pf", response_model=PFSettingsResponse)
async def update_pf_settings(
    data: PFSettingsUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update PF settings."""
    result = await db.execute(
        select(PFSettings).where(PFSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PFSettings(company_id=current_user.company_id)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# ESI Settings
# ============================================================================

@router.get("/payroll/esi", response_model=ESISettingsResponse)
async def get_esi_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get ESI settings."""
    result = await db.execute(
        select(ESISettings).where(ESISettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = ESISettings(company_id=current_user.company_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/payroll/esi", response_model=ESISettingsResponse)
async def update_esi_settings(
    data: ESISettingsUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update ESI settings."""
    result = await db.execute(
        select(ESISettings).where(ESISettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = ESISettings(company_id=current_user.company_id)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# PT Settings
# ============================================================================

@router.get("/payroll/pt", response_model=PTSettingsResponse)
async def get_pt_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get PT settings."""
    result = await db.execute(
        select(PTSettings).where(PTSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PTSettings(
            company_id=current_user.company_id,
            slabs=[{"from": 0, "to": 15000, "amount": 0}, {"from": 15001, "to": 999999, "amount": 200}]
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/payroll/pt", response_model=PTSettingsResponse)
async def update_pt_settings(
    data: PTSettingsUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update PT settings."""
    result = await db.execute(
        select(PTSettings).where(PTSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PTSettings(company_id=current_user.company_id)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# TDS Settings
# ============================================================================

@router.get("/payroll/tds", response_model=TDSSettingsResponse)
async def get_tds_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get TDS settings."""
    result = await db.execute(
        select(TDSSettings).where(TDSSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = TDSSettings(company_id=current_user.company_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/payroll/tds", response_model=TDSSettingsResponse)
async def update_tds_settings(
    data: TDSSettingsUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update TDS settings."""
    result = await db.execute(
        select(TDSSettings).where(TDSSettings.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = TDSSettings(company_id=current_user.company_id)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# Pay Schedule
# ============================================================================

@router.get("/payroll/schedule", response_model=PayScheduleResponse)
async def get_pay_schedule(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get pay schedule."""
    result = await db.execute(
        select(PaySchedule).where(PaySchedule.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PaySchedule(company_id=current_user.company_id)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/payroll/schedule", response_model=PayScheduleResponse)
async def update_pay_schedule(
    data: PayScheduleUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update pay schedule."""
    result = await db.execute(
        select(PaySchedule).where(PaySchedule.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PaySchedule(company_id=current_user.company_id)
        db.add(settings)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# Combined Payroll Settings
# ============================================================================

@router.get("/payroll", response_model=PayrollSettingsResponse)
async def get_all_payroll_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get all payroll settings."""
    company_id = current_user.company_id

    # Get all settings
    pf_result = await db.execute(select(PFSettings).where(PFSettings.company_id == company_id))
    esi_result = await db.execute(select(ESISettings).where(ESISettings.company_id == company_id))
    pt_result = await db.execute(select(PTSettings).where(PTSettings.company_id == company_id))
    tds_result = await db.execute(select(TDSSettings).where(TDSSettings.company_id == company_id))
    schedule_result = await db.execute(select(PaySchedule).where(PaySchedule.company_id == company_id))
    components_result = await db.execute(
        select(SalaryComponent).where(SalaryComponent.company_id == company_id).order_by(SalaryComponent.display_order)
    )

    return PayrollSettingsResponse(
        pf=pf_result.scalar_one_or_none(),
        esi=esi_result.scalar_one_or_none(),
        pt=pt_result.scalar_one_or_none(),
        tds=tds_result.scalar_one_or_none(),
        pay_schedule=schedule_result.scalar_one_or_none(),
        salary_components=list(components_result.scalars().all())
    )


# ============================================================================
# Leave Types (Global - not company specific)
# ============================================================================

@router.get("/leave/types", response_model=List[LeaveTypeResponse])
async def list_leave_types(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all leave types (global configuration)."""
    result = await db.execute(
        select(LeaveType)
        .order_by(LeaveType.sort_order, LeaveType.code)
    )
    return result.scalars().all()


@router.post("/leave/types", response_model=LeaveTypeResponse, status_code=status.HTTP_201_CREATED)
async def create_leave_type(
    data: LeaveTypeCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a leave type (admin only)."""
    # Check if code already exists
    existing = await db.execute(
        select(LeaveType).where(LeaveType.code == data.code)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Leave type code already exists")

    leave_type = LeaveType(**data.model_dump())
    db.add(leave_type)
    await db.commit()
    await db.refresh(leave_type)
    return leave_type


@router.put("/leave/types/{type_id}", response_model=LeaveTypeResponse)
async def update_leave_type(
    type_id: uuid.UUID,
    data: LeaveTypeUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a leave type."""
    result = await db.execute(
        select(LeaveType).where(LeaveType.id == type_id)
    )
    leave_type = result.scalar_one_or_none()
    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave type not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(leave_type, field, value)
    leave_type.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(leave_type)
    return leave_type


@router.delete("/leave/types/{type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_leave_type(
    type_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a leave type (cannot delete system types)."""
    result = await db.execute(
        select(LeaveType).where(LeaveType.id == type_id)
    )
    leave_type = result.scalar_one_or_none()
    if not leave_type:
        raise HTTPException(status_code=404, detail="Leave type not found")
    if leave_type.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system leave type")

    await db.delete(leave_type)
    await db.commit()


# ============================================================================
# Holidays
# ============================================================================

@router.get("/leave/holidays", response_model=List[HolidayResponse])
async def list_holidays(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    year: int = Query(default=None)
):
    """List all holidays for the company."""
    from sqlalchemy import extract
    query = select(Holiday).where(Holiday.company_id == current_user.company_id)
    if year:
        query = query.where(extract('year', Holiday.holiday_date) == year)
    query = query.order_by(Holiday.holiday_date)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/leave/holidays", response_model=HolidayResponse, status_code=status.HTTP_201_CREATED)
async def create_holiday(
    data: HolidayCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a holiday."""
    holiday = Holiday(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(holiday)
    await db.commit()
    await db.refresh(holiday)
    return holiday


@router.put("/leave/holidays/{holiday_id}", response_model=HolidayResponse)
async def update_holiday(
    holiday_id: uuid.UUID,
    data: HolidayUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a holiday."""
    result = await db.execute(
        select(Holiday).where(
            and_(Holiday.id == holiday_id, Holiday.company_id == current_user.company_id)
        )
    )
    holiday = result.scalar_one_or_none()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(holiday, field, value)
    holiday.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(holiday)
    return holiday


@router.delete("/leave/holidays/{holiday_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holiday(
    holiday_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a holiday."""
    result = await db.execute(
        select(Holiday).where(
            and_(Holiday.id == holiday_id, Holiday.company_id == current_user.company_id)
        )
    )
    holiday = result.scalar_one_or_none()
    if not holiday:
        raise HTTPException(status_code=404, detail="Holiday not found")

    await db.delete(holiday)
    await db.commit()


# ============================================================================
# Week-Off Settings
# ============================================================================

@router.get("/leave/weekoffs", response_model=WeekOffSettingResponse)
async def get_week_off_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get week-off settings."""
    result = await db.execute(
        select(WeekOffSetting).where(WeekOffSetting.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        # Create default week-off settings
        default_week_offs = [
            {"day": 0, "isOff": True, "isAlternate": False, "alternateWeeks": []},  # Sunday
            {"day": 1, "isOff": False, "isAlternate": False, "alternateWeeks": []},
            {"day": 2, "isOff": False, "isAlternate": False, "alternateWeeks": []},
            {"day": 3, "isOff": False, "isAlternate": False, "alternateWeeks": []},
            {"day": 4, "isOff": False, "isAlternate": False, "alternateWeeks": []},
            {"day": 5, "isOff": False, "isAlternate": False, "alternateWeeks": []},
            {"day": 6, "isOff": True, "isAlternate": True, "alternateWeeks": [2, 4]},  # Saturday
        ]
        settings = WeekOffSetting(company_id=current_user.company_id, week_offs=default_week_offs)
        db.add(settings)
        await db.commit()
        await db.refresh(settings)
    return settings


@router.put("/leave/weekoffs", response_model=WeekOffSettingResponse)
async def update_week_off_settings(
    data: WeekOffSettingUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update week-off settings."""
    result = await db.execute(
        select(WeekOffSetting).where(WeekOffSetting.company_id == current_user.company_id)
    )
    settings = result.scalar_one_or_none()
    if not settings:
        settings = WeekOffSetting(company_id=current_user.company_id)
        db.add(settings)

    settings.week_offs = data.week_offs
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)
    return settings


# ============================================================================
# Combined Leave Settings
# ============================================================================

@router.get("/leave", response_model=LeaveSettingsResponse)
async def get_all_leave_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    year: int = Query(default=None)
):
    """Get all leave settings."""
    from sqlalchemy import extract
    company_id = current_user.company_id

    # Leave types are global (no company filter)
    types_result = await db.execute(
        select(LeaveType).order_by(LeaveType.sort_order)
    )

    holidays_query = select(Holiday).where(Holiday.company_id == company_id)
    if year:
        holidays_query = holidays_query.where(extract('year', Holiday.holiday_date) == year)
    holidays_result = await db.execute(holidays_query.order_by(Holiday.holiday_date))

    weekoffs_result = await db.execute(
        select(WeekOffSetting).where(WeekOffSetting.company_id == company_id)
    )

    return LeaveSettingsResponse(
        leave_types=list(types_result.scalars().all()),
        holidays=list(holidays_result.scalars().all()),
        week_offs=weekoffs_result.scalar_one_or_none()
    )


# ============================================================================
# Shifts
# ============================================================================

@router.get("/attendance/shifts", response_model=List[ShiftResponse])
async def list_shifts(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all shifts."""
    result = await db.execute(
        select(Shift)
        .where(Shift.company_id == current_user.company_id)
        .order_by(Shift.is_default.desc(), Shift.name)
    )
    return result.scalars().all()


@router.post("/attendance/shifts", response_model=ShiftResponse, status_code=status.HTTP_201_CREATED)
async def create_shift(
    data: ShiftCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a shift."""
    shift = Shift(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(shift)
    await db.commit()
    await db.refresh(shift)
    return shift


@router.put("/attendance/shifts/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: uuid.UUID,
    data: ShiftUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a shift."""
    result = await db.execute(
        select(Shift).where(
            and_(Shift.id == shift_id, Shift.company_id == current_user.company_id)
        )
    )
    shift = result.scalar_one_or_none()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(shift, field, value)
    shift.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(shift)
    return shift


@router.delete("/attendance/shifts/{shift_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_shift(
    shift_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a shift."""
    result = await db.execute(
        select(Shift).where(
            and_(Shift.id == shift_id, Shift.company_id == current_user.company_id)
        )
    )
    shift = result.scalar_one_or_none()
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")

    await db.delete(shift)
    await db.commit()


# ============================================================================
# Overtime Rules
# ============================================================================

@router.get("/attendance/overtime-rules", response_model=List[OvertimeRuleResponse])
async def list_overtime_rules(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all overtime rules."""
    result = await db.execute(
        select(OvertimeRule)
        .where(OvertimeRule.company_id == current_user.company_id)
        .order_by(OvertimeRule.name)
    )
    return result.scalars().all()


@router.post("/attendance/overtime-rules", response_model=OvertimeRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_overtime_rule(
    data: OvertimeRuleCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an overtime rule."""
    rule = OvertimeRule(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(rule)
    await db.commit()
    await db.refresh(rule)
    return rule


@router.put("/attendance/overtime-rules/{rule_id}", response_model=OvertimeRuleResponse)
async def update_overtime_rule(
    rule_id: uuid.UUID,
    data: OvertimeRuleUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an overtime rule."""
    result = await db.execute(
        select(OvertimeRule).where(
            and_(OvertimeRule.id == rule_id, OvertimeRule.company_id == current_user.company_id)
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Overtime rule not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rule, field, value)
    rule.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(rule)
    return rule


@router.delete("/attendance/overtime-rules/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_overtime_rule(
    rule_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an overtime rule."""
    result = await db.execute(
        select(OvertimeRule).where(
            and_(OvertimeRule.id == rule_id, OvertimeRule.company_id == current_user.company_id)
        )
    )
    rule = result.scalar_one_or_none()
    if not rule:
        raise HTTPException(status_code=404, detail="Overtime rule not found")

    await db.delete(rule)
    await db.commit()


# ============================================================================
# Attendance Config
# ============================================================================

@router.get("/attendance/config", response_model=AttendanceConfigResponse)
async def get_attendance_config(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get attendance configuration."""
    result = await db.execute(
        select(AttendanceConfig).where(AttendanceConfig.company_id == current_user.company_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        config = AttendanceConfig(company_id=current_user.company_id)
        db.add(config)
        await db.commit()
        await db.refresh(config)
    return config


@router.put("/attendance/config", response_model=AttendanceConfigResponse)
async def update_attendance_config(
    data: AttendanceConfigUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update attendance configuration."""
    result = await db.execute(
        select(AttendanceConfig).where(AttendanceConfig.company_id == current_user.company_id)
    )
    config = result.scalar_one_or_none()
    if not config:
        config = AttendanceConfig(company_id=current_user.company_id)
        db.add(config)

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(config, field, value)
    config.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(config)
    return config


# ============================================================================
# Geo-Fence Locations
# ============================================================================

@router.get("/attendance/geo-fence", response_model=List[GeoFenceLocationResponse])
async def list_geo_fence_locations(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all geo-fence locations."""
    result = await db.execute(
        select(GeoFenceLocation)
        .where(GeoFenceLocation.company_id == current_user.company_id)
        .order_by(GeoFenceLocation.name)
    )
    return result.scalars().all()


@router.post("/attendance/geo-fence", response_model=GeoFenceLocationResponse, status_code=status.HTTP_201_CREATED)
async def create_geo_fence_location(
    data: GeoFenceLocationCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a geo-fence location."""
    location = GeoFenceLocation(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(location)
    await db.commit()
    await db.refresh(location)
    return location


@router.put("/attendance/geo-fence/{location_id}", response_model=GeoFenceLocationResponse)
async def update_geo_fence_location(
    location_id: uuid.UUID,
    data: GeoFenceLocationUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a geo-fence location."""
    result = await db.execute(
        select(GeoFenceLocation).where(
            and_(GeoFenceLocation.id == location_id, GeoFenceLocation.company_id == current_user.company_id)
        )
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(location, field, value)
    location.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(location)
    return location


@router.delete("/attendance/geo-fence/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_geo_fence_location(
    location_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a geo-fence location."""
    result = await db.execute(
        select(GeoFenceLocation).where(
            and_(GeoFenceLocation.id == location_id, GeoFenceLocation.company_id == current_user.company_id)
        )
    )
    location = result.scalar_one_or_none()
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")

    await db.delete(location)
    await db.commit()


# ============================================================================
# Combined Attendance Settings
# ============================================================================

@router.get("/attendance", response_model=AttendanceSettingsResponse)
async def get_all_attendance_settings(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Get all attendance settings."""
    company_id = current_user.company_id

    config_result = await db.execute(
        select(AttendanceConfig).where(AttendanceConfig.company_id == company_id)
    )
    shifts_result = await db.execute(
        select(Shift).where(Shift.company_id == company_id).order_by(Shift.is_default.desc())
    )
    rules_result = await db.execute(
        select(OvertimeRule).where(OvertimeRule.company_id == company_id)
    )
    locations_result = await db.execute(
        select(GeoFenceLocation).where(GeoFenceLocation.company_id == company_id)
    )

    return AttendanceSettingsResponse(
        config=config_result.scalar_one_or_none(),
        shifts=list(shifts_result.scalars().all()),
        overtime_rules=list(rules_result.scalars().all()),
        geo_fence_locations=list(locations_result.scalars().all())
    )


# ============================================================================
# Email Templates
# ============================================================================

@router.get("/email/templates", response_model=List[EmailTemplateResponse])
async def list_email_templates(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    category: Optional[str] = Query(None)
):
    """List all email templates."""
    query = select(EmailTemplate).where(EmailTemplate.company_id == current_user.company_id)
    if category:
        query = query.where(EmailTemplate.category == category)
    query = query.order_by(EmailTemplate.category, EmailTemplate.name)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/email/templates", response_model=EmailTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_email_template(
    data: EmailTemplateCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create an email template."""
    template = EmailTemplate(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


@router.put("/email/templates/{template_id}", response_model=EmailTemplateResponse)
async def update_email_template(
    template_id: uuid.UUID,
    data: EmailTemplateUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update an email template."""
    result = await db.execute(
        select(EmailTemplate).where(
            and_(EmailTemplate.id == template_id, EmailTemplate.company_id == current_user.company_id)
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(template, field, value)
    template.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(template)
    return template


@router.delete("/email/templates/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_email_template(
    template_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete an email template."""
    result = await db.execute(
        select(EmailTemplate).where(
            and_(EmailTemplate.id == template_id, EmailTemplate.company_id == current_user.company_id)
        )
    )
    template = result.scalar_one_or_none()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    await db.delete(template)
    await db.commit()


# ============================================================================
# Roles
# ============================================================================

@router.get("/roles", response_model=List[RoleResponse])
async def list_roles(
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """List all roles."""
    result = await db.execute(
        select(Role)
        .where(Role.company_id == current_user.company_id)
        .order_by(Role.is_system.desc(), Role.name)
    )
    return result.scalars().all()


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
async def create_role(
    data: RoleCreate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Create a role."""
    role = Role(
        company_id=current_user.company_id,
        **data.model_dump()
    )
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


@router.put("/roles/{role_id}", response_model=RoleResponse)
async def update_role(
    role_id: uuid.UUID,
    data: RoleUpdate,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Update a role."""
    result = await db.execute(
        select(Role).where(
            and_(Role.id == role_id, Role.company_id == current_user.company_id)
        )
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(role, field, value)
    role.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(role)
    return role


@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role(
    role_id: uuid.UUID,
    current_user: Annotated[TokenData, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db)
):
    """Delete a role."""
    result = await db.execute(
        select(Role).where(
            and_(Role.id == role_id, Role.company_id == current_user.company_id)
        )
    )
    role = result.scalar_one_or_none()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    if role.is_system:
        raise HTTPException(status_code=400, detail="Cannot delete system role")

    await db.delete(role)
    await db.commit()
