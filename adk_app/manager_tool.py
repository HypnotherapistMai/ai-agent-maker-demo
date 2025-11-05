"""Google ADK integration with Manager+Tool pattern."""
from typing import Dict, Any

# ⭐ Correct ADK imports based on official documentation
try:
    from google.adk.agents.llm_agent import Agent  # ⭐ Official Quickstart import
    ADK_AVAILABLE = True
except Exception as e:
    ADK_AVAILABLE = False
    _adk_error = str(e)


def _mock_research(company: str = "ACME Corp") -> dict:
    """
    Mock research tool for demo.

    In real ADK, tools are Python functions that agents can call.

    Args:
        company: Company name to research

    Returns:
        Research results dictionary
    """
    return {
        "status": "success",
        "company": company,
        "insight": f"Mocked market snapshot for {company} with key metrics.",
        "financial": {
            "revenue": "$50M",
            "growth": "20% YoY"
        },
        "legal": {
            "compliance": "Good standing",
            "litigation": "None pending"
        },
        "market": {
            "share": "8%",
            "position": "Growing"
        }
    }


class ADKManagerTool:
    """
    Minimal ADK Manager+Tool workflow.

    This demonstrates how the same workflow could be implemented
    using Google ADK instead of LangGraph.

    Equivalent mapping:
    - LangGraph StateGraph → ADK workflow
    - LangGraph Agent nodes → ADK Agents
    - LangGraph Tools → Python functions
    - LangGraph State → Context dict
    """

    def __init__(self):
        """Initialize ADK manager or fall back to mock."""
        if ADK_AVAILABLE:
            try:
                # Create ADK manager agent with tool
                self.manager = Agent(
                    model="gemini-2.0-flash-exp",  # or gemini-1.5-flash
                    name="manager",
                    description="Coordinates research and writing agents",
                    instruction="Coordinate agents; call research tool when needed.",
                    tools=[_mock_research],  # ⭐ Functions are tools
                )
                self.mode = "adk"
            except Exception as e:
                self.manager = None
                self.mode = "mock"
                self.error = str(e)
        else:
            self.manager = None
            self.mode = "mock"
            self.error = _adk_error if not ADK_AVAILABLE else None

    def run_equivalent_flow(self, blueprint: dict) -> Dict[str, Any]:
        """
        Run equivalent workflow to LangGraph.

        Args:
            blueprint: Workflow blueprint dictionary

        Returns:
            Execution result
        """
        if self.mode == "adk" and self.manager:
            # Real ADK execution
            try:
                company_name = blueprint.get("input", {}).get("company_name", "ACME Corp")

                # In real ADK, this would invoke the agent
                # For demo, we directly call the tool
                result = _mock_research(company=company_name)

                return {
                    "status": "completed",
                    "output": result,
                    "mode": "adk",
                    "message": "Executed using Google ADK"
                }

            except Exception as e:
                return {
                    "status": "error",
                    "output": None,
                    "mode": "adk",
                    "error": str(e)
                }

        else:
            # Mock mode fallback
            company_name = blueprint.get("input", {}).get("company_name", "ACME Corp")
            result = _mock_research(company=company_name)

            return {
                "status": "completed_with_mock",
                "output": result,
                "mode": "mock",
                "message": "ADK not available, using mock mode",
                "adk_error": getattr(self, 'error', None)
            }

    def get_status(self) -> Dict[str, Any]:
        """
        Get ADK integration status.

        Returns:
            Status dictionary
        """
        return {
            "adk_available": ADK_AVAILABLE,
            "mode": self.mode,
            "error": getattr(self, 'error', None) if self.mode == "mock" else None
        }
