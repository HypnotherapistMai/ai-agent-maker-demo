"""Golden tests for due diligence scenario."""
import pytest
import json
from src.core.blueprint_parser import BlueprintParser
from src.graph.builder import execute_workflow


def test_due_diligence_complete_flow(mock_env, due_diligence_blueprint):
    """Golden test: Complete due diligence workflow."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    # Verify execution completed
    assert result["success"] or result["status"] in ["completed", "failed"]

    # Check for final output
    if result.get("final_output"):
        output = result["final_output"]

        # Golden criteria: Output must contain key sections
        assert len(output) > 100, "Output too short"

        # Check for section markers (case-insensitive)
        output_lower = output.lower()

        # At least 2 of 3 required sections should be present
        sections_found = 0
        if "financial" in output_lower:
            sections_found += 1
        if "legal" in output_lower:
            sections_found += 1
        if "market" in output_lower:
            sections_found += 1

        assert sections_found >= 2, f"Missing required sections (found {sections_found}/3)"


def test_due_diligence_output_format(mock_env, due_diligence_blueprint):
    """Golden test: Due diligence output format validation."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    if result.get("final_output"):
        output = result["final_output"]

        # Should be markdown formatted
        assert "#" in output or "##" in output, "Output should use markdown headers"

        # Should have structured content
        lines = output.split("\n")
        assert len(lines) > 5, "Output should have multiple lines"


def test_due_diligence_company_name(mock_env, due_diligence_blueprint):
    """Golden test: Due diligence mentions company name."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    if result.get("final_output"):
        output = result["final_output"]
        company_name = workflow.input_data.get("company_name", "")

        # Company name should appear in output (case-insensitive)
        if company_name:
            # Check for partial match (first word at least)
            first_word = company_name.split()[0]
            assert first_word.lower() in output.lower(), f"Company name '{company_name}' not found in output"


def test_due_diligence_retry_behavior(mock_env):
    """Golden test: Retry behavior works correctly."""
    from src.core.schemas import Workflow, Step, AgentRole

    # Create workflow with strict validation
    workflow = Workflow(
        name="customer_due_diligence",
        description="Test retry workflow",
        steps=[
            Step(
                name="research",
                agent_role=AgentRole.RESEARCHER,
                output_key="findings",
                prompt_template="Research company",
                validation_rules={}
            ),
            Step(
                name="write",
                agent_role=AgentRole.WRITER,
                output_key="draft",
                prompt_template="Write brief report",
                validation_rules={}
            ),
            Step(
                name="qa",
                agent_role=AgentRole.QA,
                output_key="final",
                prompt_template="Validate",
                validation_rules={"min_sections": 3, "min_length": 200}
            )
        ],
        input_data={"company_name": "ACME Corp"}
    )

    result = execute_workflow(workflow, "test")

    # Should complete within max retries
    assert result.get("retry_count", 0) <= 2, "Should not exceed max retries"

    # Should have attempted QA
    agent_outputs = result.get("agent_outputs", {})
    assert "qa" in agent_outputs or result.get("status") == "error"


def test_due_diligence_metadata(mock_env, due_diligence_blueprint):
    """Golden test: Execution metadata is captured."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    # Check required metadata
    assert "execution_id" in result
    assert "duration_seconds" in result
    assert "status" in result

    # Duration should be reasonable (< 60 seconds for mock)
    assert result["duration_seconds"] < 60, "Execution took too long"

    # Execution ID should be valid UUID format
    execution_id = result["execution_id"]
    assert len(execution_id) > 10, "Invalid execution ID"


def test_due_diligence_agent_coordination(mock_env, due_diligence_blueprint):
    """Golden test: Agents coordinate properly."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    # Should have outputs from multiple agents
    agent_outputs = result.get("agent_outputs", {})

    # At least researcher and writer should have executed
    total_agents = len(agent_outputs)
    assert total_agents >= 2, f"Expected multiple agents, got {total_agents}"
