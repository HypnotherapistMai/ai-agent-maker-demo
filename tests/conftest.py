"""Pytest configuration and fixtures."""
import pytest
import json
import os
from pathlib import Path


@pytest.fixture
def mock_env(monkeypatch):
    """Set environment to mock mode."""
    monkeypatch.setenv("MOCK", "1")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")


@pytest.fixture
def due_diligence_blueprint():
    """Load due diligence blueprint fixture."""
    fixture_path = Path("fixtures/consulting/due_diligence.json")
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def recruiting_blueprint():
    """Load recruiting blueprint fixture."""
    fixture_path = Path("fixtures/recruiting/jd_to_sourcing.json")
    with open(fixture_path) as f:
        return json.load(f)


@pytest.fixture
def sample_research_findings():
    """Sample research findings for testing."""
    return """# Research Findings

## Financial Analysis
- Revenue: $50M (20% YoY growth)
- Profit Margin: 15%
- Cash Flow: Positive

## Legal Status
- No pending litigation
- Regulatory compliance: Good
- IP portfolio: 12 patents

## Market Position
- Market share: 8%
- Competitors: 3 major players
- Growth potential: High"""


@pytest.fixture
def sample_report():
    """Sample report for testing."""
    return """# Due Diligence Report: ACME Corp

## 1. Financial Analysis
Strong financial performance with consistent growth.

## 2. Legal Review
No major legal concerns identified.

## 3. Market Position
Competitive positioning is favorable."""


@pytest.fixture
def temp_db(tmp_path):
    """Temporary database for testing."""
    db_path = tmp_path / "test_execution_history.db"
    return str(db_path)
