"""
AI Org Builder Service
Generates organizational structures based on company profile and products
"""
import os
import json
import hashlib
import logging
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, timedelta

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

logger = logging.getLogger(__name__)

from app.core.datetime_utils import utc_now
from app.models.company import (
    CompanyProfile, CompanyExtendedProfile, CompanyProduct,
    Department, Designation, AIRecommendation, AIRecommendationItem
)


class OrgBuilderService:
    """
    AI-powered organization structure builder.

    Generates recommendations for:
    - Departments and their hierarchy
    - Designations/roles with full JDs
    - Headcount planning
    - Salary ranges (Indian market)
    """

    API_URL = "https://api.anthropic.com/v1/messages"
    MODEL = "claude-sonnet-4-20250514"

    # Industry-specific org patterns
    INDUSTRY_PATTERNS = {
        "saas": {
            "core_departments": ["Engineering", "Product", "Sales", "Customer Success", "Marketing"],
            "tech_ratio": 0.5,  # 50% tech roles
            "early_hires": ["CTO", "Lead Engineer", "Product Manager", "Sales Lead"]
        },
        "fintech": {
            "core_departments": ["Engineering", "Product", "Compliance", "Risk", "Operations"],
            "tech_ratio": 0.4,
            "early_hires": ["CTO", "Compliance Officer", "Risk Analyst", "Lead Engineer"]
        },
        "ecommerce": {
            "core_departments": ["Engineering", "Operations", "Marketing", "Supply Chain", "Customer Service"],
            "tech_ratio": 0.3,
            "early_hires": ["CTO", "Operations Manager", "Marketing Lead", "Supply Chain Manager"]
        },
        "edtech": {
            "core_departments": ["Engineering", "Content", "Product", "Sales", "Learning & Development"],
            "tech_ratio": 0.35,
            "early_hires": ["CTO", "Content Head", "Product Manager", "Instructional Designer"]
        },
        "healthtech": {
            "core_departments": ["Engineering", "Product", "Clinical", "Regulatory", "Operations"],
            "tech_ratio": 0.35,
            "early_hires": ["CTO", "Clinical Lead", "Product Manager", "Regulatory Affairs"]
        },
    }

    # Stage-based headcount multipliers
    STAGE_HEADCOUNT = {
        "idea": {"min": 1, "max": 3, "recommended": 2},
        "mvp": {"min": 3, "max": 10, "recommended": 5},
        "seed": {"min": 5, "max": 25, "recommended": 12},
        "series_a": {"min": 15, "max": 60, "recommended": 35},
        "series_b": {"min": 40, "max": 150, "recommended": 80},
        "series_c": {"min": 100, "max": 300, "recommended": 180},
        "growth": {"min": 150, "max": 500, "recommended": 300},
        "enterprise": {"min": 300, "max": 2000, "recommended": 500},
    }

    # Indian market salary ranges by level (annual in INR)
    SALARY_RANGES = {
        1: {"min": 3000000, "max": 10000000, "label": "C-Suite"},       # 30-100L
        2: {"min": 2000000, "max": 5000000, "label": "VP/Director"},    # 20-50L
        3: {"min": 1500000, "max": 3500000, "label": "Senior Manager"}, # 15-35L
        4: {"min": 1000000, "max": 2500000, "label": "Manager"},        # 10-25L
        5: {"min": 800000, "max": 1800000, "label": "Senior"},          # 8-18L
        6: {"min": 500000, "max": 1200000, "label": "Mid-Level"},       # 5-12L
        7: {"min": 300000, "max": 700000, "label": "Junior/Entry"},     # 3-7L
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            logger.info("OrgBuilderService initialized with API key configured")
        else:
            logger.warning("OrgBuilderService: ANTHROPIC_API_KEY not found in environment")

    async def generate_initial_structure(
        self,
        company_id: UUID,
        target_headcount: Optional[int] = None,
        focus_product_ids: Optional[List[UUID]] = None,
        additional_context: Optional[str] = None
    ) -> AIRecommendation:
        """
        Generate complete organizational structure for a company.

        Args:
            company_id: Company UUID
            target_headcount: Override target headcount
            focus_product_ids: Specific products to focus on
            additional_context: Additional context from user

        Returns:
            AIRecommendation with full structure
        """
        # Get company data
        company_data = await self._get_company_context(company_id)
        products = await self._get_products(company_id, focus_product_ids)

        if target_headcount:
            company_data["target_headcount"] = target_headcount

        # Build prompt
        prompt = self._build_org_structure_prompt(company_data, products, additional_context)
        prompt_hash = hashlib.sha256(prompt.encode()).hexdigest()[:16]

        # Call AI
        ai_response = await self._call_claude(prompt)

        if not ai_response:
            # Fallback to rule-based generation
            recommendation_data = self._generate_fallback_structure(company_data, products)
            confidence = Decimal("0.60")
        else:
            recommendation_data = ai_response
            confidence = Decimal("0.85")

        # Create recommendation
        recommendation = AIRecommendation(
            company_id=company_id,
            recommendation_type="initial_structure",
            status="pending",
            trigger_event="setup_wizard",
            priority=9,
            confidence_score=confidence,
            recommendation_data=recommendation_data,
            rationale=recommendation_data.get("summary", "AI-generated organizational structure"),
            ai_model_used=self.MODEL,
            ai_prompt_hash=prompt_hash,
            expires_at=utc_now() + timedelta(days=30)
        )

        self.db.add(recommendation)
        await self.db.flush()

        # Create recommendation items
        sequence = 0

        # Add departments
        for dept in recommendation_data.get("departments", []):
            item = AIRecommendationItem(
                recommendation_id=recommendation.id,
                item_type="department",
                action="create",
                item_data=dept,
                status="pending",
                priority=8,
                sequence_order=sequence
            )
            self.db.add(item)
            sequence += 1

        # Add designations
        for desig in recommendation_data.get("designations", []):
            item = AIRecommendationItem(
                recommendation_id=recommendation.id,
                item_type="designation",
                action="create",
                item_data=desig,
                status="pending",
                priority=desig.get("priority_score", 5),
                sequence_order=sequence
            )
            self.db.add(item)
            sequence += 1

        await self.db.commit()
        await self.db.refresh(recommendation)

        return recommendation

    async def generate_designation_jd(
        self,
        title: str,
        department: Optional[str] = None,
        level: Optional[int] = None,
        company_id: Optional[UUID] = None,
        additional_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a full Job Description for a designation.

        Args:
            title: Job title
            department: Department name
            level: Hierarchy level (1-7)
            company_id: Company for context
            additional_context: Additional info

        Returns:
            Dict with full JD fields
        """
        # Get company context if available
        company_context = ""
        if company_id:
            company_data = await self._get_company_context(company_id)
            company_context = f"""
Company: {company_data.get('name', 'Startup')}
Industry: {company_data.get('industry', 'Technology')}
Stage: {company_data.get('stage', 'growth')}
"""

        level_label = self.SALARY_RANGES.get(level or 6, {}).get("label", "Mid-Level")
        salary_info = self.SALARY_RANGES.get(level or 6, self.SALARY_RANGES[6])

        prompt = f"""Generate a professional Job Description for the following role in the Indian market:

Job Title: {title}
Department: {department or 'Not specified'}
Level: {level_label} (Level {level or 6})
{company_context}
{additional_context or ''}

Return a JSON object with:
1. description: Compelling role description (2-3 paragraphs)
2. requirements: Qualifications (bullet points as string with \\n)
3. responsibilities: Key duties (bullet points as string with \\n)
4. skills_required: Required skills (comma-separated)
5. experience_min: Minimum years experience (integer)
6. experience_max: Maximum years experience (integer)
7. salary_min: Minimum annual salary in INR (realistic Indian market)
8. salary_max: Maximum annual salary in INR (realistic Indian market)

Use realistic Indian startup market rates. Return ONLY valid JSON."""

        result = await self._call_claude(prompt)

        if not result:
            # Fallback
            return {
                "description": f"We are looking for a talented {title} to join our team.",
                "requirements": f"• Bachelor's degree in relevant field\\n• Strong communication skills\\n• Problem-solving abilities",
                "responsibilities": f"• Contribute to team goals\\n• Collaborate with cross-functional teams\\n• Drive results in your area",
                "skills_required": "Communication, Problem Solving, Team Collaboration",
                "experience_min": max(0, (level or 6) - 5) * 2,
                "experience_max": max(2, (level or 6) - 4) * 3,
                "salary_min": salary_info["min"],
                "salary_max": salary_info["max"]
            }

        return result

    async def analyze_product_change(
        self,
        company_id: UUID,
        product_id: UUID,
        change_type: str  # added, modified, removed
    ) -> Optional[AIRecommendation]:
        """
        Analyze a product change and suggest org adjustments.

        Args:
            company_id: Company UUID
            product_id: Changed product UUID
            change_type: Type of change (added/modified/removed)

        Returns:
            AIRecommendation if adjustments needed, None otherwise
        """
        company_data = await self._get_company_context(company_id)

        # Get the product
        product_result = await self.db.execute(
            select(CompanyProduct).where(CompanyProduct.id == product_id)
        )
        product = product_result.scalar_one_or_none()

        if not product:
            return None

        # Get current org structure
        current_depts = await self._get_current_departments(company_id)
        current_designations = await self._get_current_designations(company_id)

        prompt = f"""A company has made a product change. Analyze if organizational adjustments are needed.

Company: {company_data.get('name')}
Industry: {company_data.get('industry')}
Stage: {company_data.get('stage')}
Current Employees: {company_data.get('employee_count', 0)}

Product Change: {change_type.upper()}
Product: {product.name}
Description: {product.description or 'N/A'}
Tech Stack: {', '.join(product.tech_stack or [])}
Team Size Needed: {product.team_size_needed or 'Not specified'}

Current Departments: {', '.join([d['name'] for d in current_depts])}
Current Roles: {len(current_designations)} total

Based on this product change, suggest any organizational adjustments needed.
Return JSON with:
1. needs_adjustment: boolean
2. priority: "immediate" | "next_quarter" | "nice_to_have"
3. departments: array of department changes (if any)
4. designations: array of role additions/modifications (if any)
5. rationale: explanation

If no changes needed, return {{"needs_adjustment": false, "rationale": "explanation"}}
Return ONLY valid JSON."""

        result = await self._call_claude(prompt)

        if not result or not result.get("needs_adjustment"):
            return None

        # Create recommendation
        recommendation = AIRecommendation(
            company_id=company_id,
            recommendation_type="role_addition",
            status="pending",
            trigger_event=f"product_{change_type}",
            trigger_entity_id=product_id,
            trigger_entity_type="product",
            priority={"immediate": 9, "next_quarter": 6, "nice_to_have": 3}.get(result.get("priority", "nice_to_have"), 5),
            confidence_score=Decimal("0.75"),
            recommendation_data=result,
            rationale=result.get("rationale", "Product change analysis"),
            ai_model_used=self.MODEL,
            expires_at=utc_now() + timedelta(days=14)
        )

        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)

        return recommendation

    async def _get_company_context(self, company_id: UUID) -> Dict[str, Any]:
        """Get company context for AI prompts."""
        # Get company
        company_result = await self.db.execute(
            select(CompanyProfile).where(CompanyProfile.id == company_id)
        )
        company = company_result.scalar_one_or_none()

        # Get extended profile
        ext_result = await self.db.execute(
            select(CompanyExtendedProfile).where(CompanyExtendedProfile.company_id == company_id)
        )
        ext_profile = ext_result.scalar_one_or_none()

        # Count current employees
        emp_count_result = await self.db.execute(
            select(func.count()).select_from(
                select(Department.id).where(Department.company_id == company_id).subquery()
            )
        )

        return {
            "name": company.name if company else "Company",
            "industry": ext_profile.industry if ext_profile else "technology",
            "stage": ext_profile.company_stage if ext_profile else "seed",
            "employee_count": ext_profile.employee_count_current if ext_profile else 0,
            "target_headcount": ext_profile.employee_count_target if ext_profile else None,
            "tech_focused": ext_profile.tech_focused if ext_profile else True,
            "remote_policy": ext_profile.remote_work_policy if ext_profile else "hybrid",
            "org_preference": ext_profile.org_structure_preference if ext_profile else "flat",
            "funding_stage": ext_profile.last_funding_round if ext_profile else None,
        }

    async def _get_products(self, company_id: UUID, focus_ids: Optional[List[UUID]] = None) -> List[Dict[str, Any]]:
        """Get company products."""
        query = select(CompanyProduct).where(
            and_(
                CompanyProduct.company_id == company_id,
                CompanyProduct.status == "active"
            )
        )

        if focus_ids:
            query = query.where(CompanyProduct.id.in_(focus_ids))

        result = await self.db.execute(query)
        products = result.scalars().all()

        return [{
            "name": p.name,
            "description": p.description,
            "type": p.product_type,
            "tech_stack": p.tech_stack or [],
            "team_size_needed": p.team_size_needed,
            "is_primary": p.is_primary,
        } for p in products]

    async def _get_current_departments(self, company_id: UUID) -> List[Dict[str, Any]]:
        """Get current departments."""
        result = await self.db.execute(
            select(Department).where(
                and_(Department.company_id == company_id, Department.is_active == True)
            )
        )
        depts = result.scalars().all()
        return [{"name": d.name, "code": d.code} for d in depts]

    async def _get_current_designations(self, company_id: UUID) -> List[Dict[str, Any]]:
        """Get current designations."""
        result = await self.db.execute(
            select(Designation).where(
                and_(Designation.company_id == company_id, Designation.is_active == True)
            )
        )
        desigs = result.scalars().all()
        return [{"name": d.name, "level": d.level} for d in desigs]

    def _build_org_structure_prompt(
        self,
        company: Dict[str, Any],
        products: List[Dict[str, Any]],
        additional_context: Optional[str]
    ) -> str:
        """Build the AI prompt for org structure generation."""
        # Get industry pattern
        industry = company.get("industry", "technology").lower()
        pattern = self.INDUSTRY_PATTERNS.get(industry, self.INDUSTRY_PATTERNS.get("saas"))

        # Get stage info
        stage = company.get("stage", "seed")
        stage_info = self.STAGE_HEADCOUNT.get(stage, self.STAGE_HEADCOUNT["seed"])

        target = company.get("target_headcount") or stage_info["recommended"]

        products_desc = "\n".join([
            f"- {p['name']}: {p.get('description', 'N/A')} (Tech: {', '.join(p.get('tech_stack', []))})"
            for p in products
        ]) or "No products defined yet"

        prompt = f"""Generate an optimal organizational structure for the following Indian startup:

COMPANY PROFILE:
- Name: {company.get('name')}
- Industry: {company.get('industry')}
- Stage: {company.get('stage')}
- Current Employees: {company.get('employee_count', 0)}
- Target Headcount: {target}
- Tech Focused: {company.get('tech_focused', True)}
- Work Model: {company.get('remote_policy', 'hybrid')}
- Org Preference: {company.get('org_preference', 'flat')}
- Funding: {company.get('funding_stage', 'bootstrapped')}

PRODUCTS/SERVICES:
{products_desc}

{additional_context or ''}

Generate a comprehensive organization structure with:
1. Departments (with hierarchy if needed)
2. Designations/roles for each department
3. Full JDs with Indian market salary ranges

Return JSON with this exact structure:
{{
    "summary": "Brief summary of the recommended structure",
    "total_headcount": number,
    "estimated_monthly_cost": number (in INR),
    "departments": [
        {{
            "name": "Department Name",
            "code": "DEPT",
            "description": "Department purpose",
            "headcount_target": number,
            "parent_department": null or "Parent Dept Name",
            "rationale": "Why this department"
        }}
    ],
    "designations": [
        {{
            "name": "Role Title",
            "code": "ROLE01",
            "department": "Department Name",
            "level": 1-7 (1=C-suite, 7=Junior),
            "description": "Role description (2-3 paragraphs)",
            "requirements": "Bullet points with newlines",
            "responsibilities": "Bullet points with newlines",
            "skills_required": "comma,separated,skills",
            "experience_min": number,
            "experience_max": number,
            "salary_min": number (annual INR),
            "salary_max": number (annual INR),
            "headcount_target": number,
            "priority": "immediate" | "next_quarter" | "nice_to_have",
            "priority_score": 1-10,
            "rationale": "Why this role is needed"
        }}
    ]
}}

Use realistic Indian market salary ranges:
- C-Suite: 30-100 LPA
- VP/Director: 20-50 LPA
- Sr Manager: 15-35 LPA
- Manager: 10-25 LPA
- Senior: 8-18 LPA
- Mid-Level: 5-12 LPA
- Junior: 3-7 LPA

Return ONLY valid JSON, no additional text."""

        return prompt

    def _generate_fallback_structure(
        self,
        company: Dict[str, Any],
        products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate fallback structure when AI is unavailable."""
        industry = company.get("industry", "technology").lower()
        pattern = self.INDUSTRY_PATTERNS.get(industry, self.INDUSTRY_PATTERNS.get("saas"))
        stage = company.get("stage", "seed")
        stage_info = self.STAGE_HEADCOUNT.get(stage, self.STAGE_HEADCOUNT["seed"])

        target = company.get("target_headcount") or stage_info["recommended"]

        departments = []
        designations = []

        # Create core departments
        for dept_name in pattern.get("core_departments", ["Engineering", "Operations"])[:4]:
            dept_code = dept_name[:4].upper()
            departments.append({
                "name": dept_name,
                "code": dept_code,
                "description": f"{dept_name} department for the organization",
                "headcount_target": max(1, target // len(pattern.get("core_departments") or ["Engineering"])),
                "parent_department": None,
                "rationale": f"Core {dept_name.lower()} function"
            })

            # Add basic roles for each department
            roles = self._get_default_roles_for_department(dept_name, stage)
            for role in roles:
                role["department"] = dept_name
                designations.append(role)

        monthly_cost = sum(
            (d.get("salary_min", 500000) + d.get("salary_max", 1000000)) / 2 / 12 * d.get("headcount_target", 1)
            for d in designations
        )

        return {
            "summary": f"Basic organizational structure for a {stage} stage {industry} company with {target} target headcount.",
            "total_headcount": target,
            "estimated_monthly_cost": int(monthly_cost),
            "departments": departments,
            "designations": designations
        }

    def _get_default_roles_for_department(self, dept_name: str, stage: str) -> List[Dict[str, Any]]:
        """Get default roles for a department based on stage."""
        roles = []

        # Department head (for series_a+)
        if stage in ["series_a", "series_b", "series_c", "growth", "enterprise"]:
            head_level = 2 if stage in ["growth", "enterprise"] else 3
            salary = self.SALARY_RANGES[head_level]
            roles.append({
                "name": f"Head of {dept_name}",
                "code": f"HEAD{dept_name[:3].upper()}",
                "level": head_level,
                "description": f"Lead the {dept_name} function and build the team.",
                "requirements": "• 8+ years experience\\n• Strong leadership skills\\n• Strategic thinking",
                "responsibilities": "• Define strategy\\n• Build and lead team\\n• Drive results",
                "skills_required": "Leadership, Strategy, Communication",
                "experience_min": 8,
                "experience_max": 15,
                "salary_min": salary["min"],
                "salary_max": salary["max"],
                "headcount_target": 1,
                "priority": "immediate",
                "priority_score": 9,
                "rationale": f"Leadership needed for {dept_name}"
            })

        # Senior individual contributor
        senior_level = 5
        salary = self.SALARY_RANGES[senior_level]
        roles.append({
            "name": f"Senior {dept_name.rstrip('s')} Specialist" if dept_name != "Engineering" else "Senior Software Engineer",
            "code": f"SR{dept_name[:3].upper()}",
            "level": senior_level,
            "description": f"Senior contributor in {dept_name}.",
            "requirements": "• 4+ years experience\\n• Deep domain expertise\\n• Strong execution",
            "responsibilities": "• Lead key projects\\n• Mentor juniors\\n• Drive initiatives",
            "skills_required": "Domain Expertise, Execution, Mentoring",
            "experience_min": 4,
            "experience_max": 8,
            "salary_min": salary["min"],
            "salary_max": salary["max"],
            "headcount_target": 2,
            "priority": "immediate",
            "priority_score": 8,
            "rationale": "Core execution capability"
        })

        return roles

    async def _call_claude(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Call Claude API and parse response."""
        if not self.api_key:
            logger.warning("Claude API call skipped: No API key configured")
            return None

        logger.info(f"Calling Claude API with model {self.MODEL}, prompt length: {len(prompt)} chars")

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.API_URL,
                    headers={
                        "Content-Type": "application/json",
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01"
                    },
                    json={
                        "model": self.MODEL,
                        "max_tokens": 8192,
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                )

                logger.info(f"Claude API response status: {response.status_code}")

                if response.status_code != 200:
                    logger.error(f"Claude API error: {response.status_code} - {response.text[:500]}")
                    return None

                data = response.json()
                content = data.get("content", [{}])[0].get("text", "")

                logger.info(f"Claude API response received, content length: {len(content)} chars")

                # Parse JSON from response
                # Handle potential markdown code blocks
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                result = json.loads(content.strip())
                logger.info(f"Claude API response parsed successfully: {len(result.get('departments', []))} departments, {len(result.get('designations', []))} designations")
                return result

        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error from Claude response: {e}")
            return None
        except httpx.TimeoutException as e:
            logger.error(f"Claude API timeout after 120s: {e}")
            return None
        except Exception as e:
            logger.error(f"Claude API call failed: {type(e).__name__}: {e}")
            return None
