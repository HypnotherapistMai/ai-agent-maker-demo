"""API request and response models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class RunRequest(BaseModel):
    """Request model for workflow execution."""
    blueprint: str = Field(..., description="JSON string or natural language workflow description")
    scenario: Optional[str] = Field(None, description="Scenario hint: due_diligence, recruiting, etc.")

    class Config:
        schema_extra = {
            "example": {
                "blueprint": '{"workflow_name": "customer_due_diligence", "input": {"company_name": "ACME Corp"}}',
                "scenario": "due_diligence"
            }
        }


class RunResponse(BaseModel):
    """Response model for workflow execution."""
    run_id: str = Field(..., description="Unique execution ID")
    status: str = Field(..., description="Execution status: completed, failed, error")
    result: Optional[Dict[str, Any]] = Field(None, description="Execution results")
    error: Optional[str] = Field(None, description="Error message if failed")

    class Config:
        schema_extra = {
            "example": {
                "run_id": "550e8400-e29b-41d4-a716-446655440000",
                "status": "completed",
                "result": {
                    "final_output": "# Due Diligence Report...",
                    "validation_passed": True,
                    "execution_time": 12.5
                }
            }
        }


class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    adk_available: bool = Field(..., description="Whether Google ADK is available")


class StatsResponse(BaseModel):
    """Workflow statistics response."""
    workflow_name: str
    total_executions: int
    successful: int
    success_rate: float
    avg_duration: float
    avg_retries: float
