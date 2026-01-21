"""
Legal Case Management Services
"""
from app.services.legal.counsel_service import counsel_service
from app.services.legal.case_service import case_service
from app.services.legal.hearing_service import hearing_service
from app.services.legal.document_service import document_service
from app.services.legal.party_service import party_service
from app.services.legal.task_service import task_service
from app.services.legal.expense_service import expense_service
from app.services.legal.contract_service import contract_service
from app.services.legal.notice_service import notice_service
from app.services.legal.dashboard_service import dashboard_service

__all__ = [
    "counsel_service",
    "case_service",
    "hearing_service",
    "document_service",
    "party_service",
    "task_service",
    "expense_service",
    "contract_service",
    "notice_service",
    "dashboard_service",
]
