"""LLM client wrapper for OpenAI."""
import os
import json
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from openai import OpenAI
from src.utils.logging import setup_logger

load_dotenv()
logger = setup_logger(__name__)


class LLMClient:
    """Wrapper for OpenAI API calls."""

    def __init__(self, model: str = "gpt-4o-mini", mock: bool = False):
        """
        Initialize LLM client.

        Args:
            model: OpenAI model name
            mock: Whether to use mock responses
        """
        self.model = model
        self.mock = mock or os.getenv("MOCK", "0") == "1"

        if not self.mock:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("No OPENAI_API_KEY found, falling back to mock mode")
                self.mock = True
            else:
                self.client = OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.info("LLM client running in MOCK mode")

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ) -> str:
        """
        Generate text completion.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            json_mode: Whether to enforce JSON output
            temperature: Sampling temperature
            max_tokens: Maximum tokens in response

        Returns:
            Generated text
        """
        if self.mock:
            return self._mock_response(prompt, json_mode)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={"type": "json_object"} if json_mode else {"type": "text"}
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"LLM API error: {e}")
            logger.warning("Falling back to mock response")
            return self._mock_response(prompt, json_mode)

    def _mock_response(self, prompt: str, json_mode: bool) -> str:
        """Generate mock response for testing."""
        if json_mode:
            if "workflow" in prompt.lower() or "blueprint" in prompt.lower():
                return json.dumps({
                    "workflow_name": "mock_workflow",
                    "description": "Mock workflow for testing",
                    "input": {"company_name": "ACME Corp"},
                    "expected_output": {"format": "report"}
                })
            elif "decision" in prompt.lower() or "next_agent" in prompt.lower():
                return json.dumps({
                    "next_agent": "researcher",
                    "adjusted_prompts": {},
                    "notes": "Mock manager decision"
                })
            else:
                return json.dumps({"status": "mock", "result": "Mock JSON response"})
        else:
            if "research" in prompt.lower():
                return "Mock research findings: ACME Corp shows strong financials with 20% YoY growth."
            elif "write" in prompt.lower() or "report" in prompt.lower():
                return "Mock report:\n1. Financial Analysis: Strong performance\n2. Legal Review: No major issues\n3. Market Position: Leading competitor"
            elif "validate" in prompt.lower() or "quality" in prompt.lower():
                return "Validation passed. All required sections present."
            else:
                return "Mock LLM response for testing purposes."


def get_llm_client(model: str = "gpt-4o-mini", mock: bool = False) -> LLMClient:
    """
    Factory function to get LLM client.

    Args:
        model: Model name
        mock: Whether to use mock mode

    Returns:
        LLMClient instance
    """
    return LLMClient(model=model, mock=mock)
