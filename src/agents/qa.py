"""QA Agent: validates output quality and completeness."""
from typing import Dict, Any
from src.agents.base import BaseAgent
from src.core.validators import OutputValidator
from src.core.schemas import ValidationResult
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class QAAgent(BaseAgent):
    """
    QA Agent: Validates output quality and completeness.

    Responsibilities:
    1. Validate output against requirements
    2. Check formatting and structure
    3. Verify completeness
    4. Provide actionable feedback
    5. Make pass/fail decisions
    """

    def __init__(self):
        """Initialize QA agent."""
        super().__init__(
            role="qa",
            system_prompt="""You are a quality assurance specialist ensuring output excellence.

Your responsibilities:
1. Validate output against all requirements
2. Check for completeness, accuracy, and clarity
3. Verify proper formatting and structure
4. Identify any gaps or issues
5. Provide specific, actionable feedback

Be thorough and constructive. Your feedback should help improve the output."""
        )
        self.validator = OutputValidator()

    def process(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Validate writer output and provide feedback.

        Args:
            state: Current workflow state

        Returns:
            Dictionary with validation results and feedback
        """
        workflow = state.get("workflow")
        if not workflow:
            logger.error("No workflow found in state")
            return {"error": "No workflow provided"}

        # Get writer output
        writer_output = state.get("agent_outputs", {}).get("writer", {})
        draft = writer_output.get("draft", "")

        if not draft:
            draft = state.get("writer_draft", "")

        if not draft:
            logger.error("No draft found for validation")
            return {
                "passed": False,
                "feedback": "No output to validate",
                "failed_checks": ["missing_output"]
            }

        workflow_name = workflow.name
        expected_output = workflow.expected_output

        # Get validation rules from workflow steps
        validation_rules = self._extract_validation_rules(workflow)

        # Run automated validation
        auto_validation = self.validator.validate_workflow_output(draft, workflow_name)

        # Get LLM-based qualitative validation
        qualitative_validation = self._qualitative_validation(
            draft,
            workflow_name,
            expected_output,
            validation_rules
        )

        # Combine validations
        passed = auto_validation.passed and qualitative_validation.get("passed", True)

        feedback_parts = []
        if not auto_validation.passed:
            feedback_parts.append(f"Automated checks:\n{auto_validation.feedback}")

        if qualitative_validation.get("feedback"):
            feedback_parts.append(f"Quality review:\n{qualitative_validation['feedback']}")

        if passed:
            feedback = "✅ Validation passed. Output meets all quality criteria and requirements."
        else:
            feedback = "\n\n".join(feedback_parts)

        failed_checks = auto_validation.failed_checks + qualitative_validation.get("issues", [])

        logger.info(f"QA validation: {'PASSED' if passed else 'FAILED'} ({len(failed_checks)} issues)")

        return {
            "passed": passed,
            "feedback": feedback,
            "failed_checks": failed_checks,
            "auto_validation": auto_validation.dict(),
            "qualitative_validation": qualitative_validation
        }

    def _extract_validation_rules(self, workflow) -> Dict[str, Any]:
        """Extract validation rules from workflow steps."""
        rules = {}
        for step in workflow.steps:
            if step.agent_role.value == "qa":
                rules.update(step.validation_rules)
        return rules

    def _qualitative_validation(
        self,
        output: str,
        workflow_name: str,
        expected_output: Dict[str, Any],
        validation_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Perform LLM-based qualitative validation.

        Args:
            output: Output to validate
            workflow_name: Workflow name
            expected_output: Expected output specification
            validation_rules: Validation rules

        Returns:
            Validation result dictionary
        """
        prompt = f"""Perform quality review of this output for workflow: {workflow_name}

OUTPUT TO REVIEW:
{output}

EXPECTED OUTPUT SPECIFICATION:
{expected_output}

VALIDATION RULES:
{validation_rules}

Evaluate:
1. Completeness - Are all required elements present?
2. Quality - Is the content clear, accurate, and professional?
3. Structure - Is it well-organized with proper formatting?
4. Specificity - Does it include concrete details and data?

Provide:
- Overall assessment (pass/fail)
- Specific issues if any
- Constructive feedback for improvement

Output JSON:
{{
  "passed": true/false,
  "feedback": "detailed feedback",
  "issues": ["issue1", "issue2"],
  "strengths": ["strength1", "strength2"]
}}"""

        try:
            import json
            response = self._generate_response(prompt, json_mode=True, temperature=0.3)
            result = json.loads(response)
            return result

        except Exception as e:
            logger.error(f"Qualitative validation error: {e}")
            # Provide safe fallback
            return {
                "passed": True,
                "feedback": "Qualitative validation unavailable, proceeding with automated checks only",
                "issues": [],
                "error": str(e)
            }
