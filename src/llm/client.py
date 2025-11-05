"""LLM client wrapper for OpenAI."""
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.logging import setup_logger

load_dotenv()
logger = setup_logger(__name__)


class LLMClient:
    """Wrapper for OpenAI API calls."""

    def __init__(self, model: str = "gpt-4o-mini", mock: bool = False):
        """
        Initialize LLM client.

        Args:
            model: OpenAI model name
            mock: Whether to use mock responses
        """
        self.model = model
        self.mock = mock or os.getenv("MOCK", "0") == "1"

        if not self.mock:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OPENAI_API_KEY found, falling back to mock mode")
                self.mock = True
            else:
                self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.info("LLM client running in MOCK mode")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            json_mode: Whether to enforce JSON output
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Generated text
        """
        if self.mock:
            return self._mock_response(prompt, json_mode)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            logger.warning("Falling back to mock response")
            return self._mock_response(prompt, json_mode)

    def _mock_response(self, prompt: str, json_mode: bool) -> str:
        """Generate mock response for testing."""
        if json_mode:
            if "workflow" in prompt.lower() or "blueprint" in prompt.lower():
                return json.dumps({
                    "workflow_name": "mock_workflow",
                    "description": "Mock workflow for testing",
                    "input": {"company_name": "ACME Corp"},
                    "expected_output": {"format": "report"}
                })
            elif "decision" in prompt.lower() or "next_agent" in prompt.lower():
                return json.dumps({
                    "next_agent": "researcher",
                    "adjusted_prompts": {},
                    "notes": "Mock manager decision"
                })
            elif "quality" in prompt.lower() or "validate" in prompt.lower():
                # QA agent expects specific JSON structure
                return json.dumps({
                    "passed": True,
                    "feedback": "Output meets all quality criteria. All required sections present with sufficient detail.",
                    "issues": [],
                    "strengths": ["Clear structure", "Comprehensive coverage", "Professional tone"]
                })
            else:
                return json.dumps({"status": "mock", "result": "Mock JSON response"})
        else:
            # Extract company name from prompt if present
            company_name = "ACME Corp"
            # Look for company name patterns in the prompt
            import re

            # Pattern 1: "company_name: TechStart Inc" or similar
            company_match = re.search(r'company[_\s]*name[:\s]+([A-Za-z0-9\s&,\.]+?)(?:\n|$|,)', prompt, re.IGNORECASE)
            if company_match:
                company_name = company_match.group(1).strip()
            else:
                # Pattern 2: "for: CompanyName" or "for CompanyName"
                for_match = re.search(r'(?:for|about)[:\s]+([A-Z][A-Za-z0-9\s&,\.]+?)(?:\n|$|\.)', prompt)
                if for_match:
                    potential_name = for_match.group(1).strip()
                    # Validate it looks like a company name (starts with capital)
                    if potential_name and potential_name[0].isupper():
                        company_name = potential_name

            if "research" in prompt.lower():
                return f"""# Research Findings for {company_name}

## Financial Analysis
- Annual Revenue: $50M with 20% year-over-year growth
- Profit Margin: 15% (industry average: 12%)
- Cash Flow: Positive with $8M in reserves
- Debt-to-Equity Ratio: 0.3 (healthy leverage)

## Legal Status
- No pending litigation or regulatory investigations
- Regulatory compliance: Good standing across all jurisdictions
- Intellectual Property: 12 patents, 8 pending applications
- Corporate structure: Delaware C-Corp with clean cap table

## Market Position
- Market share: 8% in target segment
- Main competitors: 3 major players with 40% combined share
- Growth potential: High due to emerging market expansion
- Customer retention rate: 92% (excellent)"""

            elif "write" in prompt.lower() or "report" in prompt.lower():
                # Check if this is due diligence or recruiting
                if "due diligence" in prompt.lower() or "diligence" in prompt.lower():
                    return f"""# Due Diligence Report: {company_name}

## Financial Analysis

The company demonstrates strong financial performance with consistent revenue growth of 20% year-over-year, reaching $50M in annual revenue. The profit margin of 15% exceeds the industry average of 12%, indicating efficient operations and competitive positioning. Cash flow remains positive with $8M in reserves, providing adequate runway for operations and strategic initiatives. The debt-to-equity ratio of 0.3 reflects conservative financial management with healthy leverage levels.

## Legal Review

Our legal due diligence revealed no material concerns. There are no pending litigation matters or regulatory investigations that could impact the transaction. The company maintains regulatory compliance across all operating jurisdictions. The intellectual property portfolio includes 12 granted patents and 8 pending applications, providing competitive protection. The corporate structure is clean with a Delaware C-Corp entity and well-documented cap table.

## Market Position

{company_name} holds an 8% market share in its target segment, competing against three major players who collectively control 40% of the market. The company's customer retention rate of 92% demonstrates strong product-market fit and customer satisfaction. Growth potential is substantial, particularly in emerging markets where the company has established preliminary partnerships. The competitive positioning is favorable for continued expansion and market share gains."""

                elif "recruit" in prompt.lower() or "sourcing" in prompt.lower() or "boolean" in prompt.lower():
                    return """# Sourcing Strategy and Interview Materials

## Boolean Search String

```
(("Senior Software Engineer" OR "Senior Engineer" OR "Tech Lead") AND
(Python AND ("machine learning" OR ML OR "artificial intelligence" OR AI)) AND
(AWS OR "Amazon Web Services" OR GCP OR "Google Cloud" OR Azure) AND
("5+ years" OR "5 years" OR "senior level"))
```

**Alternative searches:**
- LinkedIn: `(Python AND ML AND AWS) AND ("Senior Software Engineer")`
- Indeed: `Senior Software Engineer Python Machine Learning Cloud`

## Interview Outline

### Technical Assessment (60 minutes)
**System Design (25 min)**
- Design a scalable ML inference pipeline
- Discuss trade-offs between latency and accuracy
- Architecture for real-time feature serving

**Coding Challenge (25 min)**
- Python: Implement ML data pipeline with error handling
- Focus on clean code, edge cases, and testing approach

**ML Knowledge (10 min)**
- Experience with TensorFlow/PyTorch
- Model deployment and monitoring strategies
- Handling model drift and retraining

### Behavioral Interview (30 minutes)
**Leadership & Mentorship**
- Describe experience mentoring junior engineers
- Example of technical decision you led and its outcome

**Team Collaboration**
- How do you handle technical disagreements?
- Experience working with cross-functional teams

**Problem-Solving**
- Describe a complex technical challenge you solved
- How do you approach debugging production issues?

### Final Assessment Criteria
- Technical depth in ML and cloud infrastructure
- Communication skills and ability to explain complex concepts
- Cultural fit and alignment with team values
- Leadership potential and mentorship capability"""
                else:
                    return """# Professional Analysis Report

## Executive Summary
This analysis provides comprehensive insights based on thorough research and evaluation of key factors affecting the subject matter.

## Key Findings
**Primary Observations:**
- Strong fundamentals with positive indicators across multiple metrics
- Strategic positioning demonstrates competitive advantages
- Risk factors are manageable with appropriate mitigation strategies

**Supporting Evidence:**
- Quantitative analysis shows favorable trends
- Qualitative assessment reveals strong organizational capabilities
- External factors support continued growth trajectory

## Recommendations
Based on our analysis, we recommend proceeding with appropriate due diligence and risk management protocols. The opportunity demonstrates significant potential with acceptable risk parameters."""

            elif "validate" in prompt.lower() or "quality" in prompt.lower():
                return "Validation passed. All required sections present."
            else:
                return "Mock LLM response for testing purposes."


def get_llm_client(model: str = "gpt-4o-mini", mock: bool = False) -> LLMClient:
    """
    Factory function to get LLM client.

    Args:
        model: Model name
        mock: Whether to use mock mode

    Returns:
        LLMClient instance
    """
    return LLMClient(model=model, mock=mock)
