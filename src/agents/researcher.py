"""Researcher Agent: gathers information and conducts analysis."""
from typing import Dict, Any
from src.agents.base import BaseAgent
from src.llm.mock_provider import MockLLMProvider
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class ResearcherAgent(BaseAgent):
    """
    Researcher Agent: Gathers data and conducts analysis.

    Responsibilities:
    1. Research companies, markets, or candidates
    2. Gather relevant data (mocked for demo)
    3. Provide structured findings
    4. Support various research scenarios
    """

    def __init__(self):
        """Initialize Researcher agent."""
        super().__init__(
            role="researcher",
            system_prompt="""You are a research specialist conducting thorough analysis.

Your responsibilities:
1. Gather relevant information based on the request
2. Analyze data from multiple perspectives
3. Provide structured, factual findings
4. Identify key insights and patterns
5. Flag any data gaps or concerns

Be thorough, objective, and detail-oriented. Organize findings clearly."""
        )
        self.mock_provider = MockLLMProvider()

    def process(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Conduct research based on workflow requirements.

        Args:
            state: Current workflow state

        Returns:
            Dictionary with research findings
        """
        workflow = state.get("workflow")
        if not workflow:
            logger.error("No workflow found in state")
            return {"error": "No workflow provided"}

        input_data = workflow.input_data
        workflow_name = workflow.name

        # Extract research target
        company_name = input_data.get("company_name", "ACME Corp")
        job_description = input_data.get("job_description", "")

        # Build research prompt
        if "due_diligence" in workflow_name.lower():
            prompt = self._build_due_diligence_prompt(company_name)
        elif "recruiting" in workflow_name.lower():
            prompt = self._build_recruiting_prompt(job_description)
        else:
            prompt = self._build_generic_prompt(input_data)

        # Get manager's adjusted prompts if available
        manager_decision = state.get("agent_outputs", {}).get("manager", {}).get("manager_decision", {})
        adjusted_prompt = manager_decision.get("adjusted_prompts", {}).get("researcher", "")

        if adjusted_prompt:
            prompt += f"\n\nAdditional guidance from manager:\n{adjusted_prompt}"

        try:
            # Generate research findings
            findings = self._generate_response(prompt, temperature=0.5)

            logger.info(f"Research completed for {workflow_name}")

            return {
                "findings": findings,
                "research_target": company_name or job_description[:50],
                "status": "completed"
            }

        except Exception as e:
            logger.error(f"Research error: {e}")
            # Use mock fallback
            if "due_diligence" in workflow_name.lower():
                findings = self.mock_provider.get_mock_research(company_name)
            else:
                findings = "Mock research findings: Analysis completed with standard methodology."

            return {
                "findings": findings,
                "research_target": company_name,
                "status": "completed_with_mock",
                "error": str(e)
            }

    def _build_due_diligence_prompt(self, company_name: str) -> str:
        """Build prompt for due diligence research."""
        return f"""Conduct comprehensive due diligence research on: {company_name}

Provide findings in these categories:

## 1. Financial Analysis
- Revenue trends and growth rate
- Profitability metrics
- Cash flow status
- Key financial ratios

## 2. Legal Status
- Regulatory compliance
- Pending litigation
- Intellectual property
- Contractual obligations

## 3. Market Position
- Market share and competitive position
- Industry trends
- Growth opportunities
- Competitive threats

Use markdown formatting and be specific with numbers where possible.
For this demo, provide realistic mock data."""

    def _build_recruiting_prompt(self, job_description: str) -> str:
        """Build prompt for recruiting research."""
        return f"""Analyze this job description for sourcing strategy:

{job_description}

Extract and analyze:
1. Required technical skills and experience
2. Key qualifications and certifications
3. Soft skills and cultural fit indicators
4. Competitive landscape for this role

Provide structured analysis that will inform:
- Boolean search string creation
- Interview question development
- Candidate sourcing strategy

Use markdown formatting."""

    def _build_generic_prompt(self, input_data: Dict[str, Any]) -> str:
        """Build generic research prompt."""
        return f"""Conduct research based on this input:

{input_data}

Provide thorough analysis covering:
1. Key facts and data points
2. Important patterns or trends
3. Relevant insights
4. Recommendations

Use markdown formatting and be specific."""
