"""Unit tests for agent implementations."""
import pytest
from src.agents import ManagerAgent, ResearcherAgent, WriterAgent, QAAgent
from src.core.schemas import Workflow, Step, AgentRole


@pytest.fixture
def mock_workflow():
    """Create mock workflow for testing."""
    return Workflow(
        name="test_workflow",
        description="Test workflow",
        steps=[
            Step(
                name="test_step",
                agent_role=AgentRole.RESEARCHER,
                output_key="test_output",
                prompt_template="Test prompt"
            )
        ],
        input_data={"company_name": "ACME Corp"}
    )


@pytest.fixture
def mock_state(mock_workflow):
    """Create mock state for testing."""
    return {
        "workflow": mock_workflow,
        "current_step": 0,
        "agent_outputs": {},
        "messages": [],
        "retry_count": 0
    }


def test_manager_agent_initialization(mock_env):
    """Test Manager agent initialization."""
    agent = ManagerAgent()

    assert agent.role == "manager"
    assert agent.memory is not None
    assert agent.system_prompt is not None


def test_manager_process(mock_env, mock_state):
    """Test Manager agent processing."""
    agent = ManagerAgent()

    result = agent.process(mock_state)

    assert "manager_decision" in result
    assert isinstance(result["manager_decision"], dict)
    assert "learning_applied" in result


def test_researcher_agent_initialization(mock_env):
    """Test Researcher agent initialization."""
    agent = ResearcherAgent()

    assert agent.role == "researcher"
    assert agent.system_prompt is not None


def test_researcher_process(mock_env, mock_state):
    """Test Researcher agent processing."""
    agent = ResearcherAgent()

    result = agent.process(mock_state)

    assert "findings" in result
    assert isinstance(result["findings"], str)
    assert "status" in result


def test_writer_agent_initialization(mock_env):
    """Test Writer agent initialization."""
    agent = WriterAgent()

    assert agent.role == "writer"
    assert agent.system_prompt is not None


def test_writer_process(mock_env, mock_state):
    """Test Writer agent processing."""
    # Add research findings to state
    mock_state["researcher_findings"] = "Test research findings"

    agent = WriterAgent()
    result = agent.process(mock_state)

    assert "draft" in result
    assert isinstance(result["draft"], str)
    assert "status" in result


def test_writer_process_with_feedback(mock_env, mock_state):
    """Test Writer agent with validation feedback."""
    mock_state["researcher_findings"] = "Test findings"
    mock_state["validation_feedback"] = "Add more detail"
    mock_state["retry_count"] = 1

    agent = WriterAgent()
    result = agent.process(mock_state)

    assert "draft" in result
    assert result["retry_count"] == 1


def test_qa_agent_initialization(mock_env):
    """Test QA agent initialization."""
    agent = QAAgent()

    assert agent.role == "qa"
    assert agent.validator is not None


def test_qa_process_pass(mock_env, mock_state, sample_report):
    """Test QA agent with passing output."""
    mock_state["writer_draft"] = sample_report
    mock_state["agent_outputs"] = {
        "writer": {"draft": sample_report}
    }

    agent = QAAgent()
    result = agent.process(mock_state)

    assert "passed" in result
    assert isinstance(result["passed"], bool)
    assert "feedback" in result


def test_qa_process_fail(mock_env, mock_state):
    """Test QA agent with failing output."""
    mock_state["writer_draft"] = "Too short"
    mock_state["agent_outputs"] = {
        "writer": {"draft": "Too short"}
    }

    agent = QAAgent()
    result = agent.process(mock_state)

    assert "passed" in result
    assert "feedback" in result
    assert "failed_checks" in result


def test_agent_error_handling(mock_env):
    """Test agent error handling with invalid state."""
    agent = ManagerAgent()

    # Empty state should handle gracefully
    result = agent.process({})

    assert "error" in result or "manager_decision" in result
