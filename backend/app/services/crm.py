"""
CRM Services - Phase 19
Business logic for lead management, pipeline, and AI features
"""
from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case, extract, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm import (
    Lead, LeadActivity, LeadStageHistory, AIFollowupSuggestion,
    LeadSource, LeadStage, LeadPriority, ActivityType, ActivityOutcome,
    STAGE_PROBABILITY
)
from app.models.customer import Customer
from app.models.user import User
from app.schemas.crm import (
    LeadCreate, LeadUpdate, LeadStageChange, LeadResponse, LeadListResponse,
    ActivityCreate, ActivityResponse,
    PipelineStageStats, PipelineSummary, SalesForecast,
    CRMDashboardStats, OverdueFollowup, AIFollowupSuggestionResponse,
    AILeadScoreResponse, AIEmailDraftResponse, LeadFilters,
)


class LeadService:
    """Service for lead management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_lead_code(self) -> str:
        """Generate unique lead code"""
        year = datetime.now().year
        prefix = f"LD-{year}-"

        # Get the latest lead code for this year
        query = (
            select(Lead.lead_code)
            .where(Lead.lead_code.like(f"{prefix}%"))
            .order_by(Lead.lead_code.desc())
            .limit(1)
        )
        result = await self.db.execute(query)
        last_code = result.scalar_one_or_none()

        if last_code:
            seq = int(last_code.split("-")[-1]) + 1
        else:
            seq = 1

        return f"{prefix}{seq:04d}"

    async def create(
        self,
        data: LeadCreate,
        created_by: UUID
    ) -> Lead:
        """Create a new lead"""
        lead_code = await self.generate_lead_code()

        lead = Lead(
            lead_code=lead_code,
            company_name=data.company_name,
            industry=data.industry,
            company_size=data.company_size,
            website=data.website,
            contact_name=data.contact_name,
            contact_title=data.contact_title,
            contact_email=data.contact_email,
            contact_phone=data.contact_phone,
            contact_linkedin=data.contact_linkedin,
            country=data.country,
            state=data.state,
            city=data.city,
            timezone=data.timezone,
            source=data.source,
            source_details=data.source_details,
            campaign=data.campaign,
            estimated_value=data.estimated_value,
            currency_id=data.currency_id,
            service_interest=data.service_interest,
            project_description=data.project_description,
            estimated_duration=data.estimated_duration,
            stage=LeadStage.NEW,
            probability=STAGE_PROBABILITY[LeadStage.NEW],
            priority=data.priority,
            expected_close_date=data.expected_close_date,
            assigned_to=data.assigned_to,
            notes=data.notes,
            tags=data.tags,
            created_by=created_by
        )

        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)

        # Record stage history
        await self._record_stage_change(
            lead.id, None, LeadStage.NEW, None,
            STAGE_PROBABILITY[LeadStage.NEW], "Lead created", created_by
        )

        return lead

    async def get(self, lead_id: UUID) -> Optional[Lead]:
        """Get lead by ID"""
        query = (
            select(Lead)
            .options(selectinload(Lead.activities))
            .where(Lead.id == lead_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list(
        self,
        filters: Optional[LeadFilters] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Lead], int]:
        """List leads with filters"""
        query = select(Lead)

        if filters:
            if filters.stage:
                query = query.where(Lead.stage.in_(filters.stage))
            if filters.source:
                query = query.where(Lead.source.in_(filters.source))
            if filters.priority:
                query = query.where(Lead.priority.in_(filters.priority))
            if filters.assigned_to:
                query = query.where(Lead.assigned_to == filters.assigned_to)
            if filters.country:
                query = query.where(Lead.country == filters.country)
            if filters.min_value:
                query = query.where(Lead.estimated_value >= filters.min_value)
            if filters.max_value:
                query = query.where(Lead.estimated_value <= filters.max_value)
            if filters.expected_close_from:
                query = query.where(Lead.expected_close_date >= filters.expected_close_from)
            if filters.expected_close_to:
                query = query.where(Lead.expected_close_date <= filters.expected_close_to)
            if filters.created_from:
                query = query.where(func.date(Lead.created_at) >= filters.created_from)
            if filters.created_to:
                query = query.where(func.date(Lead.created_at) <= filters.created_to)
            if filters.search:
                search_term = f"%{filters.search}%"
                query = query.where(
                    or_(
                        Lead.company_name.ilike(search_term),
                        Lead.contact_name.ilike(search_term),
                        Lead.contact_email.ilike(search_term),
                        Lead.lead_code.ilike(search_term)
                    )
                )

        # Count
        count_query = select(func.count()).select_from(query.subquery())
        result = await self.db.execute(count_query)
        total = result.scalar()

        # Fetch with pagination
        query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        result = await self.db.execute(query)
        leads = result.scalars().all()

        return list(leads), total

    async def update(
        self,
        lead_id: UUID,
        data: LeadUpdate,
        updated_by: UUID
    ) -> Optional[Lead]:
        """Update a lead"""
        lead = await self.get(lead_id)
        if not lead:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(lead, field, value)

        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def change_stage(
        self,
        lead_id: UUID,
        data: LeadStageChange,
        changed_by: UUID
    ) -> Optional[Lead]:
        """Change lead stage"""
        lead = await self.get(lead_id)
        if not lead:
            return None

        old_stage = lead.stage
        old_probability = lead.probability

        lead.stage = data.stage
        lead.probability = STAGE_PROBABILITY.get(data.stage, lead.probability)

        if data.stage == LeadStage.LOST:
            lead.lost_reason = data.lost_reason
            lead.lost_to_competitor = data.lost_to_competitor
        elif data.stage == LeadStage.WON:
            lead.won_date = date.today()

        # Record stage change
        await self._record_stage_change(
            lead_id, old_stage, data.stage,
            old_probability, lead.probability,
            data.reason, changed_by
        )

        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def convert_to_customer(
        self,
        lead_id: UUID,
        customer_name: Optional[str],
        converted_by: UUID
    ) -> Tuple[Lead, Customer]:
        """Convert lead to customer"""
        lead = await self.get(lead_id)
        if not lead:
            raise ValueError("Lead not found")

        if lead.stage != LeadStage.WON:
            raise ValueError("Can only convert won leads")

        # Create customer
        from app.models.customer import Customer, CustomerType

        customer = Customer(
            customer_code=f"CUST-{lead.lead_code.replace('LD-', '')}",
            customer_name=customer_name or lead.company_name,
            customer_type=CustomerType.EXPORT if lead.country != "India" else CustomerType.DOMESTIC,
            contact_person=lead.contact_name,
            email=lead.contact_email,
            phone=lead.contact_phone,
            country=lead.country,
            state=lead.state,
            city=lead.city,
            created_by=converted_by
        )
        self.db.add(customer)
        await self.db.flush()

        # Update lead
        lead.converted_customer_id = customer.id
        lead.conversion_date = date.today()

        await self.db.commit()
        return lead, customer

    async def _record_stage_change(
        self,
        lead_id: UUID,
        stage_from: Optional[LeadStage],
        stage_to: LeadStage,
        probability_from: Optional[int],
        probability_to: int,
        reason: Optional[str],
        changed_by: UUID
    ):
        """Record stage change history"""
        history = LeadStageHistory(
            lead_id=lead_id,
            stage_from=stage_from,
            stage_to=stage_to,
            probability_from=probability_from,
            probability_to=probability_to,
            reason=reason,
            changed_by=changed_by
        )
        self.db.add(history)


class ActivityService:
    """Service for lead activities"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(
        self,
        lead_id: UUID,
        data: ActivityCreate,
        created_by: UUID,
        is_ai_generated: bool = False
    ) -> LeadActivity:
        """Create lead activity"""
        activity = LeadActivity(
            lead_id=lead_id,
            activity_type=data.activity_type,
            activity_date=data.activity_date,
            subject=data.subject,
            description=data.description,
            outcome=data.outcome,
            outcome_notes=data.outcome_notes,
            next_action=data.next_action,
            next_action_date=data.next_action_date,
            email_sent_to=data.email_sent_to,
            email_subject=data.email_subject,
            call_duration_minutes=data.call_duration_minutes,
            meeting_attendees=data.meeting_attendees,
            is_ai_generated=is_ai_generated,
            created_by=created_by
        )

        self.db.add(activity)

        # Update lead's last activity
        query = select(Lead).where(Lead.id == lead_id)
        result = await self.db.execute(query)
        lead = result.scalar_one_or_none()

        if lead:
            lead.last_activity_at = data.activity_date
            lead.last_activity_type = data.activity_type
            if data.next_action_date:
                lead.next_followup_date = data.next_action_date
                lead.next_followup_notes = data.next_action

        await self.db.commit()
        await self.db.refresh(activity)
        return activity

    async def list_for_lead(
        self,
        lead_id: UUID,
        skip: int = 0,
        limit: int = 50
    ) -> List[LeadActivity]:
        """List activities for a lead"""
        query = (
            select(LeadActivity)
            .where(LeadActivity.lead_id == lead_id)
            .order_by(LeadActivity.activity_date.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())


class PipelineService:
    """Service for pipeline management"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_pipeline(self) -> PipelineSummary:
        """Get pipeline summary"""
        # Get counts and values by stage
        stage_query = (
            select(
                Lead.stage,
                func.count(Lead.id).label("count"),
                func.coalesce(func.sum(Lead.estimated_value), Decimal("0")).label("total_value")
            )
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
            .group_by(Lead.stage)
        )
        result = await self.db.execute(stage_query)
        stage_data = result.all()

        stages = []
        total_leads = 0
        total_value = Decimal("0")
        weighted_value = Decimal("0")

        for stage, count, value in stage_data:
            stages.append(PipelineStageStats(
                stage=stage,
                count=count,
                total_value=value,
                avg_days_in_stage=None
            ))
            total_leads += count
            total_value += value
            weighted_value += value * STAGE_PROBABILITY.get(stage, 0) / 100

        # Get leads by stage
        leads_query = (
            select(Lead)
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
            .order_by(Lead.estimated_value.desc().nullslast())
        )
        result = await self.db.execute(leads_query)
        leads = result.scalars().all()

        leads_by_stage = {}
        for lead in leads:
            stage_key = lead.stage.value
            if stage_key not in leads_by_stage:
                leads_by_stage[stage_key] = []
            leads_by_stage[stage_key].append(lead)

        return PipelineSummary(
            total_leads=total_leads,
            total_value=total_value,
            weighted_value=weighted_value,
            stages=stages,
            leads_by_stage=leads_by_stage
        )

    async def get_forecast(
        self,
        months_ahead: int = 3
    ) -> List[SalesForecast]:
        """Get sales forecast"""
        forecasts = []
        today = date.today()

        for i in range(months_ahead):
            if i == 0:
                month_start = today.replace(day=1)
            else:
                month_start = (today.replace(day=1) + timedelta(days=32 * i)).replace(day=1)

            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)

            query = (
                select(Lead)
                .where(
                    Lead.expected_close_date >= month_start,
                    Lead.expected_close_date <= month_end,
                    Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
                )
            )
            result = await self.db.execute(query)
            leads = list(result.scalars().all())

            expected_revenue = sum(l.estimated_value or Decimal("0") for l in leads)
            weighted_revenue = sum(
                (l.estimated_value or Decimal("0")) * l.probability / 100
                for l in leads
            )
            high_prob_count = sum(1 for l in leads if l.probability >= 50)

            forecasts.append(SalesForecast(
                period=month_start.strftime("%B %Y"),
                expected_revenue=expected_revenue,
                weighted_revenue=weighted_revenue,
                lead_count=len(leads),
                high_probability_count=high_prob_count,
                closing_this_month=[]  # Would need to convert to LeadListResponse
            ))

        return forecasts


class CRMDashboardService:
    """Service for CRM dashboard"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_dashboard(self) -> CRMDashboardStats:
        """Get CRM dashboard stats"""
        today = date.today()
        month_start = today.replace(day=1)
        week_start = today - timedelta(days=today.weekday())

        # Total leads (active)
        total_query = (
            select(func.count())
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
        )
        result = await self.db.execute(total_query)
        total_leads = result.scalar()

        # New leads this month
        new_query = (
            select(func.count())
            .where(
                Lead.stage == LeadStage.NEW,
                func.date(Lead.created_at) >= month_start
            )
        )
        result = await self.db.execute(new_query)
        new_leads = result.scalar()

        # Qualified leads
        qualified_query = (
            select(func.count())
            .where(Lead.stage == LeadStage.QUALIFIED)
        )
        result = await self.db.execute(qualified_query)
        qualified_leads = result.scalar()

        # In negotiation
        negotiation_query = (
            select(func.count())
            .where(Lead.stage == LeadStage.NEGOTIATION)
        )
        result = await self.db.execute(negotiation_query)
        negotiation_leads = result.scalar()

        # Pipeline values
        value_query = (
            select(
                func.coalesce(func.sum(Lead.estimated_value), Decimal("0")).label("total"),
                func.coalesce(
                    func.sum(Lead.estimated_value * Lead.probability / 100),
                    Decimal("0")
                ).label("weighted")
            )
            .where(Lead.stage.notin_([LeadStage.WON, LeadStage.LOST]))
        )
        result = await self.db.execute(value_query)
        values = result.one()
        total_pipeline = values[0] or Decimal("0")
        weighted_pipeline = values[1] or Decimal("0")

        # Conversion rate
        won_query = select(func.count()).where(Lead.stage == LeadStage.WON)
        lost_query = select(func.count()).where(Lead.stage == LeadStage.LOST)

        won_result = await self.db.execute(won_query)
        lost_result = await self.db.execute(lost_query)

        won_count = won_result.scalar() or 0
        lost_count = lost_result.scalar() or 0

        conversion_rate = Decimal("0")
        if won_count + lost_count > 0:
            conversion_rate = Decimal(won_count * 100) / (won_count + lost_count)

        # Average deal size
        avg_deal_query = (
            select(func.coalesce(func.avg(Lead.estimated_value), Decimal("0")))
            .where(Lead.stage == LeadStage.WON)
        )
        result = await self.db.execute(avg_deal_query)
        avg_deal_size = result.scalar() or Decimal("0")

        # Activities this week
        activity_query = (
            select(func.count())
            .select_from(LeadActivity)
            .where(func.date(LeadActivity.activity_date) >= week_start)
        )
        result = await self.db.execute(activity_query)
        activities_this_week = result.scalar()

        # Overdue followups
        overdue_query = (
            select(func.count())
            .where(
                Lead.next_followup_date < today,
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
        )
        result = await self.db.execute(overdue_query)
        overdue_followups = result.scalar()

        # Leads without activity (7 days)
        inactive_date = today - timedelta(days=7)
        inactive_query = (
            select(func.count())
            .where(
                or_(
                    Lead.last_activity_at < datetime.combine(inactive_date, datetime.min.time()),
                    Lead.last_activity_at.is_(None)
                ),
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
        )
        result = await self.db.execute(inactive_query)
        inactive_leads = result.scalar()

        # Leads by source
        source_query = (
            select(Lead.source, func.count())
            .group_by(Lead.source)
        )
        result = await self.db.execute(source_query)
        leads_by_source = [{"source": s.value, "count": c} for s, c in result.all()]

        # Leads by stage
        stage_query = (
            select(Lead.stage, func.count())
            .group_by(Lead.stage)
        )
        result = await self.db.execute(stage_query)
        leads_by_stage = [{"stage": s.value, "count": c} for s, c in result.all()]

        return CRMDashboardStats(
            total_leads=total_leads,
            new_leads_this_month=new_leads,
            qualified_leads=qualified_leads,
            leads_in_negotiation=negotiation_leads,
            total_pipeline_value=total_pipeline,
            weighted_pipeline_value=weighted_pipeline,
            conversion_rate=conversion_rate,
            avg_deal_size=avg_deal_size,
            avg_sales_cycle_days=30,  # Would need historical data
            activities_this_week=activities_this_week,
            overdue_followups=overdue_followups,
            leads_without_activity_7days=inactive_leads,
            leads_by_source=leads_by_source,
            leads_by_stage=leads_by_stage,
            monthly_trend=[]
        )

    async def get_overdue_followups(self) -> List[OverdueFollowup]:
        """Get overdue followup alerts"""
        today = date.today()

        query = (
            select(Lead)
            .where(
                Lead.next_followup_date < today,
                Lead.stage.notin_([LeadStage.WON, LeadStage.LOST])
            )
            .order_by(Lead.next_followup_date)
            .limit(50)
        )
        result = await self.db.execute(query)
        leads = result.scalars().all()

        overdue = []
        for lead in leads:
            days_overdue = (today - lead.next_followup_date).days
            overdue.append(OverdueFollowup(
                lead_id=lead.id,
                lead_code=lead.lead_code,
                company_name=lead.company_name,
                contact_name=lead.contact_name,
                scheduled_date=lead.next_followup_date,
                days_overdue=days_overdue,
                last_activity=lead.last_activity_type.value if lead.last_activity_type else None,
                assigned_to=None  # Would need to join with users
            ))

        return overdue


class AILeadService:
    """AI-powered lead features"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def calculate_lead_score(self, lead_id: UUID) -> AILeadScoreResponse:
        """Calculate AI lead score"""
        lead = await self._get_lead(lead_id)
        if not lead:
            raise ValueError("Lead not found")

        score = 0
        factors = {}
        recommendations = []

        # Factor 1: Contact completeness (0-15)
        contact_score = 0
        if lead.contact_email:
            contact_score += 5
        if lead.contact_phone:
            contact_score += 5
        if lead.contact_linkedin:
            contact_score += 5
        factors["contact_completeness"] = contact_score
        score += contact_score

        if contact_score < 10:
            recommendations.append("Complete contact information for better engagement")

        # Factor 2: Deal value (0-20)
        value_score = 0
        if lead.estimated_value:
            if lead.estimated_value >= 100000:
                value_score = 20
            elif lead.estimated_value >= 50000:
                value_score = 15
            elif lead.estimated_value >= 10000:
                value_score = 10
            else:
                value_score = 5
        factors["deal_value"] = value_score
        score += value_score

        # Factor 3: Activity level (0-20)
        activity_count = await self._count_activities(lead_id)
        if activity_count >= 10:
            activity_score = 20
        elif activity_count >= 5:
            activity_score = 15
        elif activity_count >= 2:
            activity_score = 10
        elif activity_count >= 1:
            activity_score = 5
        else:
            activity_score = 0
        factors["activity_level"] = activity_score
        score += activity_score

        if activity_score < 10:
            recommendations.append("Increase engagement with more activities")

        # Factor 4: Recency (0-15)
        recency_score = 0
        if lead.last_activity_at:
            days_since = (datetime.now(lead.last_activity_at.tzinfo) - lead.last_activity_at).days
            if days_since <= 3:
                recency_score = 15
            elif days_since <= 7:
                recency_score = 10
            elif days_since <= 14:
                recency_score = 5
        factors["recency"] = recency_score
        score += recency_score

        if recency_score < 10:
            recommendations.append("Schedule a follow-up soon")

        # Factor 5: Stage progression (0-15)
        stage_score = STAGE_PROBABILITY.get(lead.stage, 0) // 7
        factors["stage_progression"] = stage_score
        score += stage_score

        # Factor 6: Source quality (0-15)
        source_scores = {
            LeadSource.REFERRAL: 15,
            LeadSource.INBOUND: 12,
            LeadSource.LINKEDIN: 10,
            LeadSource.WEBSITE: 8,
            LeadSource.CONFERENCE: 8,
            LeadSource.PARTNER: 10,
            LeadSource.MARKETING: 6,
            LeadSource.COLD_OUTREACH: 4,
            LeadSource.OTHER: 5,
        }
        source_score = source_scores.get(lead.source, 5)
        factors["source_quality"] = source_score
        score += source_score

        # Update lead with score
        lead.ai_score = min(score, 100)
        lead.ai_score_factors = factors
        lead.ai_score_updated_at = datetime.utcnow()
        await self.db.commit()

        return AILeadScoreResponse(
            lead_id=lead_id,
            score=min(score, 100),
            factors=factors,
            recommendations=recommendations
        )

    async def generate_followup_suggestions(self, lead_id: UUID) -> List[AIFollowupSuggestionResponse]:
        """Generate AI follow-up suggestions"""
        lead = await self._get_lead(lead_id)
        if not lead:
            raise ValueError("Lead not found")

        suggestions = []

        # Determine suggestion based on stage and history
        if lead.stage == LeadStage.NEW:
            suggestion = AIFollowupSuggestion(
                lead_id=lead_id,
                suggestion_type=ActivityType.EMAIL,
                suggested_date=date.today() + timedelta(days=1),
                subject=f"Introduction and discovery call with {lead.company_name}",
                message_draft=f"""Hi {lead.contact_name},

Thank you for your interest in our services. I'd love to learn more about your requirements and discuss how we can help {lead.company_name}.

Would you be available for a brief 15-minute discovery call this week?

Best regards""",
                reasoning="New leads should be contacted within 24-48 hours for best conversion rates."
            )
            self.db.add(suggestion)

        elif lead.stage == LeadStage.QUALIFIED:
            suggestion = AIFollowupSuggestion(
                lead_id=lead_id,
                suggestion_type=ActivityType.DEMO,
                suggested_date=date.today() + timedelta(days=3),
                subject=f"Product demo for {lead.company_name}",
                message_draft=f"""Hi {lead.contact_name},

Following our discovery call, I'd like to schedule a product demo tailored to your specific needs.

Please let me know your availability for a 30-minute demo session.

Best regards""",
                reasoning="Qualified leads benefit from a personalized demo to move them forward."
            )
            self.db.add(suggestion)

        elif lead.stage == LeadStage.PROPOSAL:
            suggestion = AIFollowupSuggestion(
                lead_id=lead_id,
                suggestion_type=ActivityType.FOLLOW_UP,
                suggested_date=date.today() + timedelta(days=2),
                subject=f"Follow up on proposal for {lead.company_name}",
                message_draft=f"""Hi {lead.contact_name},

I wanted to follow up on the proposal we sent. Do you have any questions or need clarification on any aspects?

I'm happy to schedule a call to discuss the details further.

Best regards""",
                reasoning="Following up on proposals within 2-3 days improves close rates."
            )
            self.db.add(suggestion)

        await self.db.commit()

        # Fetch all pending suggestions
        query = (
            select(AIFollowupSuggestion)
            .where(
                AIFollowupSuggestion.lead_id == lead_id,
                AIFollowupSuggestion.is_dismissed == False,
                AIFollowupSuggestion.is_actioned == False
            )
            .order_by(AIFollowupSuggestion.suggested_date)
        )
        result = await self.db.execute(query)
        return [
            AIFollowupSuggestionResponse(
                id=s.id,
                lead_id=s.lead_id,
                suggestion_type=s.suggestion_type,
                suggested_date=s.suggested_date,
                subject=s.subject,
                message_draft=s.message_draft,
                reasoning=s.reasoning,
                created_at=s.created_at
            )
            for s in result.scalars().all()
        ]

    async def generate_email_draft(
        self,
        lead_id: UUID,
        email_type: str,
        context: Optional[str] = None
    ) -> AIEmailDraftResponse:
        """Generate AI email draft"""
        lead = await self._get_lead(lead_id)
        if not lead:
            raise ValueError("Lead not found")

        templates = {
            "intro": {
                "subject": f"Introduction: Ganakys Codilla Apps - Software Services",
                "body": f"""Dear {lead.contact_name},

I hope this email finds you well. My name is [Your Name] from Ganakys Codilla Apps, and I wanted to reach out regarding your interest in {lead.service_interest or 'our software services'}.

We specialize in delivering high-quality software solutions for businesses like {lead.company_name}. Our team has extensive experience in:
- Custom software development
- SaaS product development
- Cloud solutions and integrations

I'd love to schedule a brief call to understand your specific requirements and discuss how we can help achieve your goals.

Would you be available for a 15-minute call this week?

Best regards,
[Your Name]
Ganakys Codilla Apps"""
            },
            "followup": {
                "subject": f"Following Up: {lead.company_name} - Software Services Discussion",
                "body": f"""Hi {lead.contact_name},

I wanted to follow up on our previous conversation regarding {lead.service_interest or 'your software requirements'}.

I understand you're evaluating options, and I'm here to answer any questions you might have. We'd be happy to:
- Provide additional information about our approach
- Share relevant case studies
- Arrange a technical discussion with our team

Please let me know if there's anything specific you'd like to discuss.

Best regards,
[Your Name]"""
            },
            "proposal": {
                "subject": f"Proposal: {lead.service_interest or 'Software Development Services'} for {lead.company_name}",
                "body": f"""Dear {lead.contact_name},

Thank you for the opportunity to submit our proposal for {lead.service_interest or 'your project requirements'}.

Please find attached our detailed proposal outlining:
- Scope of work and deliverables
- Timeline and milestones
- Team composition
- Investment details

We believe our approach aligns well with your requirements and we're confident in delivering exceptional results.

I'd be happy to schedule a call to walk you through the proposal and answer any questions.

Best regards,
[Your Name]"""
            }
        }

        template = templates.get(email_type, templates["followup"])

        return AIEmailDraftResponse(
            subject=template["subject"],
            body=template["body"],
            suggested_send_time=datetime.now() + timedelta(hours=2)
        )

    async def _get_lead(self, lead_id: UUID) -> Optional[Lead]:
        """Get lead by ID"""
        query = select(Lead).where(Lead.id == lead_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _count_activities(self, lead_id: UUID) -> int:
        """Count activities for a lead"""
        query = select(func.count()).select_from(LeadActivity).where(LeadActivity.lead_id == lead_id)
        result = await self.db.execute(query)
        return result.scalar() or 0
