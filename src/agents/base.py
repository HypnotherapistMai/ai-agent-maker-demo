"""Base agent class for all specialized agents."""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from src.llm.client import get_llm_client, LLMClient
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents."""

    def __init__(self, role: str, system_prompt: str):
        """
        Initialize base agent.

        Args:
            role: Agent role identifier
            system_prompt: System prompt for this agent
        """
        self.role = role
        self.system_prompt = system_prompt
        self.llm: LLMClient = get_llm_client()
        logger.info(f"Initialized {role} agent")

    @abstractmethod
    def process(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process the current state and return results.

        Args:
            state: Current workflow state
            **kwargs: Additional arguments

        Returns:
            Dictionary with processing results
        """
        pass

    def _generate_response(
        self,
        prompt: str,
        json_mode: bool = False,
        temperature: float = 0.7
    ) -> str:
        """
        Generate response using LLM.

        Args:
            prompt: User prompt
            json_mode: Whether to enforce JSON output
            temperature: Sampling temperature

        Returns:
            Generated response
        """
        return self.llm.generate(
            prompt=prompt,
            system_prompt=self.system_prompt,
            json_mode=json_mode,
            temperature=temperature
        )
