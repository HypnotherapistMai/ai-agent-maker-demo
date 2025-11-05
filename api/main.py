"""FastAPI REST API for agent maker system."""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from api.models import RunRequest, RunResponse, HealthResponse, StatsResponse
from api.dependencies import get_blueprint_parser, get_memory_manager
from src.core.blueprint_parser import BlueprintParser
from src.core.memory import MemoryManager
from src.graph.builder import execute_workflow
from adk_app.manager_tool import ADK_AVAILABLE
from src.utils.logging import setup_logger

logger = setup_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="AI Agent Maker API",
    description="Blueprint-to-Agent system API for dynamic multi-agent workflow execution",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthResponse)
async def root() -> HealthResponse:
    """
    Root endpoint with API status.

    Returns:
        Health response with API information
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        adk_available=ADK_AVAILABLE
    )


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        adk_available=ADK_AVAILABLE
    )


@app.post("/run", response_model=RunResponse)
async def run_workflow(
    request: RunRequest,
    parser: BlueprintParser = Depends(get_blueprint_parser)
) -> RunResponse:
    """
    Execute a workflow from blueprint.

    Args:
        request: RunRequest with blueprint and optional scenario
        parser: Blueprint parser dependency

    Returns:
        RunResponse with execution results

    Raises:
        HTTPException: If execution fails
    """
    logger.info(f"Received run request for scenario: {request.scenario}")

    try:
        # Parse blueprint
        workflow = parser.parse(request.blueprint, request.scenario)
        logger.info(f"Parsed workflow: {workflow.name}")

        # Execute workflow
        result = execute_workflow(workflow, request.blueprint)

        # Build response
        if result["success"]:
            return RunResponse(
                run_id=result["execution_id"],
                status=result["status"],
                result={
                    "final_output": result.get("final_output"),
                    "validation_passed": result.get("validation_passed"),
                    "retry_count": result.get("retry_count"),
                    "execution_time": result.get("duration_seconds"),
                    "agent_outputs": result.get("agent_outputs", {})
                }
            )
        else:
            return RunResponse(
                run_id=result["execution_id"],
                status=result["status"],
                result={
                    "validation_passed": False,
                    "validation_feedback": result.get("validation_feedback"),
                    "retry_count": result.get("retry_count"),
                    "execution_time": result.get("duration_seconds")
                },
                error=result.get("error", "Execution failed")
            )

    except ValueError as e:
        logger.error(f"Blueprint parsing error: {e}")
        raise HTTPException(status_code=400, detail=f"Invalid blueprint: {str(e)}")

    except Exception as e:
        logger.error(f"Execution error: {e}")
        raise HTTPException(status_code=500, detail=f"Execution error: {str(e)}")


@app.get("/stats/{workflow_name}", response_model=StatsResponse)
async def get_stats(
    workflow_name: str,
    memory: MemoryManager = Depends(get_memory_manager)
) -> StatsResponse:
    """
    Get execution statistics for a workflow.

    Args:
        workflow_name: Name of the workflow
        memory: Memory manager dependency

    Returns:
        Workflow statistics
    """
    logger.info(f"Fetching stats for workflow: {workflow_name}")

    try:
        stats = memory.get_execution_stats(workflow_name)

        return StatsResponse(
            workflow_name=workflow_name,
            total_executions=stats["total_executions"],
            successful=stats["successful"],
            success_rate=stats["success_rate"],
            avg_duration=stats["avg_duration"],
            avg_retries=stats["avg_retries"]
        )

    except Exception as e:
        logger.error(f"Stats retrieval error: {e}")
        raise HTTPException(status_code=500, detail=f"Stats error: {str(e)}")


@app.get("/learning/{workflow_name}")
async def get_learning_context(
    workflow_name: str,
    memory: MemoryManager = Depends(get_memory_manager)
) -> Dict[str, Any]:
    """
    Get meta-learning context for a workflow.

    Args:
        workflow_name: Name of the workflow
        memory: Memory manager dependency

    Returns:
        Learning context
    """
    logger.info(f"Fetching learning context for: {workflow_name}")

    try:
        context = memory.get_learning_context(workflow_name)

        return {
            "workflow_name": workflow_name,
            "learning_context": context
        }

    except Exception as e:
        logger.error(f"Learning context error: {e}")
        raise HTTPException(status_code=500, detail=f"Learning context error: {str(e)}")


@app.delete("/history/{workflow_name}")
async def clear_history(
    workflow_name: str,
    memory: MemoryManager = Depends(get_memory_manager)
) -> Dict[str, str]:
    """
    Clear execution history for a workflow.

    Args:
        workflow_name: Name of the workflow
        memory: Memory manager dependency

    Returns:
        Confirmation message
    """
    logger.info(f"Clearing history for: {workflow_name}")

    try:
        memory.clear_history(workflow_name)

        return {
            "message": f"History cleared for workflow: {workflow_name}"
        }

    except Exception as e:
        logger.error(f"History clearing error: {e}")
        raise HTTPException(status_code=500, detail=f"History clearing error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
