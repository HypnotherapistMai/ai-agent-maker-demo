"""Unit tests for blueprint parser."""
import pytest
import json
from src.core.blueprint_parser import BlueprintParser
from src.core.schemas import Workflow


def test_parse_json_blueprint(mock_env, due_diligence_blueprint):
    """Test parsing valid JSON blueprint."""
    parser = BlueprintParser()

    blueprint_str = json.dumps(due_diligence_blueprint)
    workflow = parser.parse(blueprint_str, "due_diligence")

    assert isinstance(workflow, Workflow)
    assert workflow.name == "customer_due_diligence"
    assert len(workflow.steps) == 3
    assert workflow.input_data["company_name"] == "TechStart Inc"


def test_parse_minimal_blueprint(mock_env):
    """Test parsing minimal blueprint with defaults."""
    parser = BlueprintParser()

    minimal = {"workflow_name": "test_workflow"}
    blueprint_str = json.dumps(minimal)

    workflow = parser.parse(blueprint_str)

    assert workflow.name == "test_workflow"
    assert len(workflow.steps) >= 1  # Should generate default steps


def test_parse_invalid_json(mock_env):
    """Test handling of invalid JSON."""
    parser = BlueprintParser()

    # Invalid JSON should trigger natural language parsing
    result = parser.parse("Invalid JSON {", "due_diligence")

    # Should still return a Workflow object (via NL parsing)
    assert isinstance(result, Workflow)


def test_parse_missing_workflow_name(mock_env):
    """Test error handling for missing workflow_name."""
    parser = BlueprintParser()

    with pytest.raises(ValueError, match="workflow_name"):
        parser.parse('{"description": "test"}')


def test_generate_due_diligence_steps(mock_env):
    """Test default step generation for due diligence."""
    parser = BlueprintParser()

    steps = parser._generate_default_steps("customer_due_diligence")

    assert len(steps) >= 3
    assert any("research" in step["name"] for step in steps)
    assert any("writer" == step["agent_role"] for step in steps)
    assert any("qa" == step["agent_role"] for step in steps)


def test_generate_recruiting_steps(mock_env):
    """Test default step generation for recruiting."""
    parser = BlueprintParser()

    steps = parser._generate_default_steps("jd_to_sourcing")

    assert len(steps) >= 3
    assert any("jd" in step["name"].lower() or "analyze" in step["name"].lower() for step in steps)


def test_parse_with_scenario_hint(mock_env):
    """Test that scenario hint influences parsing."""
    parser = BlueprintParser()

    blueprint = {"workflow_name": "test_workflow"}
    workflow = parser.parse(json.dumps(blueprint), "due_diligence")

    # Should use due diligence defaults
    assert workflow.name == "test_workflow"
    assert len(workflow.steps) >= 3
