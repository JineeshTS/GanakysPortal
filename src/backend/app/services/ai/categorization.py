"""
AI-003: Transaction Categorization Service
AI-004: Confidence Scoring
Automatically categorize financial transactions with confidence scoring
"""
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class TransactionCategory(str, Enum):
    """Transaction categories."""
    # Income
    SALES_REVENUE = "sales_revenue"
    SERVICE_INCOME = "service_income"
    INTEREST_INCOME = "interest_income"
    OTHER_INCOME = "other_income"

    # Expenses
    SALARY_WAGES = "salary_wages"
    RENT = "rent"
    UTILITIES = "utilities"
    OFFICE_SUPPLIES = "office_supplies"
    TRAVEL = "travel"
    PROFESSIONAL_FEES = "professional_fees"
    MARKETING = "marketing"
    INSURANCE = "insurance"
    MAINTENANCE = "maintenance"
    SOFTWARE_SUBSCRIPTIONS = "software_subscriptions"
    BANK_CHARGES = "bank_charges"
    TAXES = "taxes"
    MISCELLANEOUS = "miscellaneous"

    # Assets
    EQUIPMENT_PURCHASE = "equipment_purchase"
    VEHICLE_PURCHASE = "vehicle_purchase"

    # Liability
    LOAN_REPAYMENT = "loan_repayment"

    UNCATEGORIZED = "uncategorized"


@dataclass
class CategorizationResult:
    """Categorization result with confidence."""
    category: TransactionCategory
    confidence: float
    sub_category: Optional[str]
    reasoning: str
    alternative_categories: List[Tuple[TransactionCategory, float]]
    requires_review: bool


class TransactionCategorizationService:
    """
    AI-powered transaction categorization with confidence scoring.

    Features:
    - Pattern-based categorization
    - AI-enhanced classification
    - Confidence scoring (AI-004)
    - Learning from corrections
    - Vendor recognition
    """

    # Keyword patterns for rule-based categorization
    CATEGORY_PATTERNS = {
        TransactionCategory.SALARY_WAGES: [
            "salary", "wages", "payroll", "stipend", "bonus", "incentive"
        ],
        TransactionCategory.RENT: [
            "rent", "lease", "property", "office space"
        ],
        TransactionCategory.UTILITIES: [
            "electricity", "power", "water", "internet", "broadband",
            "telephone", "mobile", "tata", "airtel", "jio", "bsnl"
        ],
        TransactionCategory.TRAVEL: [
            "flight", "train", "taxi", "uber", "ola", "makemytrip",
            "goibibo", "irctc", "hotel", "accommodation"
        ],
        TransactionCategory.SOFTWARE_SUBSCRIPTIONS: [
            "aws", "azure", "google cloud", "github", "slack", "zoom",
            "microsoft", "adobe", "subscription", "saas"
        ],
        TransactionCategory.BANK_CHARGES: [
            "bank charge", "service charge", "transaction fee", "gst on bank"
        ],
        TransactionCategory.PROFESSIONAL_FEES: [
            "consultant", "legal", "audit", "chartered accountant", "ca fees",
            "professional", "advisory"
        ],
        TransactionCategory.MARKETING: [
            "google ads", "facebook", "marketing", "advertisement", "promotion"
        ],
        TransactionCategory.OFFICE_SUPPLIES: [
            "stationery", "office supplies", "amazon", "flipkart"
        ],
    }

    # Vendor to category mapping (learned patterns)
    VENDOR_MAPPINGS: Dict[str, TransactionCategory] = {}

    # Confidence thresholds
    HIGH_CONFIDENCE_THRESHOLD = 0.85
    REVIEW_THRESHOLD = 0.60

    def __init__(self, ai_service=None):
        """Initialize with optional AI service for enhanced categorization."""
        self.ai_service = ai_service
        self._correction_history: List[Dict] = []

    async def categorize_transaction(
        self,
        transaction: Dict[str, Any],
        use_ai: bool = True
    ) -> CategorizationResult:
        """
        Categorize a single transaction.

        Args:
            transaction: Transaction details including:
                - description: Transaction description
                - amount: Transaction amount
                - type: debit/credit
                - vendor: Optional vendor name
                - date: Transaction date
            use_ai: Whether to use AI for enhanced categorization

        Returns:
            CategorizationResult with category and confidence
        """
        description = transaction.get("description", "").lower()
        vendor = transaction.get("vendor", "").lower()
        amount = abs(transaction.get("amount", 0))

        # Step 1: Check vendor mapping
        vendor_category = self._check_vendor_mapping(vendor)
        if vendor_category:
            return CategorizationResult(
                category=vendor_category,
                confidence=0.95,
                sub_category=None,
                reasoning=f"Matched vendor pattern: {vendor}",
                alternative_categories=[],
                requires_review=False
            )

        # Step 2: Rule-based pattern matching
        rule_result = self._rule_based_categorization(description)

        # Step 3: AI-enhanced if enabled and confidence is low
        if use_ai and self.ai_service and rule_result[1] < self.HIGH_CONFIDENCE_THRESHOLD:
            ai_result = await self._ai_categorization(transaction)

            # Combine results
            final_category, final_confidence = self._combine_results(
                rule_result, ai_result
            )
        else:
            final_category, final_confidence = rule_result

        # Generate alternatives
        alternatives = self._get_alternative_categories(description, final_category)

        return CategorizationResult(
            category=final_category,
            confidence=final_confidence,
            sub_category=self._detect_sub_category(description, final_category),
            reasoning=self._generate_reasoning(description, final_category),
            alternative_categories=alternatives,
            requires_review=final_confidence < self.REVIEW_THRESHOLD
        )

    async def categorize_batch(
        self,
        transactions: List[Dict[str, Any]]
    ) -> List[CategorizationResult]:
        """Categorize multiple transactions."""
        results = []
        for txn in transactions:
            result = await self.categorize_transaction(txn)
            results.append(result)
        return results

    def learn_from_correction(
        self,
        transaction: Dict[str, Any],
        original_category: TransactionCategory,
        corrected_category: TransactionCategory,
        user_id: str
    ) -> None:
        """
        Learn from user corrections to improve future categorization.
        Part of AI-008 Learning system.
        """
        self._correction_history.append({
            "transaction": transaction,
            "original": original_category,
            "corrected": corrected_category,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        })

        # Update vendor mapping if vendor is present
        vendor = transaction.get("vendor", "").lower()
        if vendor and len(vendor) > 3:
            self.VENDOR_MAPPINGS[vendor] = corrected_category

    def get_confidence_score(
        self,
        result: CategorizationResult
    ) -> Dict[str, Any]:
        """
        Get detailed confidence scoring breakdown (AI-004).

        Returns confidence factors and recommendations.
        """
        factors = {
            "pattern_match_score": 0.0,
            "vendor_match_score": 0.0,
            "ai_score": 0.0,
            "historical_accuracy": 0.0
        }

        # Calculate individual factors
        if "vendor" in result.reasoning.lower():
            factors["vendor_match_score"] = 0.95

        if "pattern" in result.reasoning.lower():
            factors["pattern_match_score"] = 0.80

        # Historical accuracy for this category
        factors["historical_accuracy"] = self._get_category_accuracy(result.category)

        return {
            "overall_confidence": result.confidence,
            "confidence_level": self._confidence_level(result.confidence),
            "factors": factors,
            "recommendations": self._get_recommendations(result)
        }

    def _check_vendor_mapping(self, vendor: str) -> Optional[TransactionCategory]:
        """Check if vendor has a known category mapping."""
        vendor_lower = vendor.lower()
        for known_vendor, category in self.VENDOR_MAPPINGS.items():
            if known_vendor in vendor_lower or vendor_lower in known_vendor:
                return category
        return None

    def _rule_based_categorization(
        self,
        description: str
    ) -> Tuple[TransactionCategory, float]:
        """Apply rule-based categorization."""
        best_match = (TransactionCategory.UNCATEGORIZED, 0.0)

        for category, patterns in self.CATEGORY_PATTERNS.items():
            for pattern in patterns:
                if pattern in description:
                    # Calculate match quality
                    match_ratio = len(pattern) / len(description) if description else 0
                    confidence = min(0.6 + match_ratio * 0.3, 0.85)

                    if confidence > best_match[1]:
                        best_match = (category, confidence)

        return best_match

    async def _ai_categorization(
        self,
        transaction: Dict[str, Any]
    ) -> Tuple[TransactionCategory, float]:
        """Use AI for categorization."""
        if not self.ai_service:
            return (TransactionCategory.UNCATEGORIZED, 0.0)

        categories_list = [c.value for c in TransactionCategory]

        prompt = f"""Categorize this financial transaction:

Description: {transaction.get('description', '')}
Amount: Rs.{transaction.get('amount', 0):,.2f}
Type: {transaction.get('type', 'debit')}
Vendor: {transaction.get('vendor', 'Unknown')}

Categories: {', '.join(categories_list)}

Return JSON:
{{"category": "category_name", "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
"""

        # Simulated AI response
        return (TransactionCategory.MISCELLANEOUS, 0.70)

    def _combine_results(
        self,
        rule_result: Tuple[TransactionCategory, float],
        ai_result: Tuple[TransactionCategory, float]
    ) -> Tuple[TransactionCategory, float]:
        """Combine rule-based and AI results."""
        if rule_result[0] == ai_result[0]:
            # Same category - boost confidence
            return (rule_result[0], min(0.95, (rule_result[1] + ai_result[1]) / 1.5))

        # Different categories - pick higher confidence
        if rule_result[1] >= ai_result[1]:
            return rule_result
        return ai_result

    def _get_alternative_categories(
        self,
        description: str,
        primary: TransactionCategory
    ) -> List[Tuple[TransactionCategory, float]]:
        """Get alternative category suggestions."""
        alternatives = []
        for category, patterns in self.CATEGORY_PATTERNS.items():
            if category == primary:
                continue
            for pattern in patterns:
                if pattern in description:
                    alternatives.append((category, 0.3))
                    break
        return sorted(alternatives, key=lambda x: x[1], reverse=True)[:3]

    def _detect_sub_category(
        self,
        description: str,
        category: TransactionCategory
    ) -> Optional[str]:
        """Detect sub-category within main category."""
        if category == TransactionCategory.TRAVEL:
            if any(x in description for x in ["flight", "air"]):
                return "air_travel"
            if any(x in description for x in ["train", "irctc"]):
                return "rail_travel"
            if any(x in description for x in ["taxi", "uber", "ola"]):
                return "local_transport"
        return None

    def _generate_reasoning(
        self,
        description: str,
        category: TransactionCategory
    ) -> str:
        """Generate explanation for categorization."""
        patterns = self.CATEGORY_PATTERNS.get(category, [])
        matched = [p for p in patterns if p in description]
        if matched:
            return f"Matched pattern(s): {', '.join(matched)}"
        return "AI-based classification"

    def _confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= self.HIGH_CONFIDENCE_THRESHOLD:
            return "high"
        if confidence >= self.REVIEW_THRESHOLD:
            return "medium"
        return "low"

    def _get_category_accuracy(self, category: TransactionCategory) -> float:
        """Get historical accuracy for category."""
        corrections = [c for c in self._correction_history if c["original"] == category]
        if not corrections:
            return 0.85  # Default
        correct = len([c for c in corrections if c["original"] == c["corrected"]])
        return correct / len(corrections) if corrections else 0.85

    def _get_recommendations(
        self,
        result: CategorizationResult
    ) -> List[str]:
        """Get recommendations based on confidence."""
        recommendations = []
        if result.requires_review:
            recommendations.append("Manual review recommended due to low confidence")
        if result.alternative_categories:
            recommendations.append(f"Consider alternatives: {[a[0].value for a in result.alternative_categories[:2]]}")
        return recommendations
