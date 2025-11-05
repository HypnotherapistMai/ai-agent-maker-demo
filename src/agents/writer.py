"""Writer Agent: creates structured content and reports."""
from typing import Dict, Any, Optional
from src.agents.base import BaseAgent
from src.llm.mock_provider import MockLLMProvider
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class WriterAgent(BaseAgent):
    """
    Writer Agent: Creates structured content and reports.

    Responsibilities:
    1. Transform research into polished output
    2. Follow specific formatting requirements
    3. Ensure clarity and professionalism
    4. Adapt to different output formats
    """

    def __init__(self):
        """Initialize Writer agent."""
        super().__init__(
            role="writer",
            system_prompt="""You are a professional content writer creating high-quality deliverables.

Your responsibilities:
1. Transform research findings into polished, structured output
2. Follow specific formatting and style requirements
3. Ensure clarity, accuracy, and professionalism
4. Adapt tone and structure to the target audience
5. Include all required sections and elements

Be concise yet comprehensive. Use clear markdown formatting."""
        )
        self.mock_provider = MockLLMProvider()

    def process(
        self,
        state: Dict[str, Any],
        custom_prompt: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Create written output based on research findings.

        Args:
            state: Current workflow state
            custom_prompt: Optional custom prompt from manager

        Returns:
            Dictionary with written draft
        """
        workflow = state.get("workflow")
        if not workflow:
            logger.error("No workflow found in state")
            return {"error": "No workflow provided"}

        # Get research findings
        researcher_output = state.get("agent_outputs", {}).get("researcher", {})
        research_findings = researcher_output.get("findings", "")

        if not research_findings:
            research_findings = state.get("researcher_findings", "No research findings available")

        workflow_name = workflow.name
        input_data = workflow.input_data

        # Check for previous validation feedback
        validation_feedback = state.get("validation_feedback", "")
        retry_count = state.get("retry_count", 0)

        # Build writing prompt
        if "due_diligence" in workflow_name.lower():
            prompt = self._build_due_diligence_report_prompt(
                research_findings,
                input_data.get("company_name", "ACME Corp"),
                validation_feedback
            )
        elif "recruiting" in workflow_name.lower():
            prompt = self._build_recruiting_output_prompt(
                research_findings,
                input_data.get("job_description", ""),
                validation_feedback
            )
        else:
            prompt = self._build_generic_prompt(research_findings, validation_feedback)

        # Apply manager's adjusted prompts
        if custom_prompt:
            prompt += f"\n\nAdditional guidance from manager:\n{custom_prompt}"

        # Add retry context
        if retry_count > 0:
            prompt += f"\n\nNote: This is retry #{retry_count}. Previous feedback:\n{validation_feedback}"

        try:
            # Generate written output
            draft = self._generate_response(prompt, temperature=0.7)

            logger.info(f"Writing completed for {workflow_name} (retry: {retry_count})")

            return {
                "draft": draft,
                "status": "completed",
                "retry_count": retry_count
            }

        except Exception as e:
            logger.error(f"Writing error: {e}")
            # Use mock fallback
            if "due_diligence" in workflow_name.lower():
                draft = self.mock_provider.get_mock_report(input_data.get("company_name", "ACME Corp"))
            elif "recruiting" in workflow_name.lower():
                draft = self.mock_provider.get_mock_recruiting_output()
            else:
                draft = "Mock output: Professional analysis and recommendations based on research findings."

            return {
                "draft": draft,
                "status": "completed_with_mock",
                "error": str(e),
                "retry_count": retry_count
            }

    def _build_due_diligence_report_prompt(
        self,
        findings: str,
        company_name: str,
        feedback: str = ""
    ) -> str:
        """Build prompt for due diligence report."""
        prompt = f"""Create a professional due diligence report for: {company_name}

Based on these research findings:
{findings}

Requirements:
- Exactly 3 main sections: Financial Analysis, Legal Review, Market Position
- Each section should have 2-3 paragraphs
- Use clear markdown formatting with ## headers
- Include specific data points and metrics
- Professional tone suitable for executive review
- Total length: 300-500 words
"""

        if feedback:
            prompt += f"\n\nAddress this feedback from QA:\n{feedback}"

        return prompt

    def _build_recruiting_output_prompt(
        self,
        findings: str,
        job_description: str,
        feedback: str = ""
    ) -> str:
        """Build prompt for recruiting output."""
        prompt = f"""Create sourcing strategy and interview materials.

Job Description Analysis:
{findings}

Deliverables:
1. Boolean Search String
   - Use proper boolean operators (AND, OR, parentheses)
   - Include key skills, titles, and tools
   - Make it practical for LinkedIn/Indeed search

2. Interview Outline
   - 3-4 key interview sections
   - Specific question areas
   - Duration for each section

Use markdown formatting with clear headers."""

        if feedback:
            prompt += f"\n\nAddress this feedback from QA:\n{feedback}"

        return prompt

    def _build_generic_prompt(self, findings: str, feedback: str = "") -> str:
        """Build generic writing prompt."""
        prompt = f"""Create professional output based on these findings:

{findings}

Requirements:
- Clear structure with headers
- Markdown formatting
- Professional tone
- Actionable insights
- 200-400 words"""

        if feedback:
            prompt += f"\n\nAddress this feedback:\n{feedback}"

        return prompt
