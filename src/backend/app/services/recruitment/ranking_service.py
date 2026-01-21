"""
Candidate Ranking Service
Generates ranked lists of candidates based on AI interviews, resume match, and other factors
"""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum
import re

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class RankingTier(str, Enum):
    """Ranking tier classifications."""
    TOP_CANDIDATE = "top_candidate"
    STRONG_CANDIDATE = "strong_candidate"
    QUALIFIED = "qualified"
    BORDERLINE = "borderline"
    NOT_RECOMMENDED = "not_recommended"


@dataclass
class CandidateRankData:
    """Complete ranking data for a candidate."""
    application_id: UUID
    candidate_id: UUID
    candidate_name: str
    candidate_email: str

    # Composite scores
    composite_score: float
    rank_position: int
    percentile: float
    tier: RankingTier

    # Component scores
    ai_interview_score: Optional[float] = None
    resume_match_score: Optional[float] = None
    experience_fit_score: Optional[float] = None
    skills_match_score: Optional[float] = None
    salary_fit_score: Optional[float] = None

    # AI Assessment
    ai_recommendation: Optional[str] = None
    ai_summary: Optional[str] = None
    strengths: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)

    # Application data
    application_status: str = "applied"
    application_stage: str = "screening"
    applied_date: Optional[datetime] = None

    # Score breakdown
    component_breakdown: Dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "application_id": str(self.application_id),
            "candidate_id": str(self.candidate_id),
            "candidate_name": self.candidate_name,
            "candidate_email": self.candidate_email,
            "composite_score": round(self.composite_score, 2),
            "rank_position": self.rank_position,
            "percentile": round(self.percentile, 1),
            "tier": self.tier.value,
            "ai_interview_score": round(self.ai_interview_score, 2) if self.ai_interview_score else None,
            "resume_match_score": round(self.resume_match_score, 2) if self.resume_match_score else None,
            "experience_fit_score": round(self.experience_fit_score, 2) if self.experience_fit_score else None,
            "skills_match_score": round(self.skills_match_score, 2) if self.skills_match_score else None,
            "salary_fit_score": round(self.salary_fit_score, 2) if self.salary_fit_score else None,
            "ai_recommendation": self.ai_recommendation,
            "ai_summary": self.ai_summary,
            "strengths": self.strengths,
            "concerns": self.concerns,
            "application_status": self.application_status,
            "application_stage": self.application_stage,
            "applied_date": self.applied_date.isoformat() if self.applied_date else None,
            "component_breakdown": self.component_breakdown
        }


@dataclass
class RanklistResult:
    """Complete ranklist result."""
    job_id: UUID
    job_title: str
    total_candidates: int
    generated_at: datetime
    rankings: List[CandidateRankData]

    # Statistics
    average_score: float
    score_distribution: Dict[str, int]
    recommendation_distribution: Dict[str, int]

    # Filters applied
    filters_applied: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": str(self.job_id),
            "job_title": self.job_title,
            "total_candidates": self.total_candidates,
            "generated_at": self.generated_at.isoformat(),
            "rankings": [r.to_dict() for r in self.rankings],
            "statistics": {
                "average_score": round(self.average_score, 2),
                "score_distribution": self.score_distribution,
                "recommendation_distribution": self.recommendation_distribution
            },
            "filters_applied": self.filters_applied
        }


class CandidateRankingService:
    """
    Generates ranked lists of candidates based on:
    1. AI Interview scores (weighted by session type)
    2. Resume match score
    3. Experience alignment
    4. Skills match
    5. Salary expectations fit
    """

    # Default weights for ranking components
    DEFAULT_WEIGHTS = {
        'ai_interview': 0.45,      # AI interview is most important
        'resume_match': 0.20,      # Resume/qualification match
        'experience_fit': 0.15,    # Experience level alignment
        'skills_match': 0.15,      # Skills overlap
        'salary_fit': 0.05,        # Salary expectations alignment
    }

    # Tier thresholds
    TIER_THRESHOLDS = {
        RankingTier.TOP_CANDIDATE: 85,
        RankingTier.STRONG_CANDIDATE: 70,
        RankingTier.QUALIFIED: 55,
        RankingTier.BORDERLINE: 40,
        RankingTier.NOT_RECOMMENDED: 0
    }

    def __init__(self, db: AsyncSession):
        self.db = db

    async def generate_ranklist(
        self,
        job_id: UUID,
        min_score: float = 0,
        limit: int = 50,
        include_stages: Optional[List[str]] = None,
        exclude_statuses: Optional[List[str]] = None
    ) -> RanklistResult:
        """
        Generate a ranked list of candidates for a job opening.

        Args:
            job_id: Job opening UUID
            min_score: Minimum composite score to include (0-100)
            limit: Maximum number of candidates to return
            include_stages: Only include these pipeline stages
            exclude_statuses: Exclude these application statuses

        Returns:
            RanklistResult with ranked candidates
        """
        # Get job details
        job_result = await self.db.execute(
            text("""
                SELECT id, title, description, requirements, skills_required,
                       experience_min, experience_max, salary_min, salary_max
                FROM job_openings
                WHERE id = :job_id
            """).bindparams(job_id=job_id)
        )
        job = job_result.first()

        if not job:
            raise ValueError(f"Job not found: {job_id}")

        # Get all applications for this job
        applications = await self._get_applications(
            job_id,
            include_stages,
            exclude_statuses
        )

        # Calculate scores for each application
        ranked_candidates = []
        for app in applications:
            rank_data = await self._calculate_candidate_score(app, job)
            if rank_data.composite_score >= min_score:
                ranked_candidates.append(rank_data)

        # Sort by composite score (descending)
        ranked_candidates.sort(key=lambda x: x.composite_score, reverse=True)

        # Assign rank positions and percentiles
        total = len(ranked_candidates)
        for i, candidate in enumerate(ranked_candidates):
            candidate.rank_position = i + 1
            candidate.percentile = ((total - i) / total) * 100 if total > 0 else 0
            candidate.tier = self._determine_tier(candidate.composite_score)

        # Limit results
        ranked_candidates = ranked_candidates[:limit]

        # Calculate statistics
        all_scores = [c.composite_score for c in ranked_candidates]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

        return RanklistResult(
            job_id=job_id,
            job_title=job.title,
            total_candidates=total,
            generated_at=datetime.utcnow(),
            rankings=ranked_candidates,
            average_score=avg_score,
            score_distribution=self._calculate_distribution(all_scores),
            recommendation_distribution=self._count_recommendations(ranked_candidates),
            filters_applied={
                "min_score": min_score,
                "limit": limit,
                "include_stages": include_stages,
                "exclude_statuses": exclude_statuses
            }
        )

    async def _get_applications(
        self,
        job_id: UUID,
        include_stages: Optional[List[str]] = None,
        exclude_statuses: Optional[List[str]] = None
    ) -> List[Any]:
        """Get applications for ranking."""
        query = """
            SELECT
                a.id as application_id,
                a.candidate_id,
                a.status as application_status,
                a.stage as application_stage,
                a.applied_date,
                a.ai_match_score,
                a.expected_salary,
                c.first_name,
                c.last_name,
                c.email,
                c.total_experience_years,
                c.skills,
                c.current_designation,
                ais.overall_score as ai_interview_score,
                aie.overall_score as ai_eval_score,
                aie.recommendation as ai_recommendation,
                aie.summary as ai_summary,
                aie.strengths as ai_strengths,
                aie.areas_for_improvement as ai_areas
            FROM applications a
            JOIN candidates c ON a.candidate_id = c.id
            LEFT JOIN ai_interview_sessions ais ON ais.application_id = a.id
            LEFT JOIN ai_interview_evaluations aie ON aie.session_id = ais.id
            WHERE a.job_opening_id = :job_id
        """

        params = {"job_id": job_id}

        if include_stages:
            query += " AND a.stage = ANY(:stages)"
            params["stages"] = include_stages

        if exclude_statuses:
            query += " AND a.status != ALL(:exclude_statuses)"
            params["exclude_statuses"] = exclude_statuses

        result = await self.db.execute(text(query).bindparams(**params))
        return result.fetchall()

    async def _calculate_candidate_score(
        self,
        application: Any,
        job: Any
    ) -> CandidateRankData:
        """Calculate composite ranking score for a candidate."""

        component_scores = {}

        # 1. AI Interview Score (0-100)
        ai_interview_score = None
        if application.ai_eval_score:
            # Convert 0-10 scale to 0-100
            ai_interview_score = float(application.ai_eval_score) * 10
            component_scores['ai_interview'] = ai_interview_score
        elif application.ai_interview_score:
            ai_interview_score = float(application.ai_interview_score) * 10
            component_scores['ai_interview'] = ai_interview_score

        # 2. Resume Match Score (0-100)
        resume_match_score = None
        if application.ai_match_score:
            resume_match_score = float(application.ai_match_score)
            component_scores['resume_match'] = resume_match_score

        # 3. Experience Fit Score (0-100)
        experience_fit_score = self._calculate_experience_fit(
            candidate_experience=application.total_experience_years,
            job_min=job.experience_min,
            job_max=job.experience_max
        )
        component_scores['experience_fit'] = experience_fit_score

        # 4. Skills Match Score (0-100)
        skills_match_score = self._calculate_skills_match(
            candidate_skills=application.skills,
            job_skills=job.skills_required
        )
        component_scores['skills_match'] = skills_match_score

        # 5. Salary Fit Score (0-100)
        salary_fit_score = self._calculate_salary_fit(
            expected_salary=application.expected_salary,
            job_min=job.salary_min,
            job_max=job.salary_max
        )
        component_scores['salary_fit'] = salary_fit_score

        # Calculate weighted composite score
        composite_score = self._calculate_composite_score(component_scores)

        # Parse strengths/concerns from AI evaluation
        strengths = []
        concerns = []
        if application.ai_strengths:
            try:
                if isinstance(application.ai_strengths, str):
                    strengths = application.ai_strengths.split("|")
                else:
                    strengths = list(application.ai_strengths)
            except Exception:
                pass

        if application.ai_areas:
            try:
                if isinstance(application.ai_areas, str):
                    concerns = application.ai_areas.split("|")
                else:
                    concerns = list(application.ai_areas)
            except Exception:
                pass

        return CandidateRankData(
            application_id=application.application_id,
            candidate_id=application.candidate_id,
            candidate_name=f"{application.first_name} {application.last_name}",
            candidate_email=application.email,
            composite_score=composite_score,
            rank_position=0,  # Will be set after sorting
            percentile=0,     # Will be set after sorting
            tier=RankingTier.QUALIFIED,  # Will be set after sorting
            ai_interview_score=ai_interview_score,
            resume_match_score=resume_match_score,
            experience_fit_score=experience_fit_score,
            skills_match_score=skills_match_score,
            salary_fit_score=salary_fit_score,
            ai_recommendation=application.ai_recommendation,
            ai_summary=application.ai_summary,
            strengths=strengths[:5],
            concerns=concerns[:3],
            application_status=application.application_status,
            application_stage=application.application_stage,
            applied_date=application.applied_date,
            component_breakdown=component_scores
        )

    def _calculate_composite_score(self, component_scores: Dict[str, float]) -> float:
        """Calculate weighted composite score from components."""
        total_weight = 0
        weighted_sum = 0

        for component, weight in self.DEFAULT_WEIGHTS.items():
            score = component_scores.get(component)
            if score is not None:
                weighted_sum += score * weight
                total_weight += weight

        # Normalize if not all components are present
        if total_weight > 0:
            return (weighted_sum / total_weight) * (total_weight / sum(self.DEFAULT_WEIGHTS.values()))

        return 0

    def _calculate_experience_fit(
        self,
        candidate_experience: Optional[int],
        job_min: Optional[int],
        job_max: Optional[int]
    ) -> float:
        """Calculate experience fit score (0-100)."""
        if candidate_experience is None:
            return 50  # Neutral score if unknown

        exp = candidate_experience or 0
        min_exp = job_min or 0
        max_exp = job_max or 99

        if min_exp <= exp <= max_exp:
            # Perfect fit
            return 100
        elif exp < min_exp:
            # Under-qualified
            gap = min_exp - exp
            return max(0, 100 - (gap * 15))  # Lose 15 points per year gap
        else:
            # Over-qualified
            gap = exp - max_exp
            return max(50, 100 - (gap * 10))  # Lose 10 points per year, min 50

    def _calculate_skills_match(
        self,
        candidate_skills: Optional[str],
        job_skills: Optional[str]
    ) -> float:
        """Calculate skills match score (0-100)."""
        if not job_skills:
            return 75  # No requirements, neutral-positive

        if not candidate_skills:
            return 25  # No skills listed, low score

        # Parse skills (comma-separated or JSON)
        def parse_skills(skills_str: str) -> set:
            if not skills_str:
                return set()
            # Clean and normalize
            skills_str = skills_str.lower()
            # Try JSON parse
            try:
                skills_list = json.loads(skills_str)
                return {s.strip().lower() for s in skills_list if s}
            except (json.JSONDecodeError, TypeError):
                pass
            # Comma-separated
            return {s.strip().lower() for s in re.split(r'[,;|]', skills_str) if s.strip()}

        candidate_set = parse_skills(candidate_skills)
        required_set = parse_skills(job_skills)

        if not required_set:
            return 75

        # Calculate overlap
        matches = candidate_set.intersection(required_set)
        match_ratio = len(matches) / len(required_set)

        # Bonus for having extra relevant skills
        extra_skills = len(candidate_set) - len(matches)
        bonus = min(extra_skills * 2, 10)  # Up to 10 bonus points

        return min(100, match_ratio * 90 + bonus)

    def _calculate_salary_fit(
        self,
        expected_salary: Optional[float],
        job_min: Optional[float],
        job_max: Optional[float]
    ) -> float:
        """Calculate salary expectations fit score (0-100)."""
        if expected_salary is None:
            return 75  # Neutral if not specified

        if job_min is None and job_max is None:
            return 75  # No budget constraints

        exp = float(expected_salary)
        min_sal = float(job_min) if job_min else 0
        max_sal = float(job_max) if job_max else float('inf')

        if min_sal <= exp <= max_sal:
            # Within range - perfect fit
            return 100
        elif exp < min_sal:
            # Below range - slight concern (undervaluing themselves?)
            return 80
        else:
            # Above range
            if max_sal > 0:
                excess_ratio = (exp - max_sal) / max_sal
                return max(30, 100 - (excess_ratio * 100))
            return 50

    def _determine_tier(self, score: float) -> RankingTier:
        """Determine ranking tier from score."""
        for tier, threshold in self.TIER_THRESHOLDS.items():
            if score >= threshold:
                return tier
        return RankingTier.NOT_RECOMMENDED

    def _calculate_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution."""
        distribution = {
            "90-100 (Exceptional)": 0,
            "80-89 (Excellent)": 0,
            "70-79 (Good)": 0,
            "60-69 (Above Average)": 0,
            "50-59 (Average)": 0,
            "40-49 (Below Average)": 0,
            "0-39 (Poor)": 0
        }

        for score in scores:
            if score >= 90:
                distribution["90-100 (Exceptional)"] += 1
            elif score >= 80:
                distribution["80-89 (Excellent)"] += 1
            elif score >= 70:
                distribution["70-79 (Good)"] += 1
            elif score >= 60:
                distribution["60-69 (Above Average)"] += 1
            elif score >= 50:
                distribution["50-59 (Average)"] += 1
            elif score >= 40:
                distribution["40-49 (Below Average)"] += 1
            else:
                distribution["0-39 (Poor)"] += 1

        return distribution

    def _count_recommendations(self, candidates: List[CandidateRankData]) -> Dict[str, int]:
        """Count AI recommendations."""
        counts = {
            "strong_yes": 0,
            "yes": 0,
            "maybe": 0,
            "no": 0,
            "strong_no": 0,
            "pending": 0
        }

        for c in candidates:
            rec = c.ai_recommendation
            if rec in counts:
                counts[rec] += 1
            else:
                counts["pending"] += 1

        return counts

    async def update_ranklist_entry(
        self,
        application_id: UUID,
        job_id: UUID
    ) -> None:
        """Update or create a ranklist entry for a single application."""
        # Get the full ranklist to calculate proper rank
        ranklist = await self.generate_ranklist(job_id, limit=1000)

        # Find this application in the list
        for candidate in ranklist.rankings:
            if candidate.application_id == application_id:
                # Update the database entry
                await self.db.execute(
                    text("""
                        INSERT INTO candidate_ranklist (
                            id, application_id, job_id, candidate_id,
                            rank_position, composite_score, component_scores,
                            percentile, ai_recommendation, is_current,
                            generated_at, created_at
                        ) VALUES (
                            gen_random_uuid(), :app_id, :job_id, :candidate_id,
                            :rank, :score, :components,
                            :percentile, :recommendation, TRUE,
                            NOW(), NOW()
                        )
                        ON CONFLICT (application_id)
                        DO UPDATE SET
                            rank_position = :rank,
                            composite_score = :score,
                            component_scores = :components,
                            percentile = :percentile,
                            ai_recommendation = :recommendation,
                            generated_at = NOW(),
                            is_current = TRUE
                    """).bindparams(
                        app_id=application_id,
                        job_id=job_id,
                        candidate_id=candidate.candidate_id,
                        rank=candidate.rank_position,
                        score=candidate.composite_score,
                        components=json.dumps(candidate.component_breakdown),
                        percentile=candidate.percentile,
                        recommendation=candidate.ai_recommendation
                    )
                )
                await self.db.commit()
                break

    async def get_candidate_rank(
        self,
        application_id: UUID,
        job_id: UUID
    ) -> Optional[CandidateRankData]:
        """Get ranking data for a specific application."""
        ranklist = await self.generate_ranklist(job_id, limit=1000)

        for candidate in ranklist.rankings:
            if candidate.application_id == application_id:
                return candidate

        return None
