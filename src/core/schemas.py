"""Core data schemas for the agent maker system."""
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class AgentRole(str, Enum):
    """Available agent roles in the system."""
    MANAGER = "manager"
    RESEARCHER = "researcher"
    WRITER = "writer"
    QA = "qa"


class Step(BaseModel):
    """Single workflow step definition."""
    name: str
    agent_role: AgentRole
    input_keys: List[str] = Field(default_factory=list)
    output_key: str
    prompt_template: str
    validation_rules: Dict[str, Any] = Field(default_factory=dict)


class Workflow(BaseModel):
    """Standardized workflow definition."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    steps: List[Step]
    input_data: Dict[str, Any] = Field(default_factory=dict)
    expected_output: Dict[str, Any] = Field(default_factory=dict)
    meta_context: Dict[str, Any] = Field(default_factory=dict)

    @validator("steps")
    def validate_steps(cls, v):
        """Ensure workflow has at least one step."""
        if not v:
            raise ValueError("Workflow must have at least one step")
        return v


class ExecutionRecord(BaseModel):
    """Execution history record for meta-learning."""
    id: str
    workflow_name: str
    blueprint: str
    success: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    duration_seconds: float
    timestamp: datetime
    learned_adjustments: Optional[str] = None


class ValidationResult(BaseModel):
    """Output validation result from QA agent."""
    passed: bool
    feedback: str
    failed_checks: List[str] = Field(default_factory=list)
