"""
AI Service - BE-034, BE-035
AI integration with fallback chain
"""
from typing import Dict, Any, List, Optional, AsyncGenerator
from datetime import datetime
from enum import Enum
from dataclasses import dataclass
import json


class AIProvider(str, Enum):
    """AI providers."""
    CLAUDE = "claude"
    GEMINI = "gemini"
    GPT4 = "gpt4"
    TOGETHER = "together"


@dataclass
class AIResponse:
    """AI response."""
    content: str
    provider: AIProvider
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: int
    fallback_used: bool = False
    error: Optional[str] = None


class AIService:
    """
    AI service with provider fallback chain.

    Fallback order: Claude -> Gemini -> GPT-4 -> Together AI

    Features:
    - Multiple provider support
    - Automatic fallback on failure
    - Usage tracking
    - Rate limiting
    - Context management
    """

    # Provider configurations
    PROVIDERS = {
        AIProvider.CLAUDE: {
            "api_url": "https://api.anthropic.com/v1/messages",
            "model": "claude-3-sonnet-20240229",
            "max_tokens": 4096,
            "priority": 1,
        },
        AIProvider.GEMINI: {
            "api_url": "https://generativelanguage.googleapis.com/v1/models",
            "model": "gemini-pro",
            "max_tokens": 4096,
            "priority": 2,
        },
        AIProvider.GPT4: {
            "api_url": "https://api.openai.com/v1/chat/completions",
            "model": "gpt-4-turbo-preview",
            "max_tokens": 4096,
            "priority": 3,
        },
        AIProvider.TOGETHER: {
            "api_url": "https://api.together.xyz/v1/chat/completions",
            "model": "mistralai/Mixtral-8x7B-Instruct-v0.1",
            "max_tokens": 4096,
            "priority": 4,
        },
    }

    # System prompts for different features
    SYSTEM_PROMPTS = {
        "chat": """You are GanaPortal AI Assistant, helping users with their ERP-related queries.
You have access to company data including employees, payroll, invoices, and financial information.
Be helpful, accurate, and concise. Format responses clearly.""",

        "payroll_analysis": """You are a payroll specialist AI assistant.
Analyze payroll data and provide insights on:
- Salary trends and anomalies
- Compliance issues (PF, ESI, TDS)
- Cost optimization suggestions
Present findings clearly with specific numbers.""",

        "invoice_analysis": """You are a financial analysis AI assistant.
Analyze invoice and payment data to identify:
- Outstanding receivables and collection priorities
- Payment trends and patterns
- Cash flow projections
Provide actionable recommendations.""",

        "hr_assistant": """You are an HR assistant AI.
Help with:
- Leave balance queries
- Policy explanations
- Employee onboarding assistance
- Performance review preparation
Be professional and supportive.""",

        "report_generation": """You are a business intelligence AI assistant.
Generate comprehensive reports based on the data provided.
Include:
- Executive summary
- Key metrics and KPIs
- Trends and insights
- Recommendations
Format output in a clear, professional manner.""",
    }

    def __init__(
        self,
        api_keys: Dict[AIProvider, str],
        default_provider: AIProvider = AIProvider.CLAUDE
    ):
        self.api_keys = api_keys
        self.default_provider = default_provider
        self._fallback_order = sorted(
            self.PROVIDERS.keys(),
            key=lambda p: self.PROVIDERS[p]["priority"]
        )

    async def chat(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        feature: str = "chat",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        provider: Optional[AIProvider] = None
    ) -> AIResponse:
        """
        Send chat completion request with fallback.

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Optional system prompt (overrides feature default)
            feature: Feature type for default system prompt
            max_tokens: Maximum response tokens
            temperature: Sampling temperature
            provider: Specific provider to use (skips fallback)

        Returns:
            AIResponse with content and metadata
        """
        system = system_prompt or self.SYSTEM_PROMPTS.get(feature, self.SYSTEM_PROMPTS["chat"])

        if provider:
            return await self._call_provider(provider, messages, system, max_tokens, temperature)

        # Try providers in fallback order
        last_error = None
        for p in self._fallback_order:
            if p not in self.api_keys:
                continue

            try:
                response = await self._call_provider(p, messages, system, max_tokens, temperature)
                if not response.error:
                    response.fallback_used = (p != self._fallback_order[0])
                    return response
            except Exception as e:
                last_error = str(e)
                continue

        # All providers failed
        return AIResponse(
            content="",
            provider=self.default_provider,
            model="",
            input_tokens=0,
            output_tokens=0,
            latency_ms=0,
            error=f"All providers failed. Last error: {last_error}"
        )

    async def _call_provider(
        self,
        provider: AIProvider,
        messages: List[Dict[str, str]],
        system_prompt: str,
        max_tokens: int,
        temperature: float
    ) -> AIResponse:
        """Call specific AI provider."""
        config = self.PROVIDERS[provider]
        start_time = datetime.utcnow()

        # In production, use httpx or aiohttp for actual API calls
        # This is a simulation for demo purposes

        # Simulate response
        response_content = f"[AI Response from {provider.value}] This is a simulated response."

        latency = int((datetime.utcnow() - start_time).total_seconds() * 1000)

        return AIResponse(
            content=response_content,
            provider=provider,
            model=config["model"],
            input_tokens=len(str(messages)) // 4,  # Rough estimate
            output_tokens=len(response_content) // 4,
            latency_ms=latency
        )

    async def analyze_payroll(
        self,
        payroll_data: Dict[str, Any],
        company_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analyze payroll data and provide insights.

        Args:
            payroll_data: Payroll summary data
            company_context: Company information for context

        Returns:
            Analysis results with insights
        """
        prompt = f"""Analyze the following payroll data for {company_context.get('name', 'Company')}:

Payroll Period: {payroll_data.get('period', 'N/A')}
Total Employees: {payroll_data.get('total_employees', 0)}
Total Gross: Rs.{payroll_data.get('total_gross', 0):,.2f}
Total Net: Rs.{payroll_data.get('total_net', 0):,.2f}
Total PF: Rs.{payroll_data.get('total_pf', 0):,.2f}
Total ESI: Rs.{payroll_data.get('total_esi', 0):,.2f}
Total TDS: Rs.{payroll_data.get('total_tds', 0):,.2f}

Provide:
1. Summary observations
2. Compliance check (PF threshold, ESI eligibility, TDS rates)
3. Month-over-month comparison insights
4. Recommendations"""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="payroll_analysis"
        )

        return {
            "analysis": response.content,
            "provider": response.provider.value,
            "tokens_used": response.input_tokens + response.output_tokens
        }

    async def analyze_receivables(
        self,
        receivable_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze accounts receivable and provide collection insights."""
        data_summary = json.dumps(receivable_data[:10], indent=2)  # Limit for context

        prompt = f"""Analyze the following accounts receivable data:

{data_summary}

Provide:
1. Aging analysis summary
2. High-risk accounts identification
3. Collection priority recommendations
4. Cash flow impact assessment"""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="invoice_analysis"
        )

        return {
            "analysis": response.content,
            "provider": response.provider.value,
            "tokens_used": response.input_tokens + response.output_tokens
        }

    async def generate_report_summary(
        self,
        report_data: Dict[str, Any],
        report_type: str
    ) -> Dict[str, Any]:
        """Generate AI-powered report summary."""
        prompt = f"""Generate an executive summary for the following {report_type} report:

Data: {json.dumps(report_data, indent=2)}

Include:
1. Key highlights (3-5 points)
2. Notable trends
3. Areas of concern
4. Recommendations"""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="report_generation"
        )

        return {
            "summary": response.content,
            "provider": response.provider.value,
            "tokens_used": response.input_tokens + response.output_tokens
        }

    async def answer_hr_query(
        self,
        query: str,
        employee_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Answer HR-related query."""
        context = ""
        if employee_context:
            context = f"\nEmployee Context:\n- Leave Balance: {employee_context.get('leave_balance', {})}"

        prompt = f"""Query: {query}{context}

Provide a helpful and accurate response."""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            feature="hr_assistant"
        )

        return {
            "answer": response.content,
            "provider": response.provider.value,
            "tokens_used": response.input_tokens + response.output_tokens
        }


# Demo usage
if __name__ == "__main__":
    import asyncio

    async def demo():
        service = AIService(
            api_keys={AIProvider.CLAUDE: "demo-key"},
            default_provider=AIProvider.CLAUDE
        )

        response = await service.chat(
            messages=[{"role": "user", "content": "What are the TDS slabs for FY 2024-25?"}]
        )

        print(f"Response: {response.content}")
        print(f"Provider: {response.provider.value}")
        print(f"Tokens: {response.input_tokens + response.output_tokens}")

    asyncio.run(demo())
