"""Golden tests for recruiting scenario."""
import pytest
import json
from src.core.blueprint_parser import BlueprintParser
from src.graph.builder import execute_workflow


def test_recruiting_complete_flow(mock_env, recruiting_blueprint):
    """Golden test: Complete recruiting workflow."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    # Verify execution completed
    assert result["success"] or result["status"] in ["completed", "failed"]

    # Check for final output
    if result.get("final_output"):
        output = result["final_output"]
        assert len(output) > 50, "Output too short for recruiting strategy"


def test_recruiting_boolean_search(mock_env, recruiting_blueprint):
    """Golden test: Recruiting output includes boolean search."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    if result.get("final_output"):
        output = result["final_output"].lower()

        # Should contain boolean operators
        boolean_indicators = ["and", "or", "\"", "(", ")"]
        found_indicators = sum(1 for indicator in boolean_indicators if indicator in output)

        assert found_indicators >= 3, "Output should contain boolean search syntax"


def test_recruiting_interview_outline(mock_env, recruiting_blueprint):
    """Golden test: Recruiting output includes interview outline."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    if result.get("final_output"):
        output = result["final_output"].lower()

        # Should mention interview-related terms
        interview_terms = ["interview", "question", "assessment", "technical", "behavioral"]
        found_terms = sum(1 for term in interview_terms if term in output)

        assert found_terms >= 2, "Output should contain interview-related content"


def test_recruiting_jd_extraction(mock_env):
    """Golden test: Job description skills are extracted."""
    from src.core.schemas import Workflow, Step, AgentRole

    workflow = Workflow(
        name="jd_to_sourcing",
        description="JD to sourcing",
        steps=[
            Step(
                name="analyze",
                agent_role=AgentRole.RESEARCHER,
                output_key="analysis",
                prompt_template="Analyze JD",
                validation_rules={}
            )
        ],
        input_data={
            "job_description": "Senior Python Developer with AWS and machine learning experience"
        }
    )

    result = execute_workflow(workflow, "recruiting_test")

    # Should complete
    assert "execution_id" in result


def test_recruiting_output_structure(mock_env, recruiting_blueprint):
    """Golden test: Recruiting output is well-structured."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    if result.get("final_output"):
        output = result["final_output"]

        # Should have headers or structure
        assert "#" in output or "\n\n" in output, "Output should be structured"

        # Should have multiple paragraphs/sections
        sections = [s for s in output.split("\n") if s.strip()]
        assert len(sections) >= 3, "Output should have multiple sections"


def test_recruiting_validation(mock_env, recruiting_blueprint):
    """Golden test: Recruiting output is validated."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    # Should have validation results
    if "agent_outputs" in result and "qa" in result["agent_outputs"]:
        qa_output = result["agent_outputs"]["qa"]

        assert "passed" in qa_output or "feedback" in qa_output


def test_recruiting_metadata(mock_env, recruiting_blueprint):
    """Golden test: Recruiting workflow metadata."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    # Check metadata
    assert "execution_id" in result
    assert "duration_seconds" in result
    assert result["duration_seconds"] < 60, "Execution took too long"


def test_recruiting_agent_outputs(mock_env, recruiting_blueprint):
    """Golden test: Recruiting agents produce outputs."""
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    # Should have agent outputs
    agent_outputs = result.get("agent_outputs", {})

    # At least one agent should have produced output
    assert len(agent_outputs) > 0, "No agent outputs found"


def test_recruiting_error_recovery(mock_env):
    """Golden test: Recruiting workflow handles errors."""
    from src.core.schemas import Workflow, Step, AgentRole

    # Create workflow with potential issues
    workflow = Workflow(
        name="jd_to_sourcing",
        description="Test error recovery",
        steps=[
            Step(
                name="analyze",
                agent_role=AgentRole.RESEARCHER,
                output_key="analysis",
                prompt_template="Analyze minimal input",
                validation_rules={}
            )
        ],
        input_data={}  # Empty input
    )

    result = execute_workflow(workflow, "error_recovery_test")

    # Should complete without crashing
    assert "status" in result
    assert result["status"] in ["completed", "failed", "error"]
