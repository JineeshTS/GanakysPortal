"""
Legal Case Management API Endpoints
"""
from typing import Optional, List
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.schemas.legal import (
    # Counsel
    LegalCounselCreate, LegalCounselUpdate, LegalCounselInDB, LegalCounselList,
    # Case
    LegalCaseCreate, LegalCaseUpdate, LegalCaseInDB, LegalCaseList,
    CaseType, CaseStatus, CasePriority, CourtLevel,
    # Hearing
    LegalHearingCreate, LegalHearingUpdate, LegalHearingInDB, LegalHearingList,
    HearingStatus,
    # Document
    LegalDocumentCreate, LegalDocumentUpdate, LegalDocumentInDB, LegalDocumentList,
    # Party
    LegalPartyCreate, LegalPartyUpdate, LegalPartyInDB,
    # Task
    LegalTaskCreate, LegalTaskUpdate, LegalTaskInDB, LegalTaskList,
    TaskStatus,
    # Expense
    LegalExpenseCreate, LegalExpenseUpdate, LegalExpenseInDB, LegalExpenseList,
    # Contract
    LegalContractCreate, LegalContractUpdate, LegalContractInDB, LegalContractList,
    # Notice
    LegalNoticeCreate, LegalNoticeUpdate, LegalNoticeInDB, LegalNoticeList,
    # Dashboard
    LegalDashboardSummary,
)
from app.services.legal import (
    counsel_service, case_service, hearing_service, document_service,
    party_service, task_service, expense_service, contract_service,
    notice_service, dashboard_service,
)

router = APIRouter()


# ==================== Dashboard ====================

@router.get("/dashboard", response_model=LegalDashboardSummary)
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get legal dashboard summary"""
    return await dashboard_service.get_summary(db, current_user.company_id)


# ==================== Legal Counsels ====================

@router.post("/counsels", response_model=LegalCounselInDB, status_code=status.HTTP_201_CREATED)
async def create_counsel(
    counsel_in: LegalCounselCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new legal counsel"""
    return await counsel_service.create(db, counsel_in, current_user.company_id, current_user.id)


@router.get("/counsels", response_model=LegalCounselList)
async def list_counsels(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    is_empanelled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List legal counsels"""
    items, total = await counsel_service.get_list(
        db, current_user.company_id, page, size, search, is_active, is_empanelled
    )
    return LegalCounselList(items=items, total=total, page=page, size=size)


@router.get("/counsels/{counsel_id}", response_model=LegalCounselInDB)
async def get_counsel(
    counsel_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get legal counsel by ID"""
    counsel = await counsel_service.get(db, counsel_id, current_user.company_id)
    if not counsel:
        raise HTTPException(status_code=404, detail="Counsel not found")
    return counsel


@router.put("/counsels/{counsel_id}", response_model=LegalCounselInDB)
async def update_counsel(
    counsel_id: UUID,
    counsel_in: LegalCounselUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update legal counsel"""
    counsel = await counsel_service.get(db, counsel_id, current_user.company_id)
    if not counsel:
        raise HTTPException(status_code=404, detail="Counsel not found")
    return await counsel_service.update(db, counsel, counsel_in)


# ==================== Legal Cases ====================

@router.post("/cases", response_model=LegalCaseInDB, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_in: LegalCaseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new legal case"""
    return await case_service.create(db, case_in, current_user.company_id, current_user.id)


@router.get("/cases", response_model=LegalCaseList)
async def list_cases(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    case_type: Optional[CaseType] = None,
    status: Optional[CaseStatus] = None,
    priority: Optional[CasePriority] = None,
    court_level: Optional[CourtLevel] = None,
    counsel_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List legal cases"""
    items, total = await case_service.get_list(
        db, current_user.company_id, page, size, search, case_type, status, priority, court_level, counsel_id
    )
    return LegalCaseList(items=items, total=total, page=page, size=size)


@router.get("/cases/{case_id}", response_model=LegalCaseInDB)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get legal case by ID"""
    case = await case_service.get(db, case_id, current_user.company_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.put("/cases/{case_id}", response_model=LegalCaseInDB)
async def update_case(
    case_id: UUID,
    case_in: LegalCaseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update legal case"""
    case = await case_service.get(db, case_id, current_user.company_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return await case_service.update(db, case, case_in)


# ==================== Legal Hearings ====================

@router.post("/hearings", response_model=LegalHearingInDB, status_code=status.HTTP_201_CREATED)
async def create_hearing(
    hearing_in: LegalHearingCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new hearing"""
    return await hearing_service.create(db, hearing_in, current_user.company_id, current_user.id)


@router.get("/hearings", response_model=LegalHearingList)
async def list_hearings(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    case_id: Optional[UUID] = None,
    status: Optional[HearingStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List hearings"""
    items, total = await hearing_service.get_list(
        db, current_user.company_id, page, size, case_id, status, from_date, to_date
    )
    return LegalHearingList(items=items, total=total, page=page, size=size)


@router.get("/hearings/{hearing_id}", response_model=LegalHearingInDB)
async def get_hearing(
    hearing_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get hearing by ID"""
    hearing = await hearing_service.get(db, hearing_id, current_user.company_id)
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
    return hearing


@router.put("/hearings/{hearing_id}", response_model=LegalHearingInDB)
async def update_hearing(
    hearing_id: UUID,
    hearing_in: LegalHearingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update hearing"""
    hearing = await hearing_service.get(db, hearing_id, current_user.company_id)
    if not hearing:
        raise HTTPException(status_code=404, detail="Hearing not found")
    return await hearing_service.update(db, hearing, hearing_in)


# ==================== Legal Documents ====================

@router.post("/documents", response_model=LegalDocumentInDB, status_code=status.HTTP_201_CREATED)
async def create_document(
    document_in: LegalDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new document"""
    return await document_service.create(db, document_in, current_user.company_id, current_user.id)


@router.get("/documents", response_model=LegalDocumentList)
async def list_documents(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    case_id: Optional[UUID] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List documents"""
    items, total = await document_service.get_list(
        db, current_user.company_id, page, size, case_id, category
    )
    return LegalDocumentList(items=items, total=total, page=page, size=size)


@router.get("/documents/{document_id}", response_model=LegalDocumentInDB)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document by ID"""
    document = await document_service.get(db, document_id, current_user.company_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document


@router.put("/documents/{document_id}", response_model=LegalDocumentInDB)
async def update_document(
    document_id: UUID,
    document_in: LegalDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update document"""
    document = await document_service.get(db, document_id, current_user.company_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return await document_service.update(db, document, document_in)


# ==================== Legal Parties ====================

@router.post("/parties", response_model=LegalPartyInDB, status_code=status.HTTP_201_CREATED)
async def create_party(
    party_in: LegalPartyCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add a party to a case"""
    return await party_service.create(db, party_in, current_user.company_id)


@router.get("/parties", response_model=List[LegalPartyInDB])
async def list_parties(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List parties for a case"""
    return await party_service.get_by_case(db, case_id, current_user.company_id)


@router.put("/parties/{party_id}", response_model=LegalPartyInDB)
async def update_party(
    party_id: UUID,
    party_in: LegalPartyUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update party"""
    party = await party_service.get(db, party_id, current_user.company_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    return await party_service.update(db, party, party_in)


@router.delete("/parties/{party_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_party(
    party_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete party"""
    party = await party_service.get(db, party_id, current_user.company_id)
    if not party:
        raise HTTPException(status_code=404, detail="Party not found")
    await party_service.delete(db, party)


# ==================== Legal Tasks ====================

@router.post("/tasks", response_model=LegalTaskInDB, status_code=status.HTTP_201_CREATED)
async def create_task(
    task_in: LegalTaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new task"""
    return await task_service.create(db, task_in, current_user.company_id, current_user.id)


@router.get("/tasks", response_model=LegalTaskList)
async def list_tasks(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    case_id: Optional[UUID] = None,
    assigned_to: Optional[UUID] = None,
    status: Optional[TaskStatus] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks"""
    items, total = await task_service.get_list(
        db, current_user.company_id, page, size, case_id, assigned_to, status, from_date, to_date
    )
    return LegalTaskList(items=items, total=total, page=page, size=size)


@router.get("/tasks/{task_id}", response_model=LegalTaskInDB)
async def get_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get task by ID"""
    task = await task_service.get(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put("/tasks/{task_id}", response_model=LegalTaskInDB)
async def update_task(
    task_id: UUID,
    task_in: LegalTaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update task"""
    task = await task_service.get(db, task_id, current_user.company_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return await task_service.update(db, task, task_in)


# ==================== Legal Expenses ====================

@router.post("/expenses", response_model=LegalExpenseInDB, status_code=status.HTTP_201_CREATED)
async def create_expense(
    expense_in: LegalExpenseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new expense"""
    return await expense_service.create(db, expense_in, current_user.company_id, current_user.id)


@router.get("/expenses", response_model=LegalExpenseList)
async def list_expenses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    case_id: Optional[UUID] = None,
    expense_type: Optional[str] = None,
    payment_status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List expenses"""
    items, total = await expense_service.get_list(
        db, current_user.company_id, page, size, case_id, expense_type, payment_status
    )
    return LegalExpenseList(items=items, total=total, page=page, size=size)


@router.get("/expenses/{expense_id}", response_model=LegalExpenseInDB)
async def get_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get expense by ID"""
    expense = await expense_service.get(db, expense_id, current_user.company_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.put("/expenses/{expense_id}", response_model=LegalExpenseInDB)
async def update_expense(
    expense_id: UUID,
    expense_in: LegalExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update expense"""
    expense = await expense_service.get(db, expense_id, current_user.company_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return await expense_service.update(db, expense, expense_in)


@router.post("/expenses/{expense_id}/approve", response_model=LegalExpenseInDB)
async def approve_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve expense"""
    expense = await expense_service.get(db, expense_id, current_user.company_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return await expense_service.approve(db, expense, current_user.id)


# ==================== Legal Contracts ====================

@router.post("/contracts", response_model=LegalContractInDB, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_in: LegalContractCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new contract"""
    return await contract_service.create(db, contract_in, current_user.company_id, current_user.id)


@router.get("/contracts", response_model=LegalContractList)
async def list_contracts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    contract_type: Optional[str] = None,
    status: Optional[str] = None,
    party_type: Optional[str] = None,
    expiring_in_days: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List contracts"""
    items, total = await contract_service.get_list(
        db, current_user.company_id, page, size, search, contract_type, status, party_type, expiring_in_days
    )
    return LegalContractList(items=items, total=total, page=page, size=size)


@router.get("/contracts/{contract_id}", response_model=LegalContractInDB)
async def get_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get contract by ID"""
    contract = await contract_service.get(db, contract_id, current_user.company_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return contract


@router.put("/contracts/{contract_id}", response_model=LegalContractInDB)
async def update_contract(
    contract_id: UUID,
    contract_in: LegalContractUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update contract"""
    contract = await contract_service.get(db, contract_id, current_user.company_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return await contract_service.update(db, contract, contract_in)


@router.post("/contracts/{contract_id}/approve", response_model=LegalContractInDB)
async def approve_contract(
    contract_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Approve contract"""
    contract = await contract_service.get(db, contract_id, current_user.company_id)
    if not contract:
        raise HTTPException(status_code=404, detail="Contract not found")
    return await contract_service.approve(db, contract, current_user.id)


# ==================== Legal Notices ====================

@router.post("/notices", response_model=LegalNoticeInDB, status_code=status.HTTP_201_CREATED)
async def create_notice(
    notice_in: LegalNoticeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new notice"""
    return await notice_service.create(db, notice_in, current_user.company_id, current_user.id)


@router.get("/notices", response_model=LegalNoticeList)
async def list_notices(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    notice_type: Optional[str] = None,
    direction: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List notices"""
    items, total = await notice_service.get_list(
        db, current_user.company_id, page, size, notice_type, direction, status
    )
    return LegalNoticeList(items=items, total=total, page=page, size=size)


@router.get("/notices/{notice_id}", response_model=LegalNoticeInDB)
async def get_notice(
    notice_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get notice by ID"""
    notice = await notice_service.get(db, notice_id, current_user.company_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return notice


@router.put("/notices/{notice_id}", response_model=LegalNoticeInDB)
async def update_notice(
    notice_id: UUID,
    notice_in: LegalNoticeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update notice"""
    notice = await notice_service.get(db, notice_id, current_user.company_id)
    if not notice:
        raise HTTPException(status_code=404, detail="Notice not found")
    return await notice_service.update(db, notice, notice_in)
