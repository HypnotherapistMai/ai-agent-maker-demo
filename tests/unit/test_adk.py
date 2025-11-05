"""Unit tests for ADK integration."""
import pytest
from adk_app.manager_tool import ADKManagerTool, ADK_AVAILABLE, _mock_research


def test_adk_availability():
    """Test ADK availability detection."""
    # Should be either True or False, not None
    assert isinstance(ADK_AVAILABLE, bool)


def test_mock_research_function():
    """Test mock research tool function."""
    result = _mock_research("TestCorp")

    assert isinstance(result, dict)
    assert result["status"] == "success"
    assert result["company"] == "TestCorp"
    assert "financial" in result
    assert "legal" in result
    assert "market" in result


def test_adk_manager_initialization():
    """Test ADK manager tool initialization."""
    manager = ADKManagerTool()

    assert hasattr(manager, "mode")
    assert manager.mode in ["adk", "mock"]


def test_run_equivalent_flow():
    """Test running equivalent ADK flow."""
    manager = ADKManagerTool()

    blueprint = {
        "workflow_name": "test_workflow",
        "input": {
            "company_name": "TestCorp"
        }
    }

    result = manager.run_equivalent_flow(blueprint)

    assert isinstance(result, dict)
    assert "status" in result
    assert "output" in result
    assert "mode" in result

    # Result should have completed status
    assert "completed" in result["status"]


def test_get_status():
    """Test getting ADK status."""
    manager = ADKManagerTool()

    status = manager.get_status()

    assert isinstance(status, dict)
    assert "adk_available" in status
    assert "mode" in status
    assert status["adk_available"] == ADK_AVAILABLE


def test_mock_mode_fallback():
    """Test that mock mode works as fallback."""
    manager = ADKManagerTool()

    # Even if ADK not available, should work in mock mode
    blueprint = {
        "workflow_name": "test",
        "input": {"company_name": "ACME"}
    }

    result = manager.run_equivalent_flow(blueprint)

    # Should complete successfully in mock mode
    assert result["status"] in ["completed", "completed_with_mock"]
    assert result["output"] is not None


@pytest.mark.skipif(not ADK_AVAILABLE, reason="ADK not installed")
def test_adk_real_integration():
    """Test real ADK integration if available."""
    manager = ADKManagerTool()

    assert manager.mode == "adk"
    assert manager.manager is not None


def test_error_handling():
    """Test error handling in ADK wrapper."""
    manager = ADKManagerTool()

    # Test with invalid blueprint
    invalid_blueprint = {}

    result = manager.run_equivalent_flow(invalid_blueprint)

    # Should handle gracefully
    assert isinstance(result, dict)
    assert "status" in result
