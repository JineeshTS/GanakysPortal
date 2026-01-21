"""
Comprehensive AI Evaluation Service
Handles detailed candidate evaluation with bias mitigation and report generation
"""
import json
import re
from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import UUID
from dataclasses import dataclass, field
from enum import Enum

from app.core.config import settings


class RecommendationLevel(str, Enum):
    STRONG_YES = "strong_yes"
    YES = "yes"
    MAYBE = "maybe"
    NO = "no"
    STRONG_NO = "strong_no"


@dataclass
class ComponentScore:
    """Individual scoring component."""
    name: str
    score: float
    weight: float
    max_score: float = 10.0
    reasoning: str = ""
    evidence: List[str] = field(default_factory=list)

    @property
    def weighted_score(self) -> float:
        return (self.score / self.max_score) * self.weight * 100


@dataclass
class BiasCheckResult:
    """Result of bias detection check."""
    passed: bool
    flags: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    confidence: float = 0.0


@dataclass
class EvaluationReport:
    """Complete evaluation report."""
    session_id: str
    candidate_id: str
    job_id: str

    # Overall assessment
    overall_score: float
    recommendation: RecommendationLevel
    recommendation_confidence: float

    # Component scores
    technical_score: float
    communication_score: float
    problem_solving_score: float
    cultural_fit_score: float
    enthusiasm_score: float

    # Detailed breakdown
    component_scores: List[ComponentScore]

    # Qualitative assessment
    strengths: List[str]
    areas_for_improvement: List[str]
    red_flags: List[str]

    # Detailed feedback
    summary: str
    detailed_feedback: str

    # Bias check
    bias_check: BiasCheckResult

    # Comparison data
    percentile_rank: Optional[float] = None
    comparison_notes: Optional[str] = None

    # Metadata
    evaluated_at: datetime = field(default_factory=datetime.utcnow)
    evaluation_version: str = "1.0"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "candidate_id": self.candidate_id,
            "job_id": self.job_id,
            "overall_score": self.overall_score,
            "recommendation": self.recommendation.value,
            "recommendation_confidence": self.recommendation_confidence,
            "technical_score": self.technical_score,
            "communication_score": self.communication_score,
            "problem_solving_score": self.problem_solving_score,
            "cultural_fit_score": self.cultural_fit_score,
            "enthusiasm_score": self.enthusiasm_score,
            "component_scores": [
                {
                    "name": c.name,
                    "score": c.score,
                    "weight": c.weight,
                    "weighted_score": c.weighted_score,
                    "reasoning": c.reasoning,
                    "evidence": c.evidence
                }
                for c in self.component_scores
            ],
            "strengths": self.strengths,
            "areas_for_improvement": self.areas_for_improvement,
            "red_flags": self.red_flags,
            "summary": self.summary,
            "detailed_feedback": self.detailed_feedback,
            "bias_check": {
                "passed": self.bias_check.passed,
                "flags": self.bias_check.flags,
                "recommendations": self.bias_check.recommendations,
                "confidence": self.bias_check.confidence
            },
            "percentile_rank": self.percentile_rank,
            "comparison_notes": self.comparison_notes,
            "evaluated_at": self.evaluated_at.isoformat(),
            "evaluation_version": self.evaluation_version
        }


class EvaluationService:
    """Service for comprehensive AI evaluation of interview sessions."""

    # Scoring weights for different components
    DEFAULT_WEIGHTS = {
        "technical_competency": 0.30,
        "communication_skills": 0.20,
        "problem_solving": 0.20,
        "cultural_fit": 0.15,
        "enthusiasm": 0.10,
        "professionalism": 0.05,
    }

    # Bias-sensitive terms to check
    BIAS_INDICATORS = [
        # Gender indicators
        r"\b(he|she|him|her|his|hers|man|woman|male|female|gentleman|lady)\b",
        # Age indicators
        r"\b(young|old|mature|senior|junior|millennial|boomer|gen[- ]?[xyz])\b",
        # Ethnicity/nationality indicators
        r"\b(accent|foreign|native|immigrant|ethnic|racial)\b",
        # Appearance indicators
        r"\b(attractive|handsome|pretty|appearance|dressed|groomed)\b",
        # Family status indicators
        r"\b(married|single|children|kids|family|pregnant|maternity|paternity)\b",
    ]

    def __init__(self):
        self.openai_api_key = getattr(settings, 'OPENAI_API_KEY', '')
        self.anthropic_api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')

    async def _call_ai(self, prompt: str, system_prompt: str = "") -> str:
        """Call AI API for evaluation."""
        import httpx

        if self.anthropic_api_key:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": self.anthropic_api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json",
                    },
                    json={
                        "model": "claude-sonnet-4-20250514",
                        "max_tokens": 4096,
                        "system": system_prompt or "You are an expert HR professional and interview evaluator.",
                        "messages": [{"role": "user", "content": prompt}]
                    },
                    timeout=60.0
                )
                data = response.json()
                return data["content"][0]["text"]
        elif self.openai_api_key:
            async with httpx.AsyncClient() as client:
                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4-turbo-preview",
                        "messages": messages,
                        "max_tokens": 4096,
                        "response_format": {"type": "json_object"}
                    },
                    timeout=60.0
                )
                data = response.json()
                return data["choices"][0]["message"]["content"]
        else:
            raise ValueError("No AI API key configured")

    async def generate_comprehensive_evaluation(
        self,
        session_id: UUID,
        candidate_id: UUID,
        job_id: UUID,
        job_title: str,
        job_description: str,
        job_requirements: str,
        qa_pairs: List[Dict[str, Any]],
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> EvaluationReport:
        """
        Generate a comprehensive evaluation report for an interview session.

        Args:
            session_id: Interview session UUID
            candidate_id: Candidate UUID
            job_id: Job opening UUID
            job_title: Title of the position
            job_description: Job description
            job_requirements: Required skills/qualifications
            qa_pairs: List of question-answer pairs with any existing scores
            candidate_profile: Optional candidate profile data

        Returns:
            EvaluationReport with comprehensive assessment
        """
        # Format Q&A for evaluation
        qa_formatted = self._format_qa_pairs(qa_pairs)

        # Generate detailed evaluation
        evaluation_data = await self._evaluate_interview(
            job_title=job_title,
            job_description=job_description,
            job_requirements=job_requirements,
            qa_formatted=qa_formatted,
            candidate_profile=candidate_profile
        )

        # Run bias check
        bias_result = await self._check_for_bias(evaluation_data)

        # If bias detected, re-evaluate with stricter guidelines
        if not bias_result.passed:
            evaluation_data = await self._evaluate_interview_bias_free(
                job_title=job_title,
                job_description=job_description,
                job_requirements=job_requirements,
                qa_formatted=qa_formatted,
                bias_flags=bias_result.flags
            )
            bias_result = await self._check_for_bias(evaluation_data)

        # Build component scores
        component_scores = self._build_component_scores(evaluation_data)

        # Calculate overall score
        overall_score = sum(c.weighted_score for c in component_scores) / 100 * 10

        # Determine recommendation
        recommendation = self._determine_recommendation(
            overall_score,
            evaluation_data.get("red_flags", []),
            evaluation_data.get("critical_strengths", [])
        )

        return EvaluationReport(
            session_id=str(session_id),
            candidate_id=str(candidate_id),
            job_id=str(job_id),
            overall_score=overall_score,
            recommendation=recommendation,
            recommendation_confidence=evaluation_data.get("confidence", 0.8),
            technical_score=evaluation_data.get("technical_competency", 0),
            communication_score=evaluation_data.get("communication_skills", 0),
            problem_solving_score=evaluation_data.get("problem_solving", 0),
            cultural_fit_score=evaluation_data.get("cultural_fit", 0),
            enthusiasm_score=evaluation_data.get("enthusiasm", 0),
            component_scores=component_scores,
            strengths=evaluation_data.get("strengths", []),
            areas_for_improvement=evaluation_data.get("areas_for_improvement", []),
            red_flags=evaluation_data.get("red_flags", []),
            summary=evaluation_data.get("summary", ""),
            detailed_feedback=evaluation_data.get("detailed_feedback", ""),
            bias_check=bias_result
        )

    def _format_qa_pairs(self, qa_pairs: List[Dict[str, Any]]) -> str:
        """Format Q&A pairs for the evaluation prompt."""
        formatted = []
        for i, qa in enumerate(qa_pairs, 1):
            formatted.append(f"""
Question {i}: {qa.get('question', '')}
Category: {qa.get('category', 'general')}
Type: {qa.get('type', 'standard')}

Candidate's Response:
{qa.get('answer', '[No response provided]')}

Response Duration: {qa.get('duration', 'N/A')} seconds
""")
        return "\n---\n".join(formatted)

    async def _evaluate_interview(
        self,
        job_title: str,
        job_description: str,
        job_requirements: str,
        qa_formatted: str,
        candidate_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate detailed evaluation using AI."""

        system_prompt = """You are an expert interview evaluator with extensive experience in hiring for
technical and professional roles. Your evaluations are:
- Fair and unbiased, focusing only on job-relevant criteria
- Evidence-based, citing specific examples from responses
- Constructive, providing actionable feedback
- Consistent, using standardized scoring criteria

IMPORTANT: Focus ONLY on the content and quality of responses. Do not consider or mention:
- Gender, age, ethnicity, or any demographic characteristics
- Accent or language proficiency (unless directly relevant to job requirements)
- Physical appearance or presentation
- Personal circumstances or family status"""

        prompt = f"""Evaluate this interview for the position of {job_title}.

JOB DESCRIPTION:
{job_description}

KEY REQUIREMENTS:
{job_requirements}

INTERVIEW TRANSCRIPT:
{qa_formatted}

Provide a comprehensive evaluation in JSON format with these exact fields:

{{
    "technical_competency": <score 0-10>,
    "technical_reasoning": "<detailed explanation with specific examples>",
    "technical_evidence": ["<quote 1>", "<quote 2>"],

    "communication_skills": <score 0-10>,
    "communication_reasoning": "<detailed explanation>",
    "communication_evidence": ["<example 1>", "<example 2>"],

    "problem_solving": <score 0-10>,
    "problem_solving_reasoning": "<detailed explanation>",
    "problem_solving_evidence": ["<example>"],

    "cultural_fit": <score 0-10>,
    "cultural_fit_reasoning": "<explanation based on values and work style>",

    "enthusiasm": <score 0-10>,
    "enthusiasm_reasoning": "<explanation>",

    "professionalism": <score 0-10>,
    "professionalism_reasoning": "<explanation>",

    "strengths": [
        "<specific strength 1 with evidence>",
        "<specific strength 2 with evidence>",
        "<specific strength 3 with evidence>"
    ],

    "areas_for_improvement": [
        "<specific area 1 with recommendation>",
        "<specific area 2 with recommendation>"
    ],

    "red_flags": [
        "<any concerning patterns or gaps - empty array if none>"
    ],

    "critical_strengths": [
        "<standout qualities that make this candidate exceptional - empty if none>"
    ],

    "summary": "<2-3 sentence executive summary>",

    "detailed_feedback": "<comprehensive paragraph with specific observations,
    suitable for sharing with hiring manager>",

    "confidence": <0.0-1.0 confidence in this evaluation>,

    "follow_up_questions": [
        "<suggested follow-up question for human interviewer>",
        "<another follow-up>"
    ]
}}

Be thorough, fair, and evidence-based in your evaluation."""

        response = await self._call_ai(prompt, system_prompt)

        # Parse JSON response
        try:
            # Extract JSON from response if wrapped in markdown
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                response = json_match.group(1)
            return json.loads(response)
        except json.JSONDecodeError:
            # Attempt to extract structured data if JSON parsing fails
            return self._parse_unstructured_evaluation(response)

    async def _evaluate_interview_bias_free(
        self,
        job_title: str,
        job_description: str,
        job_requirements: str,
        qa_formatted: str,
        bias_flags: List[str]
    ) -> Dict[str, Any]:
        """Re-evaluate with explicit bias mitigation after flags detected."""

        system_prompt = f"""You are an expert interview evaluator conducting a BIAS-FREE evaluation.

PREVIOUS EVALUATION CONTAINED POTENTIAL BIAS IN THESE AREAS:
{json.dumps(bias_flags, indent=2)}

You MUST:
1. Focus EXCLUSIVELY on job-relevant skills and competencies
2. Base scores ONLY on the content of responses
3. NOT reference any protected characteristics
4. Provide evidence-based reasoning for all scores
5. Apply the same standards regardless of how the candidate expresses themselves

This is a legally-compliant evaluation that could be reviewed by EEOC."""

        # Same prompt structure as above but with stricter guidelines
        prompt = f"""Re-evaluate this interview with strict bias-free criteria.

POSITION: {job_title}

REQUIREMENTS:
{job_requirements}

RESPONSES:
{qa_formatted}

Provide evaluation in JSON format focusing ONLY on demonstrated competencies.
Include same fields as standard evaluation but with bias-free reasoning."""

        response = await self._call_ai(prompt, system_prompt)

        try:
            json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response)
            if json_match:
                response = json_match.group(1)
            return json.loads(response)
        except json.JSONDecodeError:
            return self._parse_unstructured_evaluation(response)

    async def _check_for_bias(self, evaluation_data: Dict[str, Any]) -> BiasCheckResult:
        """Check evaluation for potential bias indicators."""

        flags = []
        recommendations = []

        # Convert evaluation to text for scanning
        eval_text = json.dumps(evaluation_data).lower()

        # Check for bias indicators
        for pattern in self.BIAS_INDICATORS:
            matches = re.findall(pattern, eval_text, re.IGNORECASE)
            if matches:
                flags.append(f"Potential bias indicator found: {', '.join(set(matches))}")

        # Check for subjective language
        subjective_terms = [
            r"\b(like|likeable|pleasant|nice|friendly)\b",
            r"\b(aggressive|pushy|bossy|emotional)\b",
            r"\b(articulate|well-spoken)\b",  # Can be coded language
        ]

        for pattern in subjective_terms:
            if re.search(pattern, eval_text, re.IGNORECASE):
                flags.append(f"Subjective language detected matching: {pattern}")

        # Check for consistency issues
        if "technical_competency" in evaluation_data:
            tech_score = evaluation_data["technical_competency"]
            tech_reasoning = evaluation_data.get("technical_reasoning", "")

            # Flag if high score but no evidence
            if tech_score >= 8 and len(tech_reasoning) < 50:
                flags.append("High technical score without substantial evidence")

        # Calculate confidence based on flags
        if not flags:
            confidence = 0.95
        elif len(flags) <= 2:
            confidence = 0.7
            recommendations.append("Consider human review of this evaluation")
        else:
            confidence = 0.4
            recommendations.append("Recommend re-evaluation with stricter guidelines")
            recommendations.append("Flag for HR review before sharing")

        return BiasCheckResult(
            passed=len(flags) == 0,
            flags=flags,
            recommendations=recommendations,
            confidence=confidence
        )

    def _build_component_scores(self, evaluation_data: Dict[str, Any]) -> List[ComponentScore]:
        """Build component scores from evaluation data."""
        components = []

        for name, weight in self.DEFAULT_WEIGHTS.items():
            score = evaluation_data.get(name, 5.0)
            reasoning = evaluation_data.get(f"{name}_reasoning", "")
            evidence = evaluation_data.get(f"{name}_evidence", [])

            components.append(ComponentScore(
                name=name,
                score=float(score) if score else 5.0,
                weight=weight,
                reasoning=reasoning,
                evidence=evidence if isinstance(evidence, list) else []
            ))

        return components

    def _determine_recommendation(
        self,
        overall_score: float,
        red_flags: List[str],
        critical_strengths: List[str]
    ) -> RecommendationLevel:
        """Determine recommendation level based on score and qualitative factors."""

        # Adjust score based on flags and strengths
        adjusted_score = overall_score

        # Red flags reduce recommendation
        if red_flags:
            adjusted_score -= len(red_flags) * 0.5

        # Critical strengths boost recommendation
        if critical_strengths:
            adjusted_score += min(len(critical_strengths) * 0.3, 1.0)

        # Map to recommendation
        if adjusted_score >= 8.5:
            return RecommendationLevel.STRONG_YES
        elif adjusted_score >= 7.0:
            return RecommendationLevel.YES
        elif adjusted_score >= 5.5:
            return RecommendationLevel.MAYBE
        elif adjusted_score >= 4.0:
            return RecommendationLevel.NO
        else:
            return RecommendationLevel.STRONG_NO

    def _parse_unstructured_evaluation(self, response: str) -> Dict[str, Any]:
        """Fallback parser for non-JSON responses."""
        # Basic structure with defaults
        data = {
            "technical_competency": 5.0,
            "communication_skills": 5.0,
            "problem_solving": 5.0,
            "cultural_fit": 5.0,
            "enthusiasm": 5.0,
            "professionalism": 5.0,
            "strengths": [],
            "areas_for_improvement": [],
            "red_flags": [],
            "summary": response[:500] if response else "Evaluation could not be parsed.",
            "detailed_feedback": response,
            "confidence": 0.5
        }

        # Try to extract scores from text
        score_patterns = {
            "technical": r"technical[:\s]+(\d+(?:\.\d+)?)",
            "communication": r"communication[:\s]+(\d+(?:\.\d+)?)",
            "problem": r"problem[- ]solving[:\s]+(\d+(?:\.\d+)?)",
        }

        for key, pattern in score_patterns.items():
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                try:
                    score = float(match.group(1))
                    if 0 <= score <= 10:
                        data[f"{key}_competency" if key == "technical" else f"{key}_skills" if key == "communication" else "problem_solving"] = score
                except ValueError:
                    pass

        return data

    async def generate_comparison_report(
        self,
        evaluations: List[EvaluationReport],
        job_id: UUID
    ) -> Dict[str, Any]:
        """Generate a comparison report for multiple candidates."""

        if not evaluations:
            return {"error": "No evaluations to compare"}

        # Sort by overall score
        sorted_evals = sorted(evaluations, key=lambda e: e.overall_score, reverse=True)

        # Calculate percentiles
        total = len(sorted_evals)
        for i, eval in enumerate(sorted_evals):
            eval.percentile_rank = ((total - i) / total) * 100

        # Build comparison matrix
        comparison = {
            "job_id": str(job_id),
            "total_candidates": total,
            "evaluation_date": datetime.utcnow().isoformat(),
            "rankings": [
                {
                    "rank": i + 1,
                    "candidate_id": e.candidate_id,
                    "session_id": e.session_id,
                    "overall_score": e.overall_score,
                    "recommendation": e.recommendation.value,
                    "percentile": e.percentile_rank,
                    "key_strengths": e.strengths[:3],
                    "concerns": e.red_flags[:2] if e.red_flags else [],
                    "component_summary": {
                        "technical": e.technical_score,
                        "communication": e.communication_score,
                        "problem_solving": e.problem_solving_score
                    }
                }
                for i, e in enumerate(sorted_evals)
            ],
            "statistics": {
                "average_score": sum(e.overall_score for e in sorted_evals) / total,
                "highest_score": sorted_evals[0].overall_score,
                "lowest_score": sorted_evals[-1].overall_score,
                "score_distribution": self._calculate_distribution([e.overall_score for e in sorted_evals])
            },
            "recommendations": {
                "strong_yes": sum(1 for e in sorted_evals if e.recommendation == RecommendationLevel.STRONG_YES),
                "yes": sum(1 for e in sorted_evals if e.recommendation == RecommendationLevel.YES),
                "maybe": sum(1 for e in sorted_evals if e.recommendation == RecommendationLevel.MAYBE),
                "no": sum(1 for e in sorted_evals if e.recommendation == RecommendationLevel.NO),
                "strong_no": sum(1 for e in sorted_evals if e.recommendation == RecommendationLevel.STRONG_NO)
            }
        }

        return comparison

    def _calculate_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate score distribution buckets."""
        distribution = {
            "9-10 (Excellent)": 0,
            "7-8 (Good)": 0,
            "5-6 (Average)": 0,
            "3-4 (Below Average)": 0,
            "0-2 (Poor)": 0
        }

        for score in scores:
            if score >= 9:
                distribution["9-10 (Excellent)"] += 1
            elif score >= 7:
                distribution["7-8 (Good)"] += 1
            elif score >= 5:
                distribution["5-6 (Average)"] += 1
            elif score >= 3:
                distribution["3-4 (Below Average)"] += 1
            else:
                distribution["0-2 (Poor)"] += 1

        return distribution
