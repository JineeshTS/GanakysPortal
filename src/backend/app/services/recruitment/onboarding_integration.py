"""
Onboarding Integration Service
Connects the recruitment pipeline to the employee onboarding system
"""
from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any, List
from uuid import UUID, uuid4
import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class OnboardingIntegrationService:
    """
    Service for integrating recruitment outcomes with the onboarding system.
    Handles:
    - Creating employee records from hired candidates
    - Initiating onboarding checklists
    - Setting up necessary accounts and access
    - Assigning onboarding buddies
    - Scheduling orientation sessions
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def initiate_onboarding(
        self,
        offer_id: UUID,
        candidate_id: UUID,
        job_id: UUID,
        start_date: date,
        position_title: str,
        department_id: Optional[UUID] = None,
        reporting_to: Optional[UUID] = None,
        company_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Initiate the onboarding process for a hired candidate.

        Args:
            offer_id: The accepted offer UUID
            candidate_id: Candidate UUID
            job_id: Job opening UUID
            start_date: Employee start date
            position_title: Job title
            department_id: Department UUID
            reporting_to: Manager UUID
            company_id: Company UUID

        Returns:
            Dict with onboarding details
        """
        # Get candidate details
        candidate_result = await self.db.execute(
            text("""
                SELECT c.*, cp.user_id as candidate_user_id
                FROM candidates c
                LEFT JOIN candidate_profiles cp ON cp.candidate_id = c.id
                WHERE c.id = :candidate_id
            """).bindparams(candidate_id=candidate_id)
        )
        candidate = candidate_result.first()

        if not candidate:
            raise ValueError(f"Candidate not found: {candidate_id}")

        # Get job details for additional context
        job_result = await self.db.execute(
            text("""
                SELECT j.*, d.name as department_name
                FROM job_openings j
                LEFT JOIN departments d ON j.department_id = d.id
                WHERE j.id = :job_id
            """).bindparams(job_id=job_id)
        )
        job = job_result.first()

        # Create employee record
        employee_id = await self._create_employee_record(
            candidate=candidate,
            job=job,
            position_title=position_title,
            department_id=department_id or (job.department_id if job else None),
            reporting_to=reporting_to,
            start_date=start_date,
            company_id=company_id or (job.company_id if job else None)
        )

        # Create onboarding record
        onboarding_id = await self._create_onboarding_record(
            employee_id=employee_id,
            start_date=start_date,
            company_id=company_id or (job.company_id if job else None)
        )

        # Generate onboarding checklist
        await self._generate_checklist(
            onboarding_id=onboarding_id,
            department_id=department_id or (job.department_id if job else None),
            position_title=position_title
        )

        # Assign onboarding buddy (if configured)
        buddy_id = await self._assign_buddy(
            department_id=department_id or (job.department_id if job else None),
            employee_id=employee_id
        )

        # Schedule orientation
        orientation_date = await self._schedule_orientation(
            employee_id=employee_id,
            start_date=start_date,
            company_id=company_id or (job.company_id if job else None)
        )

        # Update offer with onboarding reference
        await self.db.execute(
            text("""
                UPDATE offers
                SET employee_id = :employee_id,
                    onboarding_id = :onboarding_id,
                    updated_at = NOW()
                WHERE id = :offer_id
            """).bindparams(
                employee_id=employee_id,
                onboarding_id=onboarding_id,
                offer_id=offer_id
            )
        )

        await self.db.commit()

        return {
            "success": True,
            "employee_id": str(employee_id),
            "onboarding_id": str(onboarding_id),
            "buddy_id": str(buddy_id) if buddy_id else None,
            "orientation_date": orientation_date.isoformat() if orientation_date else None,
            "start_date": start_date.isoformat(),
            "position_title": position_title
        }

    async def _create_employee_record(
        self,
        candidate: Any,
        job: Any,
        position_title: str,
        department_id: Optional[UUID],
        reporting_to: Optional[UUID],
        start_date: date,
        company_id: Optional[UUID]
    ) -> UUID:
        """Create a new employee record from candidate data."""
        employee_id = uuid4()

        # Generate employee code
        emp_code = await self._generate_employee_code(company_id)

        await self.db.execute(
            text("""
                INSERT INTO employees (
                    id, company_id, employee_code, first_name, last_name, email,
                    phone, department_id, designation, reporting_to,
                    date_of_joining, employment_status, employment_type,
                    candidate_id, created_at, updated_at
                ) VALUES (
                    :id, :company_id, :emp_code, :first_name, :last_name, :email,
                    :phone, :dept_id, :designation, :reporting_to,
                    :doj, 'active', 'full_time',
                    :candidate_id, NOW(), NOW()
                )
            """).bindparams(
                id=employee_id,
                company_id=company_id,
                emp_code=emp_code,
                first_name=candidate.first_name,
                last_name=candidate.last_name,
                email=candidate.email,
                phone=candidate.phone,
                dept_id=department_id,
                designation=position_title,
                reporting_to=reporting_to,
                doj=start_date,
                candidate_id=candidate.id
            )
        )

        return employee_id

    async def _generate_employee_code(self, company_id: Optional[UUID]) -> str:
        """Generate unique employee code."""
        result = await self.db.execute(
            text("""
                SELECT MAX(CAST(SUBSTRING(employee_code FROM 4) AS INTEGER)) as max_num
                FROM employees
                WHERE company_id = :company_id OR :company_id IS NULL
                  AND employee_code ~ '^EMP[0-9]+$'
            """).bindparams(company_id=company_id)
        )
        max_num = result.scalar() or 0
        return f"EMP{max_num + 1:05d}"

    async def _create_onboarding_record(
        self,
        employee_id: UUID,
        start_date: date,
        company_id: Optional[UUID]
    ) -> UUID:
        """Create onboarding tracking record."""
        onboarding_id = uuid4()

        await self.db.execute(
            text("""
                INSERT INTO employee_onboarding (
                    id, company_id, employee_id, status,
                    start_date, expected_completion_date,
                    progress_percentage, created_at, updated_at
                ) VALUES (
                    :id, :company_id, :employee_id, 'pending',
                    :start_date, :expected_completion,
                    0, NOW(), NOW()
                )
            """).bindparams(
                id=onboarding_id,
                company_id=company_id,
                employee_id=employee_id,
                start_date=start_date,
                expected_completion=start_date + timedelta(days=30)
            )
        )

        return onboarding_id

    async def _generate_checklist(
        self,
        onboarding_id: UUID,
        department_id: Optional[UUID],
        position_title: str
    ) -> List[UUID]:
        """Generate onboarding checklist items."""
        # Standard checklist items
        standard_items = [
            {"title": "Complete personal information form", "category": "documentation", "days_from_start": 0, "required": True},
            {"title": "Submit identity documents", "category": "documentation", "days_from_start": 0, "required": True},
            {"title": "Submit bank account details", "category": "documentation", "days_from_start": 0, "required": True},
            {"title": "Complete tax declaration", "category": "documentation", "days_from_start": 3, "required": True},
            {"title": "Sign employment contract", "category": "documentation", "days_from_start": 0, "required": True},
            {"title": "Receive laptop/equipment", "category": "it_setup", "days_from_start": 0, "required": True},
            {"title": "Set up email account", "category": "it_setup", "days_from_start": 0, "required": True},
            {"title": "Set up VPN access", "category": "it_setup", "days_from_start": 1, "required": False},
            {"title": "Complete security awareness training", "category": "training", "days_from_start": 7, "required": True},
            {"title": "Complete compliance training", "category": "training", "days_from_start": 14, "required": True},
            {"title": "Meet with HR for orientation", "category": "orientation", "days_from_start": 0, "required": True},
            {"title": "Meet with manager for role briefing", "category": "orientation", "days_from_start": 0, "required": True},
            {"title": "Meet with onboarding buddy", "category": "orientation", "days_from_start": 0, "required": False},
            {"title": "Tour office facilities", "category": "orientation", "days_from_start": 0, "required": False},
            {"title": "Review department goals and OKRs", "category": "integration", "days_from_start": 7, "required": True},
            {"title": "Complete 30-day check-in with manager", "category": "integration", "days_from_start": 30, "required": True},
        ]

        created_items = []
        for item in standard_items:
            item_id = uuid4()
            await self.db.execute(
                text("""
                    INSERT INTO onboarding_checklist_items (
                        id, onboarding_id, title, category,
                        days_from_start, is_required, status, created_at
                    ) VALUES (
                        :id, :onboarding_id, :title, :category,
                        :days, :required, 'pending', NOW()
                    )
                """).bindparams(
                    id=item_id,
                    onboarding_id=onboarding_id,
                    title=item["title"],
                    category=item["category"],
                    days=item["days_from_start"],
                    required=item["required"]
                )
            )
            created_items.append(item_id)

        return created_items

    async def _assign_buddy(
        self,
        department_id: Optional[UUID],
        employee_id: UUID
    ) -> Optional[UUID]:
        """Assign an onboarding buddy from the same department."""
        if not department_id:
            return None

        # Find an eligible buddy (same department, >6 months tenure)
        result = await self.db.execute(
            text("""
                SELECT id FROM employees
                WHERE department_id = :dept_id
                  AND date_of_joining <= :tenure_date
                  AND employment_status = 'active'
                  AND id != :employee_id
                ORDER BY RANDOM()
                LIMIT 1
            """).bindparams(
                dept_id=department_id,
                tenure_date=date.today() - timedelta(days=180),
                employee_id=employee_id
            )
        )
        buddy = result.first()

        if buddy:
            # Record buddy assignment
            await self.db.execute(
                text("""
                    UPDATE employee_onboarding
                    SET buddy_id = :buddy_id, updated_at = NOW()
                    WHERE employee_id = :employee_id
                """).bindparams(buddy_id=buddy.id, employee_id=employee_id)
            )
            return buddy.id

        return None

    async def _schedule_orientation(
        self,
        employee_id: UUID,
        start_date: date,
        company_id: Optional[UUID]
    ) -> Optional[datetime]:
        """Schedule orientation session."""
        # Default: orientation at 9 AM on start date
        orientation_datetime = datetime.combine(start_date, datetime.min.time().replace(hour=9))

        await self.db.execute(
            text("""
                INSERT INTO orientation_sessions (
                    id, company_id, employee_id, scheduled_at,
                    session_type, status, created_at
                ) VALUES (
                    gen_random_uuid(), :company_id, :employee_id, :scheduled_at,
                    'new_hire_orientation', 'scheduled', NOW()
                )
            """).bindparams(
                company_id=company_id,
                employee_id=employee_id,
                scheduled_at=orientation_datetime
            )
        )

        return orientation_datetime

    async def get_onboarding_status(
        self,
        employee_id: UUID
    ) -> Dict[str, Any]:
        """Get current onboarding status and progress."""
        # Get onboarding record
        result = await self.db.execute(
            text("""
                SELECT o.*, e.first_name, e.last_name, e.email,
                       b.first_name as buddy_first, b.last_name as buddy_last
                FROM employee_onboarding o
                JOIN employees e ON o.employee_id = e.id
                LEFT JOIN employees b ON o.buddy_id = b.id
                WHERE o.employee_id = :employee_id
            """).bindparams(employee_id=employee_id)
        )
        onboarding = result.first()

        if not onboarding:
            return {"error": "Onboarding record not found"}

        # Get checklist progress
        checklist_result = await self.db.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'pending' AND is_required = TRUE) as pending_required
                FROM onboarding_checklist_items
                WHERE onboarding_id = :onboarding_id
            """).bindparams(onboarding_id=onboarding.id)
        )
        checklist = checklist_result.first()

        progress = (checklist.completed / checklist.total * 100) if checklist.total > 0 else 0

        return {
            "onboarding_id": str(onboarding.id),
            "employee_id": str(employee_id),
            "employee_name": f"{onboarding.first_name} {onboarding.last_name}",
            "status": onboarding.status,
            "start_date": onboarding.start_date.isoformat(),
            "expected_completion": onboarding.expected_completion_date.isoformat() if onboarding.expected_completion_date else None,
            "progress_percentage": round(progress, 1),
            "checklist": {
                "total": checklist.total,
                "completed": checklist.completed,
                "pending_required": checklist.pending_required
            },
            "buddy": {
                "name": f"{onboarding.buddy_first} {onboarding.buddy_last}" if onboarding.buddy_first else None
            } if onboarding.buddy_id else None
        }

    async def update_checklist_item(
        self,
        item_id: UUID,
        status: str,
        completed_by: Optional[UUID] = None,
        notes: Optional[str] = None
    ) -> bool:
        """Update a checklist item status."""
        await self.db.execute(
            text("""
                UPDATE onboarding_checklist_items
                SET status = :status,
                    completed_at = CASE WHEN :status = 'completed' THEN NOW() ELSE NULL END,
                    completed_by = :completed_by,
                    notes = :notes,
                    updated_at = NOW()
                WHERE id = :item_id
            """).bindparams(
                item_id=item_id,
                status=status,
                completed_by=completed_by,
                notes=notes
            )
        )

        # Update overall progress
        result = await self.db.execute(
            text("""
                SELECT onboarding_id FROM onboarding_checklist_items WHERE id = :item_id
            """).bindparams(item_id=item_id)
        )
        row = result.first()

        if row:
            await self._update_onboarding_progress(row.onboarding_id)

        await self.db.commit()
        return True

    async def _update_onboarding_progress(self, onboarding_id: UUID):
        """Recalculate and update onboarding progress."""
        result = await self.db.execute(
            text("""
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'completed') as completed
                FROM onboarding_checklist_items
                WHERE onboarding_id = :onboarding_id
            """).bindparams(onboarding_id=onboarding_id)
        )
        counts = result.first()

        progress = (counts.completed / counts.total * 100) if counts.total > 0 else 0
        new_status = "completed" if progress >= 100 else "in_progress" if progress > 0 else "pending"

        await self.db.execute(
            text("""
                UPDATE employee_onboarding
                SET progress_percentage = :progress,
                    status = :status,
                    completed_at = CASE WHEN :progress >= 100 THEN NOW() ELSE NULL END,
                    updated_at = NOW()
                WHERE id = :onboarding_id
            """).bindparams(
                onboarding_id=onboarding_id,
                progress=progress,
                status=new_status
            )
        )
