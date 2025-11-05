"""Integration tests for LangGraph execution."""
import pytest
from src.core.blueprint_parser import BlueprintParser
from src.graph.builder import build_graph, execute_workflow
from src.core.schemas import Workflow


def test_build_graph(mock_env, due_diligence_blueprint):
    """Test graph building."""
    parser = BlueprintParser()
    workflow = parser.parse(str(due_diligence_blueprint), "due_diligence")

    graph = build_graph(workflow)

    assert graph is not None
    # Graph should be compiled
    assert hasattr(graph, "invoke")


def test_execute_workflow_due_diligence(mock_env, due_diligence_blueprint):
    """Test end-to-end due diligence workflow execution."""
    import json
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    assert isinstance(result, dict)
    assert "success" in result
    assert "execution_id" in result
    assert "status" in result
    assert "duration_seconds" in result


def test_execute_workflow_recruiting(mock_env, recruiting_blueprint):
    """Test end-to-end recruiting workflow execution."""
    import json
    parser = BlueprintParser()
    blueprint_str = json.dumps(recruiting_blueprint)

    workflow = parser.parse(blueprint_str, "recruiting")
    result = execute_workflow(workflow, blueprint_str)

    assert isinstance(result, dict)
    assert "success" in result
    assert "final_output" in result or "error" in result


def test_workflow_retry_logic(mock_env):
    """Test that retry logic works correctly."""
    from src.core.schemas import Step, AgentRole

    # Create workflow that will likely fail QA first time
    workflow = Workflow(
        name="test_retry",
        description="Test retry workflow",
        steps=[
            Step(
                name="write",
                agent_role=AgentRole.WRITER,
                output_key="draft",
                prompt_template="Write a very short output",
                validation_rules={}
            ),
            Step(
                name="qa",
                agent_role=AgentRole.QA,
                output_key="final",
                prompt_template="Validate",
                validation_rules={"min_length": 500}  # High requirement
            )
        ],
        input_data={"test": "data"}
    )

    result = execute_workflow(workflow, "test")

    # Should complete even if validation fails after retries
    assert "status" in result
    assert result["status"] in ["completed", "failed", "error"]


def test_workflow_state_tracking(mock_env, due_diligence_blueprint):
    """Test that workflow state is properly tracked."""
    import json
    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")
    result = execute_workflow(workflow, blueprint_str)

    # Should have agent outputs
    if result.get("success"):
        agent_outputs = result.get("agent_outputs", {})

        # Check that agents executed
        # Note: Exact agents depend on graph structure
        assert isinstance(agent_outputs, dict)


def test_workflow_error_handling(mock_env):
    """Test workflow execution with errors."""
    from src.core.schemas import Step, AgentRole

    # Create minimal workflow with at least one step
    workflow = Workflow(
        name="error_test",
        description="Test error handling",
        steps=[
            Step(
                name="test_step",
                agent_role=AgentRole.RESEARCHER,
                output_key="output",
                prompt_template="Test",
                validation_rules={}
            )
        ],
        input_data={}
    )

    # Should handle gracefully
    result = execute_workflow(workflow, "error_test")

    assert isinstance(result, dict)
    # Should complete or error, not crash
    assert "status" in result


def test_memory_persistence(mock_env, due_diligence_blueprint):
    """Test that execution is recorded in memory."""
    import json
    from src.core.memory import MemoryManager

    parser = BlueprintParser()
    blueprint_str = json.dumps(due_diligence_blueprint)

    workflow = parser.parse(blueprint_str, "due_diligence")

    # Execute workflow
    result = execute_workflow(workflow, blueprint_str)

    # Check memory
    memory = MemoryManager()
    stats = memory.get_execution_stats(workflow.name)

    # Should have recorded at least one execution
    assert stats["total_executions"] >= 1


def test_concurrent_workflows(mock_env):
    """Test that multiple workflows can be executed."""
    from src.core.schemas import Step, AgentRole

    workflows = []
    for i in range(3):
        workflow = Workflow(
            name=f"concurrent_test_{i}",
            description=f"Concurrent workflow {i}",
            steps=[
                Step(
                    name="test_step",
                    agent_role=AgentRole.RESEARCHER,
                    output_key="output",
                    prompt_template="Test",
                    validation_rules={}
                )
            ],
            input_data={"id": i}
        )
        workflows.append(workflow)

    results = []
    for workflow in workflows:
        result = execute_workflow(workflow, f"concurrent_{workflow.name}")
        results.append(result)

    # All should complete
    assert len(results) == 3
    for result in results:
        assert "execution_id" in result
