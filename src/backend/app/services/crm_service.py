"""
CRM Service - Business Logic
Lead, Contact, Customer, Opportunity, and Activity management
India-specific with GSTIN validation and state-wise distribution
"""
import uuid
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, and_, or_, case, extract
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.crm import (
    Lead, Contact, Customer, Opportunity, Activity, Note, Pipeline,
    LeadSource, LeadStatus, OpportunityStage, ActivityType, EntityType,
    GSTRegistrationType, PaymentTerms,
    DEFAULT_STAGE_PROBABILITIES, INDIAN_STATE_CODES,
    validate_gstin, get_state_from_gstin, format_inr
)
from app.schemas.crm import (
    LeadCreate, LeadUpdate, LeadStatusUpdate, LeadConvertRequest,
    ContactCreate, ContactUpdate,
    CustomerCreate, CustomerUpdate,
    OpportunityCreate, OpportunityUpdate, OpportunityStageUpdate,
    ActivityCreate, ActivityUpdate, ActivityCompleteRequest, FollowUpRequest,
    NoteCreate, NoteUpdate,
    PipelineSummary, PipelineStageData,
    SalesForecast, SalesForecastResponse,
    DashboardMetrics, SalesFunnelReport, SalesFunnelStage,
    Customer360View, CustomerTransactionSummary,
    StateWiseDistribution, StateWiseReport
)


class CRMService:
    """
    CRM business logic service.
    Handles all CRM operations including lead management, customer management,
    opportunities, activities, and reporting.
    """

    # ========================================================================
    # Lead Management
    # ========================================================================

    @classmethod
    async def create_lead(
        cls,
        db: AsyncSession,
        company_id: UUID,
        lead_data: LeadCreate,
        created_by: UUID
    ) -> Lead:
        """
        Create a new lead with auto-generated lead number.

        Args:
            db: Database session
            company_id: Company ID
            lead_data: Lead creation data
            created_by: User ID creating the lead

        Returns:
            Created Lead instance
        """
        # Generate lead number: LD-YYYYMM-XXXX
        lead_number = await cls._generate_lead_number(db, company_id)

        lead = Lead(
            id=uuid.uuid4(),
            company_id=company_id,
            lead_number=lead_number,
            company_name=lead_data.company_name,
            industry=lead_data.industry,
            company_size=lead_data.company_size,
            website=lead_data.website,
            contact_name=lead_data.contact_name,
            email=lead_data.email,
            phone=lead_data.phone,
            mobile=lead_data.mobile,
            designation=lead_data.designation,
            address=lead_data.address,
            city=lead_data.city,
            state=lead_data.state,
            pincode=lead_data.pincode,
            country=lead_data.country,
            source=lead_data.source,
            status=LeadStatus.NEW,
            score=0,
            expected_value=lead_data.expected_value or Decimal("0"),
            expected_close_date=lead_data.expected_close_date,
            assigned_to=lead_data.assigned_to,
            campaign_id=lead_data.campaign_id,
            campaign_name=lead_data.campaign_name,
            description=lead_data.description,
            requirements=lead_data.requirements,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Calculate initial lead score
        lead.score = cls._calculate_lead_score_internal(lead)
        lead.rating = cls._get_rating_from_score(lead.score)

        db.add(lead)
        await db.flush()
        await db.refresh(lead)

        return lead

    @classmethod
    async def update_lead(
        cls,
        db: AsyncSession,
        lead_id: UUID,
        company_id: UUID,
        lead_data: LeadUpdate,
        updated_by: UUID
    ) -> Optional[Lead]:
        """Update an existing lead."""
        lead = await cls.get_lead_by_id(db, lead_id, company_id)
        if not lead:
            return None

        # Update fields if provided
        update_fields = lead_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(lead, field):
                setattr(lead, field, value)

        lead.updated_by = updated_by
        lead.updated_at = datetime.utcnow()

        # Recalculate score
        lead.score = cls._calculate_lead_score_internal(lead)
        lead.rating = cls._get_rating_from_score(lead.score)

        await db.flush()
        await db.refresh(lead)

        return lead

    @classmethod
    async def update_lead_stage(
        cls,
        db: AsyncSession,
        lead_id: UUID,
        company_id: UUID,
        status_update: LeadStatusUpdate,
        updated_by: UUID
    ) -> Optional[Lead]:
        """Update lead status/stage."""
        lead = await cls.get_lead_by_id(db, lead_id, company_id)
        if not lead:
            return None

        lead.status = status_update.status
        lead.updated_by = updated_by
        lead.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(lead)

        return lead

    @classmethod
    async def get_lead_by_id(
        cls,
        db: AsyncSession,
        lead_id: UUID,
        company_id: UUID
    ) -> Optional[Lead]:
        """Get a lead by ID."""
        result = await db.execute(
            select(Lead).where(
                and_(
                    Lead.id == lead_id,
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_leads(
        cls,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        limit: int = 20,
        status: Optional[LeadStatus] = None,
        source: Optional[LeadSource] = None,
        assigned_to: Optional[UUID] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Lead], int]:
        """List leads with filters and pagination."""
        query = select(Lead).where(
            and_(
                Lead.company_id == company_id,
                Lead.deleted_at.is_(None)
            )
        )

        # Apply filters
        if status:
            query = query.where(Lead.status == status)
        if source:
            query = query.where(Lead.source == source)
        if assigned_to:
            query = query.where(Lead.assigned_to == assigned_to)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Lead.contact_name.ilike(search_term),
                    Lead.company_name.ilike(search_term),
                    Lead.email.ilike(search_term),
                    Lead.lead_number.ilike(search_term)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Lead, sort_by, Lead.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        leads = result.scalars().all()

        return list(leads), total

    @classmethod
    def calculate_lead_score(cls, lead: Lead) -> Dict[str, Any]:
        """
        Calculate lead score with breakdown of factors.

        Scoring factors:
        - Company info completeness: 0-20 points
        - Contact info completeness: 0-20 points
        - Expected value: 0-20 points
        - Source quality: 0-15 points
        - Engagement (activities): 0-15 points
        - Recency: 0-10 points
        """
        score = cls._calculate_lead_score_internal(lead)
        rating = cls._get_rating_from_score(score)

        factors = {
            "company_info": cls._score_company_info(lead),
            "contact_info": cls._score_contact_info(lead),
            "expected_value": cls._score_expected_value(lead),
            "source_quality": cls._score_source(lead),
            "recency": cls._score_recency(lead),
        }

        return {
            "lead_id": lead.id,
            "score": score,
            "rating": rating,
            "factors": factors
        }

    @classmethod
    def _calculate_lead_score_internal(cls, lead: Lead) -> int:
        """Calculate lead score internally."""
        score = 0
        score += cls._score_company_info(lead)
        score += cls._score_contact_info(lead)
        score += cls._score_expected_value(lead)
        score += cls._score_source(lead)
        score += cls._score_recency(lead)
        return min(score, 100)

    @classmethod
    def _score_company_info(cls, lead: Lead) -> int:
        """Score based on company information completeness."""
        score = 0
        if lead.company_name:
            score += 8
        if lead.industry:
            score += 4
        if lead.company_size:
            score += 4
        if lead.website:
            score += 4
        return min(score, 20)

    @classmethod
    def _score_contact_info(cls, lead: Lead) -> int:
        """Score based on contact information completeness."""
        score = 0
        if lead.contact_name:
            score += 5
        if lead.email:
            score += 6
        if lead.phone or lead.mobile:
            score += 5
        if lead.designation:
            score += 4
        return min(score, 20)

    @classmethod
    def _score_expected_value(cls, lead: Lead) -> int:
        """Score based on expected deal value."""
        if not lead.expected_value:
            return 0

        value = float(lead.expected_value)
        if value >= 1000000:  # 10 Lakh+
            return 20
        elif value >= 500000:  # 5 Lakh+
            return 15
        elif value >= 100000:  # 1 Lakh+
            return 10
        elif value >= 50000:
            return 5
        return 2

    @classmethod
    def _score_source(cls, lead: Lead) -> int:
        """Score based on lead source quality."""
        source_scores = {
            LeadSource.REFERRAL: 15,
            LeadSource.PARTNER: 14,
            LeadSource.WEBSITE: 12,
            LeadSource.TRADE_SHOW: 11,
            LeadSource.INDIAMART: 10,
            LeadSource.JUSTDIAL: 10,
            LeadSource.GOOGLE_ADS: 9,
            LeadSource.EMAIL_CAMPAIGN: 8,
            LeadSource.SOCIAL_MEDIA: 7,
            LeadSource.COLD_CALL: 5,
            LeadSource.ADVERTISEMENT: 6,
            LeadSource.OTHER: 3
        }
        return source_scores.get(lead.source, 5)

    @classmethod
    def _score_recency(cls, lead: Lead) -> int:
        """Score based on lead recency."""
        if not lead.created_at:
            return 0

        days_old = (datetime.utcnow() - lead.created_at).days
        if days_old <= 7:
            return 10
        elif days_old <= 14:
            return 8
        elif days_old <= 30:
            return 5
        elif days_old <= 60:
            return 3
        return 1

    @classmethod
    def _get_rating_from_score(cls, score: int) -> str:
        """Get rating from score."""
        if score >= 70:
            return "hot"
        elif score >= 40:
            return "warm"
        return "cold"

    @classmethod
    async def convert_lead_to_customer(
        cls,
        db: AsyncSession,
        lead_id: UUID,
        company_id: UUID,
        convert_data: LeadConvertRequest,
        converted_by: UUID
    ) -> Dict[str, Any]:
        """
        Convert a lead to a customer, optionally creating an opportunity.

        Args:
            db: Database session
            lead_id: Lead ID to convert
            company_id: Company ID
            convert_data: Conversion data
            converted_by: User ID performing conversion

        Returns:
            Dictionary with customer_id, opportunity_id (if created), and customer_code
        """
        lead = await cls.get_lead_by_id(db, lead_id, company_id)
        if not lead:
            raise ValueError("Lead not found")

        if lead.status == LeadStatus.CONVERTED:
            raise ValueError("Lead is already converted")

        # Generate customer code
        customer_code = convert_data.customer_code or await cls._generate_customer_code(db, company_id)

        # Derive state from GSTIN if provided
        state = None
        state_code = None
        if convert_data.gstin:
            state = get_state_from_gstin(convert_data.gstin)
            state_code = convert_data.gstin[:2] if convert_data.gstin else None
        elif lead.state:
            state = lead.state

        # Create customer
        customer = Customer(
            id=uuid.uuid4(),
            company_id=company_id,
            customer_code=customer_code,
            company_name=lead.company_name or lead.contact_name,
            display_name=lead.company_name or lead.contact_name,
            gstin=convert_data.gstin,
            pan=convert_data.pan,
            gst_registration_type=GSTRegistrationType.REGULAR,
            state=state,
            state_code=state_code,
            billing_address_line1=lead.address,
            billing_city=lead.city,
            billing_state=lead.state,
            billing_pincode=lead.pincode,
            billing_country=lead.country or "India",
            shipping_same_as_billing=True,
            credit_limit=convert_data.credit_limit,
            payment_terms=convert_data.payment_terms,
            credit_days=30,
            industry=lead.industry,
            primary_email=lead.email,
            primary_phone=lead.phone or lead.mobile,
            website=lead.website,
            converted_from_lead_id=lead.id,
            is_active=True,
            created_by=converted_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(customer)

        # Create primary contact
        contact = Contact(
            id=uuid.uuid4(),
            company_id=company_id,
            customer_id=customer.id,
            name=lead.contact_name,
            email=lead.email,
            phone=lead.phone,
            mobile=lead.mobile,
            designation=lead.designation,
            is_primary=True,
            is_active=True,
            created_by=converted_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(contact)

        opportunity_id = None
        opportunity_number = None

        # Create opportunity if requested
        if convert_data.create_opportunity:
            opportunity_number = await cls._generate_opportunity_number(db, company_id)
            opportunity_value = convert_data.opportunity_value or lead.expected_value or Decimal("0")

            opportunity = Opportunity(
                id=uuid.uuid4(),
                company_id=company_id,
                opportunity_number=opportunity_number,
                title=convert_data.opportunity_title or f"Opportunity from {lead.company_name or lead.contact_name}",
                lead_id=lead.id,
                customer_id=customer.id,
                value=opportunity_value,
                probability=DEFAULT_STAGE_PROBABILITIES[OpportunityStage.QUALIFICATION],
                weighted_value=opportunity_value * Decimal("0.20"),
                currency="INR",
                stage=OpportunityStage.QUALIFICATION,
                stage_changed_at=datetime.utcnow(),
                expected_close_date=lead.expected_close_date,
                source=lead.source,
                owner_id=lead.assigned_to or converted_by,
                description=lead.description,
                requirements=lead.requirements,
                created_by=converted_by,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(opportunity)
            opportunity_id = opportunity.id
            lead.converted_opportunity_id = opportunity.id

        # Update lead status
        lead.status = LeadStatus.CONVERTED
        lead.converted_at = datetime.utcnow()
        lead.converted_customer_id = customer.id
        lead.updated_by = converted_by
        lead.updated_at = datetime.utcnow()

        await db.flush()

        return {
            "lead_id": lead.id,
            "customer_id": customer.id,
            "opportunity_id": opportunity_id,
            "customer_code": customer_code,
            "message": f"Lead converted successfully to customer {customer_code}"
        }

    @classmethod
    async def _generate_lead_number(cls, db: AsyncSession, company_id: UUID) -> str:
        """Generate unique lead number: LD-YYYYMM-XXXX."""
        prefix = datetime.now().strftime("LD-%Y%m-")

        result = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.lead_number.like(f"{prefix}%")
                )
            )
        )
        count = result.scalar() or 0

        return f"{prefix}{(count + 1):04d}"

    # ========================================================================
    # Contact Management
    # ========================================================================

    @classmethod
    async def create_contact(
        cls,
        db: AsyncSession,
        company_id: UUID,
        contact_data: ContactCreate,
        created_by: UUID
    ) -> Contact:
        """Create a new contact for a customer."""
        # Verify customer exists
        customer = await cls.get_customer_by_id(db, contact_data.customer_id, company_id)
        if not customer:
            raise ValueError("Customer not found")

        # If this is primary, unset other primary contacts
        if contact_data.is_primary:
            await cls._unset_primary_contacts(db, contact_data.customer_id)

        contact = Contact(
            id=uuid.uuid4(),
            company_id=company_id,
            customer_id=contact_data.customer_id,
            name=contact_data.name,
            email=contact_data.email,
            phone=contact_data.phone,
            mobile=contact_data.mobile,
            designation=contact_data.designation,
            department=contact_data.department,
            is_primary=contact_data.is_primary,
            is_billing_contact=contact_data.is_billing_contact,
            is_shipping_contact=contact_data.is_shipping_contact,
            is_decision_maker=contact_data.is_decision_maker,
            preferred_contact_method=contact_data.preferred_contact_method,
            best_time_to_call=contact_data.best_time_to_call,
            linkedin_url=contact_data.linkedin_url,
            notes=contact_data.notes,
            is_active=True,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(contact)
        await db.flush()
        await db.refresh(contact)

        return contact

    @classmethod
    async def update_contact(
        cls,
        db: AsyncSession,
        contact_id: UUID,
        company_id: UUID,
        contact_data: ContactUpdate,
        updated_by: UUID
    ) -> Optional[Contact]:
        """Update an existing contact."""
        result = await db.execute(
            select(Contact).where(
                and_(
                    Contact.id == contact_id,
                    Contact.company_id == company_id
                )
            )
        )
        contact = result.scalar_one_or_none()
        if not contact:
            return None

        # If setting as primary, unset others
        if contact_data.is_primary:
            await cls._unset_primary_contacts(db, contact.customer_id)

        update_fields = contact_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(contact, field):
                setattr(contact, field, value)

        contact.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(contact)

        return contact

    @classmethod
    async def get_contact_by_id(
        cls,
        db: AsyncSession,
        contact_id: UUID,
        company_id: UUID
    ) -> Optional[Contact]:
        """Get a contact by ID."""
        result = await db.execute(
            select(Contact).where(
                and_(
                    Contact.id == contact_id,
                    Contact.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_contacts(
        cls,
        db: AsyncSession,
        company_id: UUID,
        customer_id: Optional[UUID] = None,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        is_active: Optional[bool] = True
    ) -> Tuple[List[Contact], int]:
        """List contacts with filters and pagination."""
        query = select(Contact).where(Contact.company_id == company_id)

        if customer_id:
            query = query.where(Contact.customer_id == customer_id)
        if is_active is not None:
            query = query.where(Contact.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Contact.name.ilike(search_term),
                    Contact.email.ilike(search_term)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply pagination
        offset = (page - 1) * limit
        query = query.order_by(Contact.created_at.desc()).offset(offset).limit(limit)

        result = await db.execute(query)
        contacts = result.scalars().all()

        return list(contacts), total

    @classmethod
    async def _unset_primary_contacts(cls, db: AsyncSession, customer_id: UUID) -> None:
        """Unset all primary contacts for a customer."""
        result = await db.execute(
            select(Contact).where(
                and_(
                    Contact.customer_id == customer_id,
                    Contact.is_primary == True
                )
            )
        )
        for contact in result.scalars():
            contact.is_primary = False

    # ========================================================================
    # Customer Management
    # ========================================================================

    @classmethod
    async def create_customer(
        cls,
        db: AsyncSession,
        company_id: UUID,
        customer_data: CustomerCreate,
        created_by: UUID
    ) -> Customer:
        """Create a new customer."""
        customer_code = customer_data.customer_code or await cls._generate_customer_code(db, company_id)

        # Derive state from GSTIN
        state = None
        state_code = None
        if customer_data.gstin:
            state = get_state_from_gstin(customer_data.gstin)
            state_code = customer_data.gstin[:2]

        customer = Customer(
            id=uuid.uuid4(),
            company_id=company_id,
            customer_code=customer_code,
            company_name=customer_data.company_name,
            display_name=customer_data.display_name or customer_data.company_name,
            gstin=customer_data.gstin,
            pan=customer_data.pan,
            gst_registration_type=customer_data.gst_registration_type,
            tan=customer_data.tan,
            cin=customer_data.cin,
            state=state,
            state_code=state_code,
            tds_applicable=customer_data.tds_applicable,
            tds_section=customer_data.tds_section,
            tds_rate=customer_data.tds_rate,
            credit_limit=customer_data.credit_limit,
            payment_terms=customer_data.payment_terms,
            credit_days=customer_data.credit_days,
            customer_type=customer_data.customer_type,
            industry=customer_data.industry,
            segment=customer_data.segment,
            primary_email=customer_data.primary_email,
            primary_phone=customer_data.primary_phone,
            website=customer_data.website,
            bank_name=customer_data.bank_name,
            bank_account_number=customer_data.bank_account_number,
            bank_ifsc=customer_data.bank_ifsc,
            bank_branch=customer_data.bank_branch,
            account_manager_id=customer_data.account_manager_id,
            shipping_same_as_billing=customer_data.shipping_same_as_billing,
            is_active=True,
            notes=customer_data.notes,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Set billing address
        if customer_data.billing_address:
            customer.billing_address_line1 = customer_data.billing_address.address_line1
            customer.billing_address_line2 = customer_data.billing_address.address_line2
            customer.billing_city = customer_data.billing_address.city
            customer.billing_state = customer_data.billing_address.state
            customer.billing_pincode = customer_data.billing_address.pincode
            customer.billing_country = customer_data.billing_address.country

        # Set shipping address
        if customer_data.shipping_address and not customer_data.shipping_same_as_billing:
            customer.shipping_address_line1 = customer_data.shipping_address.address_line1
            customer.shipping_address_line2 = customer_data.shipping_address.address_line2
            customer.shipping_city = customer_data.shipping_address.city
            customer.shipping_state = customer_data.shipping_address.state
            customer.shipping_pincode = customer_data.shipping_address.pincode
            customer.shipping_country = customer_data.shipping_address.country

        db.add(customer)
        await db.flush()
        await db.refresh(customer)

        return customer

    @classmethod
    async def update_customer(
        cls,
        db: AsyncSession,
        customer_id: UUID,
        company_id: UUID,
        customer_data: CustomerUpdate,
        updated_by: UUID
    ) -> Optional[Customer]:
        """Update an existing customer."""
        customer = await cls.get_customer_by_id(db, customer_id, company_id)
        if not customer:
            return None

        update_fields = customer_data.model_dump(exclude_unset=True, exclude={'billing_address', 'shipping_address'})
        for field, value in update_fields.items():
            if hasattr(customer, field):
                setattr(customer, field, value)

        # Update GSTIN-derived state
        if customer_data.gstin:
            customer.state = get_state_from_gstin(customer_data.gstin)
            customer.state_code = customer_data.gstin[:2]

        # Update billing address
        if customer_data.billing_address:
            customer.billing_address_line1 = customer_data.billing_address.address_line1
            customer.billing_address_line2 = customer_data.billing_address.address_line2
            customer.billing_city = customer_data.billing_address.city
            customer.billing_state = customer_data.billing_address.state
            customer.billing_pincode = customer_data.billing_address.pincode
            customer.billing_country = customer_data.billing_address.country

        # Update shipping address
        if customer_data.shipping_address:
            customer.shipping_address_line1 = customer_data.shipping_address.address_line1
            customer.shipping_address_line2 = customer_data.shipping_address.address_line2
            customer.shipping_city = customer_data.shipping_address.city
            customer.shipping_state = customer_data.shipping_address.state
            customer.shipping_pincode = customer_data.shipping_address.pincode
            customer.shipping_country = customer_data.shipping_address.country

        customer.updated_by = updated_by
        customer.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(customer)

        return customer

    @classmethod
    async def get_customer_by_id(
        cls,
        db: AsyncSession,
        customer_id: UUID,
        company_id: UUID
    ) -> Optional[Customer]:
        """Get a customer by ID."""
        result = await db.execute(
            select(Customer).where(
                and_(
                    Customer.id == customer_id,
                    Customer.company_id == company_id,
                    Customer.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_customers(
        cls,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        limit: int = 20,
        state: Optional[str] = None,
        is_active: Optional[bool] = True,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Customer], int]:
        """List customers with filters and pagination."""
        query = select(Customer).where(
            and_(
                Customer.company_id == company_id,
                Customer.deleted_at.is_(None)
            )
        )

        if state:
            query = query.where(Customer.state == state)
        if is_active is not None:
            query = query.where(Customer.is_active == is_active)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Customer.company_name.ilike(search_term),
                    Customer.customer_code.ilike(search_term),
                    Customer.gstin.ilike(search_term),
                    Customer.primary_email.ilike(search_term)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Customer, sort_by, Customer.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        customers = result.scalars().all()

        return list(customers), total

    @classmethod
    async def get_customer_360_view(
        cls,
        db: AsyncSession,
        customer_id: UUID,
        company_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get complete 360-degree view of a customer.
        Includes customer details, contacts, opportunities, activities, and transaction summary.
        """
        customer = await cls.get_customer_by_id(db, customer_id, company_id)
        if not customer:
            return None

        # Get contacts
        contacts, _ = await cls.list_contacts(db, company_id, customer_id=customer_id, limit=100)

        # Get opportunities
        opportunities, _ = await cls.list_opportunities(db, company_id, customer_id=customer_id, limit=100)

        # Get recent activities
        activities, _ = await cls.list_activities(
            db, company_id,
            entity_type=EntityType.CUSTOMER,
            entity_id=customer_id,
            limit=10
        )

        # Calculate transaction summary (placeholder - would integrate with invoice/payment models)
        transaction_summary = {
            "customer_id": customer_id,
            "total_invoices": 0,
            "total_invoice_amount": Decimal("0"),
            "total_payments": 0,
            "total_payment_amount": Decimal("0"),
            "outstanding_amount": customer.outstanding_receivable,
            "overdue_amount": Decimal("0"),
            "last_invoice_date": None,
            "last_payment_date": None
        }

        return {
            "customer": customer,
            "contacts": contacts,
            "opportunities": opportunities,
            "recent_activities": activities,
            "transaction_summary": transaction_summary
        }

    @classmethod
    async def get_state_wise_distribution(
        cls,
        db: AsyncSession,
        company_id: UUID
    ) -> List[Dict[str, Any]]:
        """Get state-wise customer distribution."""
        result = await db.execute(
            select(
                Customer.state,
                Customer.state_code,
                func.count(Customer.id).label('customer_count'),
                func.coalesce(func.sum(Customer.total_revenue), 0).label('total_revenue'),
                func.coalesce(func.sum(Customer.outstanding_receivable), 0).label('outstanding_amount')
            )
            .where(
                and_(
                    Customer.company_id == company_id,
                    Customer.deleted_at.is_(None),
                    Customer.state.isnot(None)
                )
            )
            .group_by(Customer.state, Customer.state_code)
            .order_by(func.count(Customer.id).desc())
        )

        rows = result.all()
        total_customers = sum(row.customer_count for row in rows)

        distribution = []
        for row in rows:
            distribution.append({
                "state": row.state,
                "state_code": row.state_code,
                "customer_count": row.customer_count,
                "total_revenue": row.total_revenue,
                "outstanding_amount": row.outstanding_amount,
                "percentage": (row.customer_count / total_customers * 100) if total_customers > 0 else 0
            })

        return distribution

    @classmethod
    async def _generate_customer_code(cls, db: AsyncSession, company_id: UUID) -> str:
        """Generate unique customer code: CUST-XXXX."""
        result = await db.execute(
            select(func.count())
            .select_from(Customer)
            .where(Customer.company_id == company_id)
        )
        count = result.scalar() or 0

        return f"CUST-{(count + 1):04d}"

    # ========================================================================
    # Opportunity Management
    # ========================================================================

    @classmethod
    async def create_opportunity(
        cls,
        db: AsyncSession,
        company_id: UUID,
        opportunity_data: OpportunityCreate,
        created_by: UUID
    ) -> Opportunity:
        """Create a new opportunity."""
        opportunity_number = await cls._generate_opportunity_number(db, company_id)

        probability = opportunity_data.probability
        value = opportunity_data.value or Decimal("0")
        weighted_value = value * Decimal(str(probability)) / Decimal("100")

        opportunity = Opportunity(
            id=uuid.uuid4(),
            company_id=company_id,
            opportunity_number=opportunity_number,
            title=opportunity_data.title,
            lead_id=opportunity_data.lead_id,
            customer_id=opportunity_data.customer_id,
            value=value,
            probability=probability,
            weighted_value=weighted_value,
            currency=opportunity_data.currency,
            stage=OpportunityStage.PROSPECTING,
            stage_changed_at=datetime.utcnow(),
            expected_close_date=opportunity_data.expected_close_date,
            source=opportunity_data.source,
            owner_id=opportunity_data.owner_id or created_by,
            campaign_id=opportunity_data.campaign_id,
            next_step=opportunity_data.next_step,
            next_step_date=opportunity_data.next_step_date,
            description=opportunity_data.description,
            competitors=opportunity_data.competitors,
            requirements=opportunity_data.requirements,
            products=opportunity_data.products,
            is_closed=False,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.add(opportunity)
        await db.flush()
        await db.refresh(opportunity)

        return opportunity

    @classmethod
    async def update_opportunity(
        cls,
        db: AsyncSession,
        opportunity_id: UUID,
        company_id: UUID,
        opportunity_data: OpportunityUpdate,
        updated_by: UUID
    ) -> Optional[Opportunity]:
        """Update an existing opportunity."""
        opportunity = await cls.get_opportunity_by_id(db, opportunity_id, company_id)
        if not opportunity:
            return None

        update_fields = opportunity_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(opportunity, field):
                setattr(opportunity, field, value)

        # Recalculate weighted value
        opportunity.weighted_value = opportunity.value * Decimal(str(opportunity.probability)) / Decimal("100")

        opportunity.updated_by = updated_by
        opportunity.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(opportunity)

        return opportunity

    @classmethod
    async def update_opportunity_stage(
        cls,
        db: AsyncSession,
        opportunity_id: UUID,
        company_id: UUID,
        stage_update: OpportunityStageUpdate,
        updated_by: UUID
    ) -> Optional[Opportunity]:
        """Update opportunity stage with automatic probability adjustment."""
        opportunity = await cls.get_opportunity_by_id(db, opportunity_id, company_id)
        if not opportunity:
            return None

        old_stage = opportunity.stage
        new_stage = stage_update.stage

        opportunity.stage = new_stage
        opportunity.stage_changed_at = datetime.utcnow()

        # Update probability based on stage
        opportunity.probability = DEFAULT_STAGE_PROBABILITIES.get(new_stage, 10)
        opportunity.weighted_value = opportunity.value * Decimal(str(opportunity.probability)) / Decimal("100")

        # Handle closed stages
        if new_stage in [OpportunityStage.CLOSED_WON, OpportunityStage.CLOSED_LOST]:
            opportunity.is_closed = True
            opportunity.is_won = new_stage == OpportunityStage.CLOSED_WON
            opportunity.actual_close_date = date.today()
            opportunity.close_reason = stage_update.close_reason
            if new_stage == OpportunityStage.CLOSED_LOST:
                opportunity.competitor_lost_to = stage_update.competitor_lost_to

        opportunity.updated_by = updated_by
        opportunity.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(opportunity)

        return opportunity

    @classmethod
    async def get_opportunity_by_id(
        cls,
        db: AsyncSession,
        opportunity_id: UUID,
        company_id: UUID
    ) -> Optional[Opportunity]:
        """Get an opportunity by ID."""
        result = await db.execute(
            select(Opportunity).where(
                and_(
                    Opportunity.id == opportunity_id,
                    Opportunity.company_id == company_id,
                    Opportunity.deleted_at.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_opportunities(
        cls,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        limit: int = 20,
        stage: Optional[OpportunityStage] = None,
        customer_id: Optional[UUID] = None,
        owner_id: Optional[UUID] = None,
        is_closed: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Opportunity], int]:
        """List opportunities with filters and pagination."""
        query = select(Opportunity).where(
            and_(
                Opportunity.company_id == company_id,
                Opportunity.deleted_at.is_(None)
            )
        )

        if stage:
            query = query.where(Opportunity.stage == stage)
        if customer_id:
            query = query.where(Opportunity.customer_id == customer_id)
        if owner_id:
            query = query.where(Opportunity.owner_id == owner_id)
        if is_closed is not None:
            query = query.where(Opportunity.is_closed == is_closed)
        if search:
            search_term = f"%{search}%"
            query = query.where(
                or_(
                    Opportunity.title.ilike(search_term),
                    Opportunity.opportunity_number.ilike(search_term)
                )
            )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Opportunity, sort_by, Opportunity.created_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        opportunities = result.scalars().all()

        return list(opportunities), total

    @classmethod
    async def get_pipeline_summary(
        cls,
        db: AsyncSession,
        company_id: UUID,
        owner_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Get pipeline summary grouped by stage.
        Returns count, value, and weighted value for each stage.
        """
        query = select(
            Opportunity.stage,
            func.count(Opportunity.id).label('count'),
            func.coalesce(func.sum(Opportunity.value), 0).label('total_value'),
            func.coalesce(func.sum(Opportunity.weighted_value), 0).label('weighted_value')
        ).where(
            and_(
                Opportunity.company_id == company_id,
                Opportunity.deleted_at.is_(None),
                Opportunity.is_closed == False
            )
        )

        if owner_id:
            query = query.where(Opportunity.owner_id == owner_id)

        query = query.group_by(Opportunity.stage)
        result = await db.execute(query)
        rows = result.all()

        stages = []
        total_opportunities = 0
        total_value = Decimal("0")
        total_weighted = Decimal("0")

        for row in rows:
            stages.append({
                "stage": row.stage.value,
                "count": row.count,
                "total_value": row.total_value,
                "weighted_value": row.weighted_value,
                "opportunities": []  # Would fetch if needed
            })
            total_opportunities += row.count
            total_value += row.total_value
            total_weighted += row.weighted_value

        # Calculate conversion rate
        won_count = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_won == True
                )
            )
        )
        won = won_count.scalar() or 0

        total_closed = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_closed == True
                )
            )
        )
        closed = total_closed.scalar() or 0

        conversion_rate = (won / closed * 100) if closed > 0 else 0
        avg_deal_size = (total_value / total_opportunities) if total_opportunities > 0 else Decimal("0")

        return {
            "total_opportunities": total_opportunities,
            "total_value": total_value,
            "total_weighted_value": total_weighted,
            "stages": stages,
            "conversion_rate": round(conversion_rate, 2),
            "average_deal_size": avg_deal_size
        }

    @classmethod
    async def get_sales_forecast(
        cls,
        db: AsyncSession,
        company_id: UUID,
        forecast_months: int = 6
    ) -> Dict[str, Any]:
        """
        Get sales forecast based on expected close dates.
        Groups opportunities by month and calculates expected vs weighted values.
        """
        today = date.today()
        forecasts = []

        for i in range(forecast_months):
            month_start = date(today.year, today.month, 1)
            if today.month + i > 12:
                month_start = date(today.year + 1, (today.month + i) % 12 or 12, 1)
            else:
                month_start = date(today.year, today.month + i, 1)

            if month_start.month == 12:
                month_end = date(month_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                month_end = date(month_start.year, month_start.month + 1, 1) - timedelta(days=1)

            # Get opportunities expected to close in this month
            result = await db.execute(
                select(
                    func.count(Opportunity.id).label('count'),
                    func.coalesce(func.sum(Opportunity.value), 0).label('expected_value'),
                    func.coalesce(func.sum(Opportunity.weighted_value), 0).label('weighted_value')
                )
                .where(
                    and_(
                        Opportunity.company_id == company_id,
                        Opportunity.deleted_at.is_(None),
                        Opportunity.is_closed == False,
                        Opportunity.expected_close_date >= month_start,
                        Opportunity.expected_close_date <= month_end
                    )
                )
            )
            row = result.one()

            # Get won value for the month
            won_result = await db.execute(
                select(func.coalesce(func.sum(Opportunity.value), 0))
                .where(
                    and_(
                        Opportunity.company_id == company_id,
                        Opportunity.is_won == True,
                        Opportunity.actual_close_date >= month_start,
                        Opportunity.actual_close_date <= month_end
                    )
                )
            )
            won_value = won_result.scalar() or Decimal("0")

            # Get lost value for the month
            lost_result = await db.execute(
                select(func.coalesce(func.sum(Opportunity.value), 0))
                .where(
                    and_(
                        Opportunity.company_id == company_id,
                        Opportunity.is_closed == True,
                        Opportunity.is_won == False,
                        Opportunity.actual_close_date >= month_start,
                        Opportunity.actual_close_date <= month_end
                    )
                )
            )
            lost_value = lost_result.scalar() or Decimal("0")

            forecasts.append({
                "period": month_start.strftime("%Y-%m"),
                "expected_value": row.expected_value,
                "weighted_value": row.weighted_value,
                "opportunity_count": row.count,
                "won_value": won_value,
                "lost_value": lost_value
            })

        total_forecast = sum(f["expected_value"] for f in forecasts)
        total_weighted = sum(f["weighted_value"] for f in forecasts)

        return {
            "forecast_period": "monthly",
            "forecasts": forecasts,
            "total_forecast": total_forecast,
            "total_weighted": total_weighted
        }

    @classmethod
    async def _generate_opportunity_number(cls, db: AsyncSession, company_id: UUID) -> str:
        """Generate unique opportunity number: OP-YYYYMM-XXXX."""
        prefix = datetime.now().strftime("OP-%Y%m-")

        result = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.opportunity_number.like(f"{prefix}%")
                )
            )
        )
        count = result.scalar() or 0

        return f"{prefix}{(count + 1):04d}"

    # ========================================================================
    # Activity Management
    # ========================================================================

    @classmethod
    async def create_activity(
        cls,
        db: AsyncSession,
        company_id: UUID,
        activity_data: ActivityCreate,
        created_by: UUID
    ) -> Activity:
        """Create a new activity."""
        activity = Activity(
            id=uuid.uuid4(),
            company_id=company_id,
            entity_type=activity_data.entity_type,
            entity_id=activity_data.entity_id,
            type=activity_data.type,
            subject=activity_data.subject,
            description=activity_data.description,
            scheduled_at=activity_data.scheduled_at,
            duration_minutes=activity_data.duration_minutes,
            is_all_day=activity_data.is_all_day,
            location=activity_data.location,
            meeting_link=activity_data.meeting_link,
            owner_id=created_by,
            assigned_to=activity_data.assigned_to or created_by,
            status="scheduled",
            priority=activity_data.priority,
            reminder_at=activity_data.reminder_at,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Set direct foreign keys based on entity type
        if activity_data.entity_type == EntityType.LEAD:
            activity.lead_id = activity_data.entity_id
        elif activity_data.entity_type == EntityType.OPPORTUNITY:
            activity.opportunity_id = activity_data.entity_id
        elif activity_data.entity_type == EntityType.CUSTOMER:
            activity.customer_id = activity_data.entity_id

        db.add(activity)
        await db.flush()
        await db.refresh(activity)

        return activity

    @classmethod
    async def update_activity(
        cls,
        db: AsyncSession,
        activity_id: UUID,
        company_id: UUID,
        activity_data: ActivityUpdate,
        updated_by: UUID
    ) -> Optional[Activity]:
        """Update an existing activity."""
        activity = await cls.get_activity_by_id(db, activity_id, company_id)
        if not activity:
            return None

        update_fields = activity_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(activity, field):
                setattr(activity, field, value)

        activity.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(activity)

        return activity

    @classmethod
    async def complete_activity(
        cls,
        db: AsyncSession,
        activity_id: UUID,
        company_id: UUID,
        complete_data: ActivityCompleteRequest,
        completed_by: UUID
    ) -> Optional[Activity]:
        """Mark an activity as completed."""
        activity = await cls.get_activity_by_id(db, activity_id, company_id)
        if not activity:
            return None

        activity.status = "completed"
        activity.completed_at = complete_data.completed_at or datetime.utcnow()
        activity.outcome = complete_data.outcome
        activity.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(activity)

        return activity

    @classmethod
    async def schedule_followup(
        cls,
        db: AsyncSession,
        company_id: UUID,
        followup_data: FollowUpRequest,
        created_by: UUID
    ) -> Activity:
        """Schedule a follow-up activity."""
        activity_data = ActivityCreate(
            entity_type=followup_data.entity_type,
            entity_id=followup_data.entity_id,
            type=followup_data.activity_type,
            subject=followup_data.subject,
            description=followup_data.description,
            scheduled_at=followup_data.scheduled_at,
            assigned_to=followup_data.assigned_to,
            reminder_at=followup_data.reminder_at,
            priority="normal"
        )

        return await cls.create_activity(db, company_id, activity_data, created_by)

    @classmethod
    async def get_activity_by_id(
        cls,
        db: AsyncSession,
        activity_id: UUID,
        company_id: UUID
    ) -> Optional[Activity]:
        """Get an activity by ID."""
        result = await db.execute(
            select(Activity).where(
                and_(
                    Activity.id == activity_id,
                    Activity.company_id == company_id
                )
            )
        )
        return result.scalar_one_or_none()

    @classmethod
    async def list_activities(
        cls,
        db: AsyncSession,
        company_id: UUID,
        page: int = 1,
        limit: int = 20,
        entity_type: Optional[EntityType] = None,
        entity_id: Optional[UUID] = None,
        activity_type: Optional[ActivityType] = None,
        status: Optional[str] = None,
        owner_id: Optional[UUID] = None,
        scheduled_from: Optional[datetime] = None,
        scheduled_to: Optional[datetime] = None,
        sort_by: str = "scheduled_at",
        sort_order: str = "asc"
    ) -> Tuple[List[Activity], int]:
        """List activities with filters and pagination."""
        query = select(Activity).where(Activity.company_id == company_id)

        if entity_type:
            query = query.where(Activity.entity_type == entity_type)
        if entity_id:
            query = query.where(Activity.entity_id == entity_id)
        if activity_type:
            query = query.where(Activity.type == activity_type)
        if status:
            query = query.where(Activity.status == status)
        if owner_id:
            query = query.where(Activity.owner_id == owner_id)
        if scheduled_from:
            query = query.where(Activity.scheduled_at >= scheduled_from)
        if scheduled_to:
            query = query.where(Activity.scheduled_at <= scheduled_to)

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply sorting
        sort_column = getattr(Activity, sort_by, Activity.scheduled_at)
        if sort_order == "desc":
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())

        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)

        result = await db.execute(query)
        activities = result.scalars().all()

        return list(activities), total

    @classmethod
    async def get_upcoming_activities(
        cls,
        db: AsyncSession,
        company_id: UUID,
        user_id: UUID,
        days: int = 7,
        limit: int = 20
    ) -> List[Activity]:
        """Get upcoming activities for a user within the specified days."""
        now = datetime.utcnow()
        end_date = now + timedelta(days=days)

        result = await db.execute(
            select(Activity)
            .where(
                and_(
                    Activity.company_id == company_id,
                    or_(
                        Activity.owner_id == user_id,
                        Activity.assigned_to == user_id
                    ),
                    Activity.status.in_(["scheduled", "in_progress"]),
                    Activity.scheduled_at >= now,
                    Activity.scheduled_at <= end_date
                )
            )
            .order_by(Activity.scheduled_at.asc())
            .limit(limit)
        )

        return list(result.scalars().all())

    # ========================================================================
    # Note Management
    # ========================================================================

    @classmethod
    async def create_note(
        cls,
        db: AsyncSession,
        company_id: UUID,
        note_data: NoteCreate,
        created_by: UUID
    ) -> Note:
        """Create a new note."""
        note = Note(
            id=uuid.uuid4(),
            company_id=company_id,
            entity_type=note_data.entity_type,
            entity_id=note_data.entity_id,
            content=note_data.content,
            is_pinned=note_data.is_pinned,
            is_private=note_data.is_private,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        # Set direct foreign keys based on entity type
        if note_data.entity_type == EntityType.LEAD:
            note.lead_id = note_data.entity_id
        elif note_data.entity_type == EntityType.OPPORTUNITY:
            note.opportunity_id = note_data.entity_id
        elif note_data.entity_type == EntityType.CUSTOMER:
            note.customer_id = note_data.entity_id

        db.add(note)
        await db.flush()
        await db.refresh(note)

        return note

    @classmethod
    async def update_note(
        cls,
        db: AsyncSession,
        note_id: UUID,
        company_id: UUID,
        note_data: NoteUpdate,
        updated_by: UUID
    ) -> Optional[Note]:
        """Update an existing note."""
        result = await db.execute(
            select(Note).where(
                and_(
                    Note.id == note_id,
                    Note.company_id == company_id,
                    Note.created_by == updated_by  # Only creator can update
                )
            )
        )
        note = result.scalar_one_or_none()
        if not note:
            return None

        update_fields = note_data.model_dump(exclude_unset=True)
        for field, value in update_fields.items():
            if hasattr(note, field):
                setattr(note, field, value)

        note.updated_at = datetime.utcnow()

        await db.flush()
        await db.refresh(note)

        return note

    @classmethod
    async def delete_note(
        cls,
        db: AsyncSession,
        note_id: UUID,
        company_id: UUID,
        deleted_by: UUID
    ) -> bool:
        """Delete a note (only by creator)."""
        result = await db.execute(
            select(Note).where(
                and_(
                    Note.id == note_id,
                    Note.company_id == company_id,
                    Note.created_by == deleted_by
                )
            )
        )
        note = result.scalar_one_or_none()
        if not note:
            return False

        await db.delete(note)
        await db.flush()

        return True

    @classmethod
    async def list_notes(
        cls,
        db: AsyncSession,
        company_id: UUID,
        entity_type: EntityType,
        entity_id: UUID,
        user_id: UUID,
        page: int = 1,
        limit: int = 20
    ) -> Tuple[List[Note], int]:
        """List notes for an entity (excluding private notes from other users)."""
        query = select(Note).where(
            and_(
                Note.company_id == company_id,
                Note.entity_type == entity_type,
                Note.entity_id == entity_id,
                or_(
                    Note.is_private == False,
                    Note.created_by == user_id
                )
            )
        )

        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar() or 0

        # Apply ordering and pagination
        offset = (page - 1) * limit
        query = query.order_by(Note.is_pinned.desc(), Note.created_at.desc()).offset(offset).limit(limit)

        result = await db.execute(query)
        notes = result.scalars().all()

        return list(notes), total

    # ========================================================================
    # Dashboard and Reports
    # ========================================================================

    @classmethod
    async def get_dashboard_metrics(
        cls,
        db: AsyncSession,
        company_id: UUID
    ) -> Dict[str, Any]:
        """Get CRM dashboard metrics."""
        today = date.today()
        month_start = date(today.year, today.month, 1)

        # Lead metrics
        total_leads = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None)
                )
            )
        )

        new_leads_this_month = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None),
                    Lead.created_at >= month_start
                )
            )
        )

        leads_by_status = await db.execute(
            select(Lead.status, func.count())
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None)
                )
            )
            .group_by(Lead.status)
        )

        leads_by_source = await db.execute(
            select(Lead.source, func.count())
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None)
                )
            )
            .group_by(Lead.source)
        )

        # Customer metrics
        total_customers = await db.execute(
            select(func.count())
            .select_from(Customer)
            .where(
                and_(
                    Customer.company_id == company_id,
                    Customer.deleted_at.is_(None)
                )
            )
        )

        new_customers_this_month = await db.execute(
            select(func.count())
            .select_from(Customer)
            .where(
                and_(
                    Customer.company_id == company_id,
                    Customer.deleted_at.is_(None),
                    Customer.created_at >= month_start
                )
            )
        )

        customers_by_state = await db.execute(
            select(Customer.state, func.count())
            .where(
                and_(
                    Customer.company_id == company_id,
                    Customer.deleted_at.is_(None),
                    Customer.state.isnot(None)
                )
            )
            .group_by(Customer.state)
        )

        # Opportunity metrics
        total_opportunities = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.deleted_at.is_(None)
                )
            )
        )

        open_opportunities = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.deleted_at.is_(None),
                    Opportunity.is_closed == False
                )
            )
        )

        pipeline_values = await db.execute(
            select(
                func.coalesce(func.sum(Opportunity.value), 0),
                func.coalesce(func.sum(Opportunity.weighted_value), 0)
            )
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.deleted_at.is_(None),
                    Opportunity.is_closed == False
                )
            )
        )

        opportunities_by_stage = await db.execute(
            select(Opportunity.stage, func.count())
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.deleted_at.is_(None),
                    Opportunity.is_closed == False
                )
            )
            .group_by(Opportunity.stage)
        )

        won_this_month = await db.execute(
            select(func.count(), func.coalesce(func.sum(Opportunity.value), 0))
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_won == True,
                    Opportunity.actual_close_date >= month_start
                )
            )
        )

        lost_this_month = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_closed == True,
                    Opportunity.is_won == False,
                    Opportunity.actual_close_date >= month_start
                )
            )
        )

        # Activity metrics
        activities_today = await db.execute(
            select(func.count())
            .select_from(Activity)
            .where(
                and_(
                    Activity.company_id == company_id,
                    func.date(Activity.scheduled_at) == today
                )
            )
        )

        overdue_activities = await db.execute(
            select(func.count())
            .select_from(Activity)
            .where(
                and_(
                    Activity.company_id == company_id,
                    Activity.status.in_(["scheduled", "in_progress"]),
                    Activity.scheduled_at < datetime.utcnow()
                )
            )
        )

        # Process results
        pipeline_row = pipeline_values.one()
        won_row = won_this_month.one()

        # Calculate conversion rate
        total_closed = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_closed == True
                )
            )
        )
        closed_count = total_closed.scalar() or 0

        total_won = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_won == True
                )
            )
        )
        won_count = total_won.scalar() or 0

        conversion_rate = (won_count / closed_count * 100) if closed_count > 0 else 0

        # Calculate average deal size
        avg_deal = await db.execute(
            select(func.avg(Opportunity.value))
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_won == True
                )
            )
        )
        avg_deal_size = avg_deal.scalar() or Decimal("0")

        return {
            "total_leads": total_leads.scalar() or 0,
            "new_leads_this_month": new_leads_this_month.scalar() or 0,
            "leads_by_status": {row[0].value: row[1] for row in leads_by_status.all()},
            "leads_by_source": {row[0].value: row[1] for row in leads_by_source.all()},
            "total_customers": total_customers.scalar() or 0,
            "new_customers_this_month": new_customers_this_month.scalar() or 0,
            "customers_by_state": {row[0]: row[1] for row in customers_by_state.all()},
            "total_opportunities": total_opportunities.scalar() or 0,
            "open_opportunities": open_opportunities.scalar() or 0,
            "opportunities_by_stage": {row[0].value: row[1] for row in opportunities_by_stage.all()},
            "pipeline_value": pipeline_row[0],
            "weighted_pipeline_value": pipeline_row[1],
            "won_this_month": won_row[0],
            "won_value_this_month": won_row[1],
            "lost_this_month": lost_this_month.scalar() or 0,
            "activities_today": activities_today.scalar() or 0,
            "overdue_activities": overdue_activities.scalar() or 0,
            "conversion_rate": round(conversion_rate, 2),
            "average_deal_size": avg_deal_size,
            "average_sales_cycle_days": 30  # Would calculate from actual data
        }

    @classmethod
    async def get_sales_funnel_report(
        cls,
        db: AsyncSession,
        company_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """Get sales funnel report with stage-wise breakdown and conversion rates."""
        if not start_date:
            start_date = date.today() - timedelta(days=90)
        if not end_date:
            end_date = date.today()

        # Get leads created in period
        leads_count = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.deleted_at.is_(None),
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date
                )
            )
        )
        total_leads = leads_count.scalar() or 0

        # Get leads converted to opportunities
        converted_count = await db.execute(
            select(func.count())
            .select_from(Lead)
            .where(
                and_(
                    Lead.company_id == company_id,
                    Lead.status == LeadStatus.CONVERTED,
                    func.date(Lead.created_at) >= start_date,
                    func.date(Lead.created_at) <= end_date
                )
            )
        )
        converted_leads = converted_count.scalar() or 0

        # Get opportunity stage distribution
        stages = [
            OpportunityStage.PROSPECTING,
            OpportunityStage.QUALIFICATION,
            OpportunityStage.NEEDS_ANALYSIS,
            OpportunityStage.PROPOSAL,
            OpportunityStage.NEGOTIATION,
            OpportunityStage.CLOSED_WON
        ]

        funnel_stages = []
        previous_count = total_leads

        for stage in stages:
            count_result = await db.execute(
                select(func.count(), func.coalesce(func.sum(Opportunity.value), 0))
                .where(
                    and_(
                        Opportunity.company_id == company_id,
                        Opportunity.deleted_at.is_(None),
                        func.date(Opportunity.created_at) >= start_date,
                        func.date(Opportunity.created_at) <= end_date,
                        or_(
                            Opportunity.stage == stage,
                            and_(
                                Opportunity.is_closed == True,
                                Opportunity.stage.in_(stages[stages.index(stage):])
                            )
                        )
                    )
                )
            )
            row = count_result.one()
            count = row[0]
            value = row[1]

            percentage = (count / total_leads * 100) if total_leads > 0 else 0
            conversion_to_next = (count / previous_count * 100) if previous_count > 0 else 0

            funnel_stages.append({
                "stage": stage.value,
                "count": count,
                "value": value,
                "percentage": round(percentage, 2),
                "conversion_to_next": round(conversion_to_next, 2)
            })

            previous_count = count if count > 0 else previous_count

        # Get won opportunities
        won_result = await db.execute(
            select(func.count())
            .select_from(Opportunity)
            .where(
                and_(
                    Opportunity.company_id == company_id,
                    Opportunity.is_won == True,
                    func.date(Opportunity.created_at) >= start_date,
                    func.date(Opportunity.created_at) <= end_date
                )
            )
        )
        won_count = won_result.scalar() or 0

        overall_conversion = (won_count / total_leads * 100) if total_leads > 0 else 0

        return {
            "period": f"{start_date.isoformat()} to {end_date.isoformat()}",
            "stages": funnel_stages,
            "overall_conversion_rate": round(overall_conversion, 2),
            "average_time_in_funnel_days": 30  # Would calculate from actual data
        }
