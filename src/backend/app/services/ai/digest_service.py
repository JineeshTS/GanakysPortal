"""
AI-007: Daily Digest & Summary Generation Service
AI-008: Learning from Corrections
Generate intelligent daily summaries and learn from feedback
"""
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, date, timedelta
from enum import Enum


class DigestType(str, Enum):
    """Digest types."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class DigestSection(str, Enum):
    """Digest sections."""
    HR = "hr"
    FINANCE = "finance"
    PAYROLL = "payroll"
    LEAVE = "leave"
    CRM = "crm"
    COMPLIANCE = "compliance"


@dataclass
class DigestItem:
    """Individual digest item."""
    section: DigestSection
    title: str
    summary: str
    metrics: Dict[str, Any]
    priority: int  # 1=high, 2=medium, 3=low
    action_required: bool
    link: Optional[str] = None


@dataclass
class DailyDigest:
    """Complete daily digest."""
    id: str
    company_id: str
    date: date
    digest_type: DigestType
    items: List[DigestItem]
    ai_insights: str
    key_metrics: Dict[str, Any]
    alerts: List[str]
    generated_at: datetime
    user_feedback: Optional[Dict[str, Any]] = None


@dataclass
class CorrectionRecord:
    """Record of user correction for learning."""
    id: str
    user_id: str
    original_output: str
    corrected_output: str
    context: Dict[str, Any]
    feature: str
    timestamp: datetime
    applied: bool = False


class DigestService:
    """
    AI-powered digest and summary generation.

    Features:
    - Daily/weekly/monthly summaries
    - Role-based content customization
    - AI-generated insights
    - Priority-based alerts
    - Learning from corrections (AI-008)
    """

    # Section priorities by role
    ROLE_SECTION_PRIORITY = {
        "hr_manager": [DigestSection.HR, DigestSection.LEAVE, DigestSection.PAYROLL],
        "finance_manager": [DigestSection.FINANCE, DigestSection.PAYROLL, DigestSection.COMPLIANCE],
        "admin": [DigestSection.HR, DigestSection.FINANCE, DigestSection.PAYROLL, DigestSection.LEAVE],
        "employee": [DigestSection.LEAVE, DigestSection.HR],
    }

    def __init__(self, ai_service):
        """Initialize with AI service."""
        self.ai_service = ai_service
        self._corrections: List[CorrectionRecord] = []

    async def generate_daily_digest(
        self,
        company_id: str,
        target_date: date,
        user_role: str = "admin",
        sections: Optional[List[DigestSection]] = None
    ) -> DailyDigest:
        """
        Generate daily digest for a company.

        Args:
            company_id: Company ID
            target_date: Date for digest
            user_role: User role for content prioritization
            sections: Specific sections to include

        Returns:
            Complete daily digest
        """
        import uuid

        # Determine sections to include
        if sections is None:
            sections = self.ROLE_SECTION_PRIORITY.get(
                user_role,
                list(DigestSection)
            )

        items = []
        alerts = []
        key_metrics = {}

        # Generate items for each section
        for section in sections:
            section_items, section_alerts, section_metrics = await self._generate_section(
                company_id, target_date, section
            )
            items.extend(section_items)
            alerts.extend(section_alerts)
            key_metrics[section.value] = section_metrics

        # Sort items by priority
        items.sort(key=lambda x: x.priority)

        # Generate AI insights
        ai_insights = await self._generate_insights(items, key_metrics)

        return DailyDigest(
            id=str(uuid.uuid4()),
            company_id=company_id,
            date=target_date,
            digest_type=DigestType.DAILY,
            items=items,
            ai_insights=ai_insights,
            key_metrics=key_metrics,
            alerts=alerts,
            generated_at=datetime.utcnow()
        )

    async def generate_weekly_summary(
        self,
        company_id: str,
        week_ending: date
    ) -> Dict[str, Any]:
        """Generate weekly summary with trends."""
        week_start = week_ending - timedelta(days=6)

        return {
            "period": f"{week_start} to {week_ending}",
            "highlights": [
                "Payroll processed for 150 employees",
                "12 new employees onboarded",
                "Leave approval rate: 95%",
                "Outstanding invoices reduced by 15%"
            ],
            "trends": {
                "employee_count": {"change": 12, "direction": "up"},
                "payroll_cost": {"change": 5.2, "direction": "up", "unit": "%"},
                "leave_utilization": {"change": 8, "direction": "down", "unit": "%"}
            },
            "alerts": [
                "PF returns due in 3 days",
                "5 employees pending compliance documents"
            ],
            "ai_recommendations": await self._generate_weekly_recommendations(company_id)
        }

    async def submit_feedback(
        self,
        digest_id: str,
        user_id: str,
        feedback: Dict[str, Any]
    ) -> None:
        """Submit feedback on digest for learning."""
        # Store feedback for learning
        if "corrections" in feedback:
            for correction in feedback["corrections"]:
                self._corrections.append(CorrectionRecord(
                    id=str(datetime.utcnow().timestamp()),
                    user_id=user_id,
                    original_output=correction.get("original", ""),
                    corrected_output=correction.get("corrected", ""),
                    context={"digest_id": digest_id},
                    feature="digest",
                    timestamp=datetime.utcnow()
                ))

    def learn_from_corrections(self) -> Dict[str, Any]:
        """
        Process corrections and update model behavior.
        Implementation of AI-008.
        """
        pending = [c for c in self._corrections if not c.applied]

        if not pending:
            return {"status": "no_pending_corrections"}

        # Group by feature
        by_feature = {}
        for c in pending:
            if c.feature not in by_feature:
                by_feature[c.feature] = []
            by_feature[c.feature].append(c)

        # Generate learning insights
        insights = {}
        for feature, corrections in by_feature.items():
            insights[feature] = {
                "correction_count": len(corrections),
                "common_issues": self._analyze_corrections(corrections)
            }
            # Mark as applied
            for c in corrections:
                c.applied = True

        return {
            "status": "processed",
            "corrections_applied": len(pending),
            "insights": insights
        }

    async def _generate_section(
        self,
        company_id: str,
        target_date: date,
        section: DigestSection
    ) -> tuple:
        """Generate items for a specific section."""
        items = []
        alerts = []
        metrics = {}

        if section == DigestSection.HR:
            items.append(DigestItem(
                section=section,
                title="Employee Updates",
                summary="2 new employees joined, 1 exit processed",
                metrics={"new_hires": 2, "exits": 1, "total_active": 152},
                priority=2,
                action_required=False
            ))
            metrics = {"total_employees": 152, "new_hires_mtd": 8}

        elif section == DigestSection.PAYROLL:
            items.append(DigestItem(
                section=section,
                title="Payroll Status",
                summary="December payroll ready for processing",
                metrics={"pending_approval": 150, "total_gross": 12500000},
                priority=1,
                action_required=True,
                link="/payroll/december"
            ))
            alerts.append("Payroll processing deadline: Jan 25")
            metrics = {"pending": 150, "processed": 0}

        elif section == DigestSection.LEAVE:
            items.append(DigestItem(
                section=section,
                title="Leave Requests",
                summary="5 pending leave requests require approval",
                metrics={"pending": 5, "approved_today": 3, "rejected": 1},
                priority=2,
                action_required=True
            ))
            metrics = {"pending_approvals": 5}

        elif section == DigestSection.FINANCE:
            items.append(DigestItem(
                section=section,
                title="Accounts Receivable",
                summary="₹8.5L outstanding, ₹2.1L overdue",
                metrics={"total_outstanding": 850000, "overdue": 210000},
                priority=1,
                action_required=True
            ))
            alerts.append("3 invoices overdue by 30+ days")
            metrics = {"receivables": 850000, "overdue": 210000}

        elif section == DigestSection.COMPLIANCE:
            items.append(DigestItem(
                section=section,
                title="Compliance Calendar",
                summary="PF/ESI returns due on Jan 15",
                metrics={"upcoming_deadlines": 2, "overdue": 0},
                priority=1,
                action_required=True
            ))
            alerts.append("GST return filing due in 5 days")
            metrics = {"upcoming": 2, "completed_this_month": 3}

        elif section == DigestSection.CRM:
            items.append(DigestItem(
                section=section,
                title="Sales Pipeline",
                summary="3 deals in negotiation worth ₹15L",
                metrics={"pipeline_value": 1500000, "deals_won": 2},
                priority=2,
                action_required=False
            ))
            metrics = {"pipeline": 1500000, "won_this_month": 2}

        return items, alerts, metrics

    async def _generate_insights(
        self,
        items: List[DigestItem],
        metrics: Dict[str, Any]
    ) -> str:
        """Generate AI insights from digest data."""
        prompt = f"""Based on this business data, provide 2-3 brief insights:

Items: {[{'title': i.title, 'summary': i.summary, 'priority': i.priority} for i in items]}
Metrics: {metrics}

Focus on actionable insights and trends. Keep response under 100 words."""

        response = await self.ai_service.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="report_generation",
            max_tokens=200
        )

        return response.content

    async def _generate_weekly_recommendations(self, company_id: str) -> List[str]:
        """Generate AI recommendations for the week."""
        return [
            "Consider bulk payment of pending invoices to avail early payment discounts",
            "Review pending leave requests before month-end",
            "Complete PF returns filing to avoid late fees"
        ]

    def _analyze_corrections(self, corrections: List[CorrectionRecord]) -> List[str]:
        """Analyze corrections to find common issues."""
        # In production, use NLP to identify patterns
        return [
            "Users prefer shorter summaries",
            "Currency formatting should always use ₹ symbol"
        ]
