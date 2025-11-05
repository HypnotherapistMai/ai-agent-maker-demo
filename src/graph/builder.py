"""LangGraph builder: constructs dynamic execution graphs."""
from langgraph.graph import StateGraph, START, END  # ⭐ Correct imports
from langgraph.checkpoint.memory import MemorySaver
from typing import Literal, Any, Dict
import time
import uuid
from datetime import datetime

from src.graph.state import AgentState
from src.agents import ManagerAgent, ResearcherAgent, WriterAgent, QAAgent
from src.core.schemas import Workflow, ExecutionRecord
from src.core.memory import MemoryManager
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


def manager_node(state: AgentState) -> Dict[str, Any]:
    """
    Manager decision node.

    Args:
        state: Current state

    Returns:
        Partial state update with manager decisions
    """
    logger.info("Executing manager node")
    agent = ManagerAgent()

    try:
        result = agent.process(state)

        # Modify agent_outputs in-place to avoid INVALID_CONCURRENT_GRAPH_UPDATE
        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["manager"] = result

        return {
            "current_step": state.get("current_step", 0) + 1
        }

    except Exception as e:
        logger.error(f"Manager node error: {e}")
        return {
            "errors": [{"node": "manager", "error": str(e)}]
        }


def researcher_node(state: AgentState) -> Dict[str, Any]:
    """
    Researcher node.

    Args:
        state: Current state

    Returns:
        Partial state update with research findings
    """
    logger.info("Executing researcher node")
    agent = ResearcherAgent()

    try:
        result = agent.process(state)

        # Modify agent_outputs in-place to avoid INVALID_CONCURRENT_GRAPH_UPDATE
        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["researcher"] = result

        return {
            "researcher_findings": result.get("findings")
        }

    except Exception as e:
        logger.error(f"Researcher node error: {e}")
        return {
            "errors": [{"node": "researcher", "error": str(e)}],
            "researcher_findings": "Error in research, using fallback data"
        }


def writer_node(state: AgentState) -> Dict[str, Any]:
    """
    Writer node.

    Args:
        state: Current state

    Returns:
        Partial state update with written draft
    """
    logger.info(f"Executing writer node (retry: {state.get('retry_count', 0)})")
    agent = WriterAgent()

    try:
        # Get manager's adjusted prompts if available
        manager_decision = state.get("agent_outputs", {}).get("manager", {}).get("manager_decision", {})
        adjusted_prompt = manager_decision.get("adjusted_prompts", {}).get("writer")

        result = agent.process(state, custom_prompt=adjusted_prompt)

        # Modify agent_outputs in-place to avoid INVALID_CONCURRENT_GRAPH_UPDATE
        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["writer"] = result

        return {
            "writer_draft": result.get("draft")
        }

    except Exception as e:
        logger.error(f"Writer node error: {e}")
        return {
            "errors": [{"node": "writer", "error": str(e)}],
            "writer_draft": "Error in writing, using fallback content"
        }


def qa_node(state: AgentState) -> Dict[str, Any]:
    """
    QA validation node.

    Args:
        state: Current state

    Returns:
        Partial state update with validation results
    """
    logger.info("Executing QA node")
    agent = QAAgent()

    try:
        result = agent.process(state)

        # Modify agent_outputs in-place to avoid INVALID_CONCURRENT_GRAPH_UPDATE
        if "agent_outputs" not in state:
            state["agent_outputs"] = {}
        state["agent_outputs"]["qa"] = result

        passed = result.get("passed", False)
        updates = {
            "validation_passed": passed,
            "validation_feedback": result.get("feedback")
        }

        if passed:
            updates["final_output"] = state.get("writer_draft")
            updates["status"] = "completed"
            logger.info("✅ Validation passed")
        else:
            retry_count = state.get("retry_count", 0) + 1
            updates["retry_count"] = retry_count
            updates["status"] = "retrying" if retry_count < 2 else "failed"
            logger.warning(f"❌ Validation failed (retry {retry_count}/2)")

        return updates

    except Exception as e:
        logger.error(f"QA node error: {e}")
        return {
            "errors": [{"node": "qa", "error": str(e)}],
            "validation_passed": False,
            "validation_feedback": f"QA error: {e}",
            "status": "failed"
        }


def qa_decision(state: AgentState) -> Literal["done", "rewrite"]:
    """
    Decide whether to finish or rewrite based on QA results.

    Args:
        state: Current state

    Returns:
        "done" to finish, "rewrite" to retry
    """
    if state.get("validation_passed", False):
        logger.info("QA decision: done (validation passed)")
        return "done"

    retry_count = state.get("retry_count", 0)
    if retry_count >= 2:
        logger.info(f"QA decision: done (max retries reached: {retry_count})")
        return "done"

    logger.info(f"QA decision: rewrite (retry {retry_count}/2)")
    return "rewrite"


def build_graph(workflow: Workflow) -> Any:
    """
    Build dynamic LangGraph execution graph.

    Flow:
    START → Manager → Researcher → Manager → Writer → QA → {END | Writer (retry)}

    Args:
        workflow: Workflow definition

    Returns:
        Compiled LangGraph application
    """
    logger.info(f"Building graph for workflow: {workflow.name}")

    # Define state graph
    graph = StateGraph(AgentState)

    # Add nodes
    graph.add_node("manager", manager_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("writer", writer_node)
    graph.add_node("qa", qa_node)

    # Define edges
    graph.add_edge(START, "manager")  # ⭐ Use START
    graph.add_edge("manager", "researcher")
    graph.add_edge("researcher", "writer")  # Direct path, no second manager call

    # ⭐ Conditional edge: QA decides pass or retry
    graph.add_conditional_edges(
        "qa",
        qa_decision,
        {
            "done": END,      # ⭐ Use END
            "rewrite": "writer"  # Retry loop
        }
    )

    graph.add_edge("writer", "qa")

    # ⭐ Must compile
    checkpointer = MemorySaver()
    app = graph.compile(checkpointer=checkpointer)

    logger.info("Graph compiled successfully")

    # Generate Mermaid diagram
    try:
        mermaid_code = app.get_graph().draw_mermaid()
        import os
        os.makedirs("docs", exist_ok=True)
        with open("docs/graph.mmd", "w") as f:
            f.write(mermaid_code)
        logger.info("Mermaid diagram saved to docs/graph.mmd")
    except Exception as e:
        logger.warning(f"Could not generate Mermaid diagram: {e}")

    return app


def execute_workflow(
    workflow: Workflow,
    blueprint_raw: str = ""
) -> Dict[str, Any]:
    """
    Execute a workflow end-to-end.

    Args:
        workflow: Workflow to execute
        blueprint_raw: Raw blueprint string

    Returns:
        Execution result dictionary
    """
    logger.info(f"Starting workflow execution: {workflow.name}")

    # Build graph
    app = build_graph(workflow)

    # Initialize state
    initial_state = {
        "workflow": workflow,
        "blueprint_raw": blueprint_raw or workflow.name,
        "current_step": 0,
        "agent_outputs": {},
        "messages": [],
        "researcher_findings": None,
        "writer_draft": None,
        "validation_passed": False,
        "validation_feedback": None,
        "retry_count": 0,
        "execution_id": str(uuid.uuid4()),
        "start_time": time.time(),
        "errors": [],
        "final_output": None,
        "status": "running"
    }

    # Execute
    start_time = time.time()
    memory_manager = MemoryManager()

    try:
        # Run graph with increased recursion limit for retry loops
        config = {
            "configurable": {"thread_id": initial_state["execution_id"]},
            "recursion_limit": 50  # Allow for retries and complex workflows
        }
        result = app.invoke(initial_state, config=config)

        duration = time.time() - start_time
        success = result.get("status") == "completed"

        # Record execution
        record = ExecutionRecord(
            id=initial_state["execution_id"],
            workflow_name=workflow.name,
            blueprint=blueprint_raw,
            success=success,
            error_type=None if success else "validation_failed",
            error_message=None if success else result.get("validation_feedback"),
            retry_count=result.get("retry_count", 0),
            duration_seconds=duration,
            timestamp=datetime.now(),
            learned_adjustments=None
        )
        memory_manager.record_execution(record)

        logger.info(f"Workflow execution completed: {workflow.name} ({'SUCCESS' if success else 'FAILED'})")

        return {
            "success": success,
            "final_output": result.get("final_output"),
            "status": result.get("status"),
            "retry_count": result.get("retry_count", 0),
            "validation_passed": result.get("validation_passed", False),
            "validation_feedback": result.get("validation_feedback"),
            "duration_seconds": duration,
            "execution_id": initial_state["execution_id"],
            "agent_outputs": result.get("agent_outputs", {}),
            "errors": result.get("errors", [])
        }

    except Exception as e:
        duration = time.time() - start_time
        logger.error(f"Workflow execution error: {e}")

        # Record failure
        record = ExecutionRecord(
            id=initial_state["execution_id"],
            workflow_name=workflow.name,
            blueprint=blueprint_raw,
            success=False,
            error_type=type(e).__name__,
            error_message=str(e),
            retry_count=0,
            duration_seconds=duration,
            timestamp=datetime.now(),
            learned_adjustments=None
        )
        memory_manager.record_execution(record)

        return {
            "success": False,
            "final_output": None,
            "status": "error",
            "error": str(e),
            "duration_seconds": duration,
            "execution_id": initial_state["execution_id"]
        }
