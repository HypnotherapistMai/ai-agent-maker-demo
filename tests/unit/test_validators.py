"""Unit tests for output validators."""
import pytest
from src.core.validators import OutputValidator
from src.core.schemas import ValidationResult


def test_validate_min_length_pass():
    """Test minimum length validation passes."""
    validator = OutputValidator()

    output = "This is a test output that is long enough to pass validation checks."
    rules = {"min_length": 20}

    result = validator.validate(output, rules)

    assert isinstance(result, ValidationResult)
    assert result.passed is True
    assert len(result.failed_checks) == 0


def test_validate_min_length_fail():
    """Test minimum length validation fails."""
    validator = OutputValidator()

    output = "Too short"
    rules = {"min_length": 100}

    result = validator.validate(output, rules)

    assert result.passed is False
    assert len(result.failed_checks) > 0
    assert any("too short" in check.lower() for check in result.failed_checks)


def test_validate_min_sections_pass():
    """Test minimum sections validation passes."""
    validator = OutputValidator()

    output = """# Section 1
Content here

## Section 2
More content

### Section 3
Final content"""

    rules = {"min_sections": 3}
    result = validator.validate(output, rules)

    assert result.passed is True


def test_validate_min_sections_fail():
    """Test minimum sections validation fails."""
    validator = OutputValidator()

    output = "# Only One Section\nSome content"
    rules = {"min_sections": 3}

    result = validator.validate(output, rules)

    assert result.passed is False
    assert len(result.failed_checks) > 0


def test_validate_must_contain_pass():
    """Test must_contain validation passes."""
    validator = OutputValidator()

    output = "This output contains financial data, legal information, and market analysis."
    rules = {"must_contain": ["financial", "legal", "market"]}

    result = validator.validate(output, rules)

    assert result.passed is True


def test_validate_must_contain_fail():
    """Test must_contain validation fails."""
    validator = OutputValidator()

    output = "This output only has financial data."
    rules = {"must_contain": ["financial", "legal", "market"]}

    result = validator.validate(output, rules)

    assert result.passed is False
    assert len(result.failed_checks) >= 2  # Missing legal and market


def test_validate_multiple_rules():
    """Test validation with multiple rules."""
    validator = OutputValidator()

    output = """# Financial Analysis
Revenue is strong at $50M with 20% growth.

## Legal Review
No major legal issues found.

### Market Position
Competitive positioning is favorable."""

    rules = {
        "min_length": 100,
        "min_sections": 3,
        "must_contain": ["financial", "legal", "market"]
    }

    result = validator.validate(output, rules)

    assert result.passed is True
    assert len(result.failed_checks) == 0


def test_validate_workflow_output_due_diligence():
    """Test workflow-specific validation for due diligence."""
    validator = OutputValidator()

    output = """# Due Diligence Report

## Financial Analysis
Strong performance

## Legal Review
Compliant

## Market Position
Growing"""

    result = validator.validate_workflow_output(output, "customer_due_diligence")

    assert isinstance(result, ValidationResult)
    # Should check for 3 sections and minimum length


def test_validate_workflow_output_recruiting():
    """Test workflow-specific validation for recruiting."""
    validator = OutputValidator()

    output = """# Sourcing Strategy

## Boolean Search
(Python AND \"senior engineer\")

## Interview Outline
1. Technical assessment
2. Behavioral questions"""

    result = validator.validate_workflow_output(output, "jd_to_sourcing")

    assert isinstance(result, ValidationResult)
    # Should check for boolean and interview content


def test_count_sections():
    """Test section counting helper."""
    validator = OutputValidator()

    text = """# Header 1
Content

## Header 2
More content

1. Numbered item
2. Another item

### Header 3
Final content"""

    count = validator._count_sections(text)

    assert count >= 3  # At least 3 markdown headers


def test_is_markdown():
    """Test markdown detection."""
    validator = OutputValidator()

    markdown_text = "# Header\n**bold** text with *italic*"
    plain_text = "Just plain text without any markdown"

    assert validator._is_markdown(markdown_text) is True
    assert validator._is_markdown(plain_text) is False
