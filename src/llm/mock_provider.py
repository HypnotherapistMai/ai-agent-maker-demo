"""Mock LLM provider for testing without API calls."""
from typing import Dict, Any


class MockLLMProvider:
    """Provides deterministic mock responses for testing."""

    @staticmethod
    def get_mock_research(company: str = "ACME Corp") -> str:
        """Mock research findings."""
        return f"""# Research Findings for {company}

## Financial Analysis
- Revenue: $50M (20% YoY growth)
- Profit Margin: 15%
- Cash Flow: Positive

## Legal Status
- No pending litigation
- Regulatory compliance: Good standing
- IP portfolio: 12 patents

## Market Position
- Market share: 8%
- Main competitors: 3 major players
- Growth potential: High
"""

    @staticmethod
    def get_mock_report(company: str = "ACME Corp") -> str:
        """Mock due diligence report."""
        return f"""# Due Diligence Report: {company}

## 1. Financial Analysis
Strong financial performance with consistent revenue growth. Cash flow positive with healthy margins.

## 2. Legal Review
No major legal concerns identified. Regulatory compliance is maintained across all jurisdictions.

## 3. Market Position
Competitive positioning is favorable with significant growth opportunities in emerging markets.
"""

    @staticmethod
    def get_mock_validation() -> Dict[str, Any]:
        """Mock validation result."""
        return {
            "passed": True,
            "feedback": "Report meets all quality criteria. All required sections present with sufficient detail.",
            "failed_checks": []
        }

    @staticmethod
    def get_mock_recruiting_output() -> str:
        """Mock recruiting output."""
        return """# Sourcing Strategy

## Boolean Search
(Python OR "machine learning" OR AI) AND ("senior engineer" OR "tech lead") AND (AWS OR Azure OR GCP)

## Interview Outline
1. Technical Assessment (60 min)
   - System design
   - Coding challenge
   - Architecture discussion

2. Behavioral Interview (30 min)
   - Leadership examples
   - Team collaboration
   - Problem-solving approach
"""
