"""Output validation utilities."""
from typing import Dict, Any, List
from src.core.schemas import ValidationResult
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class OutputValidator:
    """Validate agent outputs against rules."""

    @staticmethod
    def validate(
        output: str,
        rules: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate output against rules.

        Args:
            output: Output text to validate
            rules: Validation rules dictionary

        Returns:
            ValidationResult with pass/fail and feedback
        """
        failed_checks = []

        # Check minimum length
        if "min_length" in rules:
            min_len = rules["min_length"]
            if len(output) < min_len:
                failed_checks.append(f"Output too short (min {min_len} chars)")

        # Check minimum sections/points
        if "min_sections" in rules:
            min_sections = rules["min_sections"]
            section_count = OutputValidator._count_sections(output)
            if section_count < min_sections:
                failed_checks.append(f"Need at least {min_sections} sections, found {section_count}")

        # Check required keywords
        if "must_contain" in rules:
            keywords = rules["must_contain"]
            for keyword in keywords:
                if keyword.lower() not in output.lower():
                    failed_checks.append(f"Missing required keyword: {keyword}")

        # Check must include (for recruiting)
        if "must_include" in rules:
            required = rules["must_include"]
            for item in required:
                if item.lower() not in output.lower():
                    failed_checks.append(f"Missing required element: {item}")

        # Check format requirements
        if "format" in rules:
            fmt = rules["format"]
            if fmt == "markdown" and not OutputValidator._is_markdown(output):
                failed_checks.append("Output must be in markdown format")

        passed = len(failed_checks) == 0

        if passed:
            feedback = "Validation passed. Output meets all quality criteria."
        else:
            feedback = f"Validation failed. Issues:\n" + "\n".join(f"- {check}" for check in failed_checks)

        logger.info(f"Validation result: {'PASSED' if passed else 'FAILED'}")

        return ValidationResult(
            passed=passed,
            feedback=feedback,
            failed_checks=failed_checks
        )

    @staticmethod
    def _count_sections(text: str) -> int:
        """
        Count sections in text (markdown headers or numbered points).

        Args:
            text: Text to analyze

        Returns:
            Number of sections found
        """
        lines = text.split('\n')
        count = 0

        for line in lines:
            # Markdown headers
            if line.strip().startswith('#'):
                count += 1
            # Numbered points
            elif line.strip() and line.strip()[0].isdigit() and '.' in line[:5]:
                count += 1

        return count

    @staticmethod
    def _is_markdown(text: str) -> bool:
        """
        Check if text contains markdown formatting.

        Args:
            text: Text to check

        Returns:
            True if markdown detected
        """
        markdown_indicators = ['#', '##', '**', '*', '-', '```', '|']
        return any(indicator in text for indicator in markdown_indicators)

    @staticmethod
    def validate_workflow_output(
        output: str,
        workflow_name: str
    ) -> ValidationResult:
        """
        Validate output based on workflow type.

        Args:
            output: Output to validate
            workflow_name: Name of the workflow

        Returns:
            ValidationResult
        """
        if "due_diligence" in workflow_name.lower():
            return OutputValidator.validate(output, {
                "min_sections": 3,
                "min_length": 200,
                "format": "markdown"
            })

        if "recruiting" in workflow_name.lower() or "jd" in workflow_name.lower():
            return OutputValidator.validate(output, {
                "must_include": ["boolean", "interview"],
                "min_length": 100,
                "format": "markdown"
            })

        # Generic validation
        return OutputValidator.validate(output, {
            "min_length": 50
        })
