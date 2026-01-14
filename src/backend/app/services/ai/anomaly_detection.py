"""
AI-009: Anomaly Detection Service
AI-010: Smart Suggestions
Detect anomalies in business data and provide intelligent suggestions
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, date, timedelta
from enum import Enum
import statistics


class AnomalyType(str, Enum):
    """Types of anomalies."""
    SPIKE = "spike"
    DROP = "drop"
    UNUSUAL_PATTERN = "unusual_pattern"
    MISSING_DATA = "missing_data"
    DUPLICATE = "duplicate"
    OUTLIER = "outlier"
    SEQUENCE_BREAK = "sequence_break"


class AnomalySeverity(str, Enum):
    """Anomaly severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SuggestionType(str, Enum):
    """Types of smart suggestions."""
    EFFICIENCY = "efficiency"
    COST_SAVING = "cost_saving"
    COMPLIANCE = "compliance"
    PROCESS_IMPROVEMENT = "process_improvement"
    RISK_MITIGATION = "risk_mitigation"


@dataclass
class Anomaly:
    """Detected anomaly."""
    id: str
    type: AnomalyType
    severity: AnomalySeverity
    entity_type: str  # e.g., "payroll", "invoice", "expense"
    entity_id: str
    description: str
    expected_value: Any
    actual_value: Any
    deviation_percentage: float
    detected_at: datetime
    context: Dict[str, Any]
    suggested_action: str
    is_acknowledged: bool = False


@dataclass
class SmartSuggestion:
    """AI-generated smart suggestion."""
    id: str
    type: SuggestionType
    title: str
    description: str
    impact: str
    effort: str  # low, medium, high
    priority: int
    data_basis: Dict[str, Any]
    action_items: List[str]
    estimated_savings: Optional[float] = None


class AnomalyDetectionService:
    """
    AI-powered anomaly detection in business data.

    Features:
    - Statistical anomaly detection
    - Pattern recognition
    - Real-time monitoring
    - Historical comparison
    - Alert generation
    """

    # Thresholds for anomaly detection
    THRESHOLDS = {
        "payroll_variance": 0.15,  # 15% variance triggers alert
        "expense_spike": 2.0,  # 2x average triggers alert
        "invoice_overdue_days": 30,
        "attendance_drop": 0.20,  # 20% attendance drop
    }

    def __init__(self, ai_service=None):
        """Initialize with optional AI service."""
        self.ai_service = ai_service
        self._anomaly_history: List[Anomaly] = []

    async def detect_payroll_anomalies(
        self,
        current_payroll: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> List[Anomaly]:
        """
        Detect anomalies in payroll data.

        Args:
            current_payroll: Current month's payroll data
            historical_data: Past 12 months payroll data

        Returns:
            List of detected anomalies
        """
        anomalies = []

        if not historical_data:
            return anomalies

        # Calculate historical statistics
        historical_gross = [p.get("total_gross", 0) for p in historical_data]
        avg_gross = statistics.mean(historical_gross)
        std_gross = statistics.stdev(historical_gross) if len(historical_gross) > 1 else 0

        current_gross = current_payroll.get("total_gross", 0)

        # Check for significant variance
        if avg_gross > 0:
            variance = abs(current_gross - avg_gross) / avg_gross

            if variance > self.THRESHOLDS["payroll_variance"]:
                anomaly_type = AnomalyType.SPIKE if current_gross > avg_gross else AnomalyType.DROP

                anomalies.append(Anomaly(
                    id=self._generate_id(),
                    type=anomaly_type,
                    severity=AnomalySeverity.HIGH if variance > 0.25 else AnomalySeverity.MEDIUM,
                    entity_type="payroll",
                    entity_id=current_payroll.get("id", ""),
                    description=f"Payroll {'increase' if current_gross > avg_gross else 'decrease'} of {variance*100:.1f}% from average",
                    expected_value=avg_gross,
                    actual_value=current_gross,
                    deviation_percentage=variance * 100,
                    detected_at=datetime.utcnow(),
                    context={
                        "historical_avg": avg_gross,
                        "historical_std": std_gross,
                        "period": current_payroll.get("period", "")
                    },
                    suggested_action="Review payroll changes - check for new hires, exits, or salary revisions"
                ))

        # Check individual employee payroll
        for emp_payroll in current_payroll.get("items", []):
            employee_id = emp_payroll.get("employee_id")
            emp_history = [
                p for h in historical_data
                for p in h.get("items", [])
                if p.get("employee_id") == employee_id
            ]

            if emp_history:
                avg_emp_gross = statistics.mean([p.get("gross", 0) for p in emp_history])
                current_emp_gross = emp_payroll.get("gross", 0)

                if avg_emp_gross > 0:
                    emp_variance = abs(current_emp_gross - avg_emp_gross) / avg_emp_gross

                    if emp_variance > 0.30:  # 30% variance for individual
                        anomalies.append(Anomaly(
                            id=self._generate_id(),
                            type=AnomalyType.OUTLIER,
                            severity=AnomalySeverity.MEDIUM,
                            entity_type="employee_payroll",
                            entity_id=employee_id,
                            description=f"Employee payroll variance of {emp_variance*100:.1f}%",
                            expected_value=avg_emp_gross,
                            actual_value=current_emp_gross,
                            deviation_percentage=emp_variance * 100,
                            detected_at=datetime.utcnow(),
                            context={"employee_id": employee_id},
                            suggested_action="Verify salary components and deductions"
                        ))

        return anomalies

    async def detect_expense_anomalies(
        self,
        expenses: List[Dict[str, Any]],
        category_budgets: Dict[str, float]
    ) -> List[Anomaly]:
        """Detect anomalies in expense data."""
        anomalies = []

        # Group expenses by category
        category_totals: Dict[str, float] = {}
        for expense in expenses:
            category = expense.get("category", "other")
            amount = expense.get("amount", 0)
            category_totals[category] = category_totals.get(category, 0) + amount

        # Check against budgets
        for category, total in category_totals.items():
            budget = category_budgets.get(category, 0)

            if budget > 0:
                utilization = total / budget

                if utilization > 1.0:  # Over budget
                    anomalies.append(Anomaly(
                        id=self._generate_id(),
                        type=AnomalyType.SPIKE,
                        severity=AnomalySeverity.HIGH if utilization > 1.25 else AnomalySeverity.MEDIUM,
                        entity_type="expense_category",
                        entity_id=category,
                        description=f"Category '{category}' is {(utilization-1)*100:.1f}% over budget",
                        expected_value=budget,
                        actual_value=total,
                        deviation_percentage=(utilization - 1) * 100,
                        detected_at=datetime.utcnow(),
                        context={"category": category, "budget": budget},
                        suggested_action=f"Review {category} expenses and implement cost controls"
                    ))

        # Check for duplicate expenses
        seen_expenses: Dict[str, List[Dict]] = {}
        for expense in expenses:
            key = f"{expense.get('vendor', '')}_{expense.get('amount', 0)}_{expense.get('date', '')}"
            if key in seen_expenses:
                anomalies.append(Anomaly(
                    id=self._generate_id(),
                    type=AnomalyType.DUPLICATE,
                    severity=AnomalySeverity.MEDIUM,
                    entity_type="expense",
                    entity_id=expense.get("id", ""),
                    description=f"Possible duplicate expense: {expense.get('description', '')}",
                    expected_value=1,
                    actual_value=len(seen_expenses[key]) + 1,
                    deviation_percentage=100,
                    detected_at=datetime.utcnow(),
                    context={"similar_expenses": seen_expenses[key]},
                    suggested_action="Verify if this is a legitimate expense or duplicate entry"
                ))
            seen_expenses.setdefault(key, []).append(expense)

        return anomalies

    async def detect_attendance_anomalies(
        self,
        attendance_data: List[Dict[str, Any]],
        department: Optional[str] = None
    ) -> List[Anomaly]:
        """Detect attendance pattern anomalies."""
        anomalies = []

        # Check for unusual absence patterns
        employee_absences: Dict[str, int] = {}
        for record in attendance_data:
            if record.get("status") == "absent":
                emp_id = record.get("employee_id")
                employee_absences[emp_id] = employee_absences.get(emp_id, 0) + 1

        # Flag employees with high absences
        for emp_id, absences in employee_absences.items():
            if absences > 3:  # More than 3 absences in period
                anomalies.append(Anomaly(
                    id=self._generate_id(),
                    type=AnomalyType.UNUSUAL_PATTERN,
                    severity=AnomalySeverity.LOW if absences <= 5 else AnomalySeverity.MEDIUM,
                    entity_type="attendance",
                    entity_id=emp_id,
                    description=f"Employee has {absences} absences this period",
                    expected_value=2,
                    actual_value=absences,
                    deviation_percentage=((absences - 2) / 2) * 100,
                    detected_at=datetime.utcnow(),
                    context={"employee_id": emp_id, "department": department},
                    suggested_action="Review attendance and discuss with employee if needed"
                ))

        return anomalies

    def acknowledge_anomaly(self, anomaly_id: str, user_id: str, notes: str = "") -> bool:
        """Acknowledge an anomaly as reviewed."""
        for anomaly in self._anomaly_history:
            if anomaly.id == anomaly_id:
                anomaly.is_acknowledged = True
                anomaly.context["acknowledged_by"] = user_id
                anomaly.context["acknowledged_at"] = datetime.utcnow().isoformat()
                anomaly.context["notes"] = notes
                return True
        return False

    def _generate_id(self) -> str:
        """Generate unique anomaly ID."""
        import uuid
        return str(uuid.uuid4())[:8]


class SmartSuggestionService:
    """
    AI-010: Smart Suggestions Service

    Generate intelligent suggestions based on business data analysis.
    """

    def __init__(self, ai_service=None):
        """Initialize with optional AI service."""
        self.ai_service = ai_service

    async def generate_suggestions(
        self,
        company_data: Dict[str, Any],
        focus_areas: Optional[List[SuggestionType]] = None
    ) -> List[SmartSuggestion]:
        """
        Generate smart suggestions based on company data.

        Args:
            company_data: Company metrics and data
            focus_areas: Specific areas to focus on

        Returns:
            List of prioritized suggestions
        """
        suggestions = []

        # Cost saving suggestions
        if not focus_areas or SuggestionType.COST_SAVING in focus_areas:
            suggestions.extend(await self._cost_saving_suggestions(company_data))

        # Efficiency suggestions
        if not focus_areas or SuggestionType.EFFICIENCY in focus_areas:
            suggestions.extend(await self._efficiency_suggestions(company_data))

        # Compliance suggestions
        if not focus_areas or SuggestionType.COMPLIANCE in focus_areas:
            suggestions.extend(await self._compliance_suggestions(company_data))

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority)

        return suggestions

    async def _cost_saving_suggestions(
        self,
        data: Dict[str, Any]
    ) -> List[SmartSuggestion]:
        """Generate cost-saving suggestions."""
        suggestions = []

        # Check overtime costs
        overtime_cost = data.get("overtime_cost", 0)
        if overtime_cost > 50000:  # Rs. 50,000
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.COST_SAVING,
                title="Reduce Overtime Costs",
                description=f"Current overtime spending is ₹{overtime_cost:,.0f}. Consider workload redistribution.",
                impact="Potential 20-30% reduction in overtime costs",
                effort="medium",
                priority=2,
                data_basis={"overtime_cost": overtime_cost},
                action_items=[
                    "Analyze departments with highest overtime",
                    "Review project timelines and deadlines",
                    "Consider hiring additional resources for peak periods"
                ],
                estimated_savings=overtime_cost * 0.25
            ))

        # Check vendor consolidation
        vendor_count = data.get("active_vendors", 0)
        if vendor_count > 50:
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.COST_SAVING,
                title="Vendor Consolidation Opportunity",
                description=f"You have {vendor_count} active vendors. Consolidation could yield better rates.",
                impact="Potential 5-10% savings on procurement",
                effort="high",
                priority=3,
                data_basis={"vendor_count": vendor_count},
                action_items=[
                    "Identify vendors with overlapping services",
                    "Analyze spending by vendor category",
                    "Negotiate volume discounts with key vendors"
                ]
            ))

        return suggestions

    async def _efficiency_suggestions(
        self,
        data: Dict[str, Any]
    ) -> List[SmartSuggestion]:
        """Generate efficiency suggestions."""
        suggestions = []

        # Check approval bottlenecks
        pending_approvals = data.get("pending_approvals", 0)
        if pending_approvals > 20:
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.EFFICIENCY,
                title="Streamline Approval Process",
                description=f"{pending_approvals} items pending approval. Consider delegation or auto-approval rules.",
                impact="Reduce approval cycle time by 50%",
                effort="low",
                priority=1,
                data_basis={"pending_approvals": pending_approvals},
                action_items=[
                    "Set up auto-approval for low-value items",
                    "Configure approval delegation during absence",
                    "Review and update approval hierarchies"
                ]
            ))

        # Check invoice processing time
        avg_invoice_days = data.get("avg_invoice_processing_days", 0)
        if avg_invoice_days > 5:
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.EFFICIENCY,
                title="Speed Up Invoice Processing",
                description=f"Average invoice processing takes {avg_invoice_days} days. Consider automation.",
                impact="Improve vendor relationships and capture early payment discounts",
                effort="medium",
                priority=2,
                data_basis={"avg_processing_days": avg_invoice_days},
                action_items=[
                    "Implement OCR for invoice data extraction",
                    "Set up 3-way matching automation",
                    "Configure payment scheduling"
                ]
            ))

        return suggestions

    async def _compliance_suggestions(
        self,
        data: Dict[str, Any]
    ) -> List[SmartSuggestion]:
        """Generate compliance suggestions."""
        suggestions = []

        # Check pending compliance items
        pending_filings = data.get("pending_filings", [])
        if pending_filings:
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.COMPLIANCE,
                title="Upcoming Compliance Deadlines",
                description=f"{len(pending_filings)} filings due soon. Set up reminders and prepare documents.",
                impact="Avoid penalties and maintain compliance status",
                effort="low",
                priority=1,
                data_basis={"pending_filings": pending_filings},
                action_items=[
                    "Review and complete pending documentation",
                    "Set up automated compliance calendar",
                    "Assign compliance owners for each filing type"
                ]
            ))

        # Check document expiries
        expiring_docs = data.get("expiring_documents", 0)
        if expiring_docs > 0:
            suggestions.append(SmartSuggestion(
                id=self._generate_id(),
                type=SuggestionType.COMPLIANCE,
                title="Renew Expiring Documents",
                description=f"{expiring_docs} documents expiring in next 30 days.",
                impact="Maintain operational continuity and compliance",
                effort="low",
                priority=1,
                data_basis={"expiring_count": expiring_docs},
                action_items=[
                    "Review list of expiring documents",
                    "Initiate renewal process",
                    "Update document management system"
                ]
            ))

        return suggestions

    def _generate_id(self) -> str:
        """Generate unique suggestion ID."""
        import uuid
        return str(uuid.uuid4())[:8]
