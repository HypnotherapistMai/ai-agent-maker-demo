"""Mock adapter when ADK is not available."""
from typing import Dict, Any, Callable, List


class MockADKAgent:
    """Mock ADK Agent for testing without google-adk installed."""

    def __init__(
        self,
        model: str = "gemini-2.0-flash-exp",
        name: str = "mock_agent",
        description: str = "",
        instruction: str = "",
        tools: List[Callable] = None
    ):
        """
        Initialize mock ADK agent.

        Args:
            model: Model name (ignored in mock)
            name: Agent name
            description: Agent description
            instruction: Agent instructions
            tools: List of tool functions
        """
        self.model = model
        self.name = name
        self.description = description
        self.instruction = instruction
        self.tools = tools or []

    def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mock agent invocation.

        Args:
            input_data: Input dictionary

        Returns:
            Mock result
        """
        return {
            "agent": self.name,
            "result": f"Mock response from {self.name}",
            "tools_available": len(self.tools)
        }
