"""Manager Agent: orchestrates workflow and applies meta-learning."""
import json
from typing import Dict, Any
from src.agents.base import BaseAgent
from src.core.memory import MemoryManager
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class ManagerAgent(BaseAgent):
    """
    Manager Agent: Coordinates the entire workflow.

    Responsibilities:
    1. Analyze workflow requirements
    2. Coordinate other agents
    3. Apply meta-learning to adjust strategies
    4. Make go/no-go decisions
    """

    def __init__(self):
        """Initialize Manager agent."""
        super().__init__(
            role="manager",
            system_prompt="""You are a workflow manager coordinating AI agents.

Your responsibilities:
1. Analyze the workflow blueprint and requirements
2. Coordinate researcher, writer, and QA agents
3. Learn from past failures and adjust prompts accordingly
4. Make strategic decisions about workflow execution
5. Provide clear guidance to other agents

Be strategic, adaptive, and proactive in preventing issues based on historical patterns."""
        )
        self.memory = MemoryManager()

    def process(self, state: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """
        Process current state and make strategic decisions.

        Args:
            state: Current workflow state

        Returns:
            Dictionary with manager decisions and adjusted prompts
        """
        workflow = state.get("workflow")
        if not workflow:
            logger.error("No workflow found in state")
            return {"error": "No workflow provided"}

        # Get meta-learning context
        learning_context = self.memory.get_learning_context(workflow.name)
        current_step = state.get("current_step", 0)

        # Get execution stats
        stats = self.memory.get_execution_stats(workflow.name)

        # Build decision prompt
        prompt = f"""Workflow: {workflow.name}
Description: {workflow.description}
Current step: {current_step}
Total steps: {len(workflow.steps)}

Execution Statistics:
- Total executions: {stats['total_executions']}
- Success rate: {stats['success_rate']:.1f}%
- Average duration: {stats['avg_duration']:.1f}s
- Average retries: {stats['avg_retries']:.1f}

{learning_context}

Input data: {json.dumps(workflow.input_data, indent=2)}

Based on historical learning and current context, provide strategic guidance:
1. What is the next agent to call? (researcher, writer, or qa)
2. Any specific adjustments to their prompts based on past failures?
3. Any special validation requirements?
4. Strategic notes or warnings?

Output JSON with:
{{
  "next_agent": "agent_name",
  "adjusted_prompts": {{"agent_name": "additional guidance"}},
  "validation_requirements": ["requirement1", "requirement2"],
  "notes": "strategic guidance"
}}"""

        try:
            response = self._generate_response(prompt, json_mode=True, temperature=0.5)
            decision = json.loads(response)

            logger.info(f"Manager decision: next agent = {decision.get('next_agent')}")

            return {
                "manager_decision": decision,
                "learning_applied": learning_context != "No historical failures for this workflow type.",
                "execution_stats": stats
            }

        except Exception as e:
            logger.error(f"Manager processing error: {e}")
            # Provide fallback decision
            return {
                "manager_decision": {
                    "next_agent": "researcher",
                    "adjusted_prompts": {},
                    "validation_requirements": [],
                    "notes": "Fallback decision due to processing error"
                },
                "learning_applied": False,
                "error": str(e)
            }

    def design_strategy(self, workflow_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Design execution strategy for a workflow.

        Args:
            workflow_name: Name of the workflow
            input_data: Input data for the workflow

        Returns:
            Strategy dictionary
        """
        learning_context = self.memory.get_learning_context(workflow_name)
        stats = self.memory.get_execution_stats(workflow_name)

        prompt = f"""Design an execution strategy for: {workflow_name}

Historical Context:
{learning_context}

Statistics:
- Success rate: {stats['success_rate']:.1f}%
- Average retries: {stats['avg_retries']:.1f}

Input: {json.dumps(input_data)}

Provide a strategy with:
1. Key risk areas to watch
2. Recommended validation checkpoints
3. Prompt adjustments for each agent type

Output JSON format."""

        try:
            response = self._generate_response(prompt, json_mode=True, temperature=0.5)
            return json.loads(response)
        except Exception as e:
            logger.error(f"Strategy design error: {e}")
            return {
                "risk_areas": ["output_quality", "completeness"],
                "validation_checkpoints": ["after_research", "after_writing"],
                "prompt_adjustments": {}
            }
