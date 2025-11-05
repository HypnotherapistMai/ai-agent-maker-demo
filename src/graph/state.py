"""LangGraph state definition."""
from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    """
    State schema for LangGraph workflow execution.

    This state is passed between all agent nodes and tracks
    the entire workflow execution.
    """
    # Input
    workflow: Any  # Workflow object from schemas
    blueprint_raw: str

    # Execution tracking
    current_step: int
    agent_outputs: Dict[str, Any]

    # Agent communication
    messages: Annotated[List[BaseMessage], operator.add]
    researcher_findings: Optional[str]
    writer_draft: Optional[str]

    # Quality control
    validation_passed: bool
    validation_feedback: Optional[str]
    retry_count: int

    # Meta-learning
    execution_id: str
    start_time: float
    errors: Annotated[List[Dict[str, Any]], operator.add]

    # Final output
    final_output: Optional[str]
    status: str
