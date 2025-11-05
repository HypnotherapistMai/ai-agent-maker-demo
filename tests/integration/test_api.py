"""Integration tests for FastAPI."""
import pytest
from fastapi.testclient import TestClient
import json

from api.main import app


client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()

    assert "status" in data
    assert data["status"] == "healthy"
    assert "version" in data
    assert "adk_available" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "healthy"


def test_run_workflow_due_diligence(mock_env):
    """Test running due diligence workflow via API."""
    blueprint = {
        "workflow_name": "customer_due_diligence",
        "input": {
            "company_name": "ACME Corp"
        }
    }

    response = client.post(
        "/run",
        json={
            "blueprint": json.dumps(blueprint),
            "scenario": "due_diligence"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "run_id" in data
    assert "status" in data
    assert "result" in data


def test_run_workflow_recruiting(mock_env):
    """Test running recruiting workflow via API."""
    blueprint = {
        "workflow_name": "jd_to_sourcing",
        "input": {
            "job_description": "Senior Python Developer needed"
        }
    }

    response = client.post(
        "/run",
        json={
            "blueprint": json.dumps(blueprint),
            "scenario": "recruiting"
        }
    )

    assert response.status_code == 200
    data = response.json()

    assert "run_id" in data
    assert data["status"] in ["completed", "failed"]


def test_run_workflow_invalid_blueprint():
    """Test API with invalid blueprint."""
    response = client.post(
        "/run",
        json={
            "blueprint": "{}",  # Missing workflow_name
            "scenario": "test"
        }
    )

    assert response.status_code == 400
    assert "Invalid blueprint" in response.json()["detail"]


def test_get_stats_new_workflow():
    """Test getting stats for workflow with no history."""
    response = client.get("/stats/new_workflow")

    assert response.status_code == 200
    data = response.json()

    assert data["workflow_name"] == "new_workflow"
    assert data["total_executions"] == 0


def test_get_learning_context():
    """Test getting learning context."""
    response = client.get("/learning/test_workflow")

    assert response.status_code == 200
    data = response.json()

    assert "workflow_name" in data
    assert "learning_context" in data


def test_clear_history():
    """Test clearing workflow history."""
    response = client.delete("/history/test_workflow")

    assert response.status_code == 200
    data = response.json()

    assert "message" in data


def test_api_cors_headers():
    """Test CORS headers are present."""
    response = client.options("/health")

    # CORS should allow all origins
    assert response.status_code == 200


def test_openapi_docs_available():
    """Test that OpenAPI docs are accessible."""
    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_run_workflow_end_to_end(mock_env):
    """Test complete workflow execution via API."""
    # 1. Submit workflow
    blueprint = {
        "workflow_name": "test_e2e",
        "input": {"test": "data"}
    }

    run_response = client.post(
        "/run",
        json={
            "blueprint": json.dumps(blueprint),
            "scenario": "custom"
        }
    )

    assert run_response.status_code == 200
    run_data = run_response.json()
    run_id = run_data["run_id"]

    assert run_id is not None

    # 2. Check stats
    stats_response = client.get("/stats/test_e2e")
    assert stats_response.status_code == 200

    # 3. Get learning context
    learning_response = client.get("/learning/test_e2e")
    assert learning_response.status_code == 200
