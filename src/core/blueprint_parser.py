"""Blueprint parser: converts JSON or natural language to Workflow."""
import json
from typing import Union, List, Dict, Any
from src.core.schemas import Workflow, Step, AgentRole
from src.llm.client import get_llm_client
from src.utils.logging import setup_logger

logger = setup_logger(__name__)


class BlueprintParser:
    """Parse blueprint from JSON or natural language."""

    def __init__(self):
        """Initialize parser with LLM client."""
        self.llm = get_llm_client()

    def parse(self, raw_input: str, scenario: str = None) -> Workflow:
        """
        Parse blueprint from JSON or natural language.

        Args:
            raw_input: JSON string or natural language description
            scenario: Optional scenario hint (due_diligence, recruiting)

        Returns:
            Standardized Workflow object

        Raises:
            ValueError: If blueprint cannot be parsed
        """
        try:
            # Try JSON parsing first
            data = json.loads(raw_input)
            return self._parse_json(data)
        except json.JSONDecodeError:
            # Fall back to natural language parsing
            logger.info("JSON parsing failed, attempting natural language parsing")
            return self._parse_natural_language(raw_input, scenario)

    def _parse_json(self, data: dict) -> Workflow:
        """
        Build Workflow from JSON structure.

        Args:
            data: Parsed JSON dictionary

        Returns:
            Workflow object
        """
        # Validate required fields
        if "workflow_name" not in data:
            raise ValueError("Missing required field: workflow_name")

        # Generate default steps if not provided
        if "steps" not in data or not data["steps"]:
            logger.info(f"No steps provided, generating defaults for {data['workflow_name']}")
            data["steps"] = self._generate_default_steps(data["workflow_name"])

        # Convert to Pydantic model
        workflow = Workflow(
            name=data["workflow_name"],
            description=data.get("description", ""),
            steps=[Step(**s) for s in data["steps"]],
            input_data=data.get("input", {}),
            expected_output=data.get("expected_output", {}),
            meta_context=data.get("meta_context", {})
        )

        logger.info(f"Parsed workflow: {workflow.name} with {len(workflow.steps)} steps")
        return workflow

    def _parse_natural_language(self, text: str, scenario: str) -> Workflow:
        """
        Parse natural language request into Workflow using LLM.

        Args:
            text: Natural language description
            scenario: Scenario hint

        Returns:
            Workflow object
        """
        prompt = f"""Parse this workflow request into a structured format:

Request: {text}
Scenario hint: {scenario}

Output a JSON with:
- workflow_name: string (use scenario if provided, or infer from request)
- description: string (clear description of workflow purpose)
- input: dict (extract key entities like company_name, job_description, etc.)
- expected_output: dict (format, requirements)

Output ONLY valid JSON, no explanation."""

        response = self.llm.generate(prompt, json_mode=True)
        data = json.loads(response)

        # Ensure workflow_name is set
        if "workflow_name" not in data and scenario:
            data["workflow_name"] = scenario

        return self._parse_json(data)

    def _generate_default_steps(self, workflow_name: str) -> List[dict]:
        """
        Generate default workflow steps based on scenario.

        Args:
            workflow_name: Name of the workflow

        Returns:
            List of step dictionaries
        """
        if "due_diligence" in workflow_name.lower():
            return [
                {
                    "name": "research",
                    "agent_role": "researcher",
                    "input_keys": [],
                    "output_key": "research_findings",
                    "prompt_template": "Research the company for due diligence",
                    "validation_rules": {}
                },
                {
                    "name": "write_report",
                    "agent_role": "writer",
                    "input_keys": ["research_findings"],
                    "output_key": "report_draft",
                    "prompt_template": "Write a 3-point summary report covering financial, legal, and market analysis",
                    "validation_rules": {"min_sections": 3}
                },
                {
                    "name": "qa_check",
                    "agent_role": "qa",
                    "input_keys": ["report_draft"],
                    "output_key": "final_report",
                    "prompt_template": "Validate the report quality and completeness",
                    "validation_rules": {"must_contain": ["財務", "法律", "市場"]}
                }
            ]

        if "recruiting" in workflow_name.lower() or "jd" in workflow_name.lower():
            return [
                {
                    "name": "analyze_jd",
                    "agent_role": "researcher",
                    "input_keys": [],
                    "output_key": "jd_analysis",
                    "prompt_template": "Analyze the job description and extract key requirements",
                    "validation_rules": {}
                },
                {
                    "name": "create_strategy",
                    "agent_role": "writer",
                    "input_keys": ["jd_analysis"],
                    "output_key": "sourcing_strategy",
                    "prompt_template": "Create boolean search syntax and interview outline",
                    "validation_rules": {"must_include": ["boolean", "interview"]}
                },
                {
                    "name": "validate_output",
                    "agent_role": "qa",
                    "input_keys": ["sourcing_strategy"],
                    "output_key": "final_output",
                    "prompt_template": "Validate the sourcing strategy completeness",
                    "validation_rules": {}
                }
            ]

        # Default generic steps
        logger.warning(f"No specific template for workflow: {workflow_name}, using generic steps")
        return [
            {
                "name": "analyze",
                "agent_role": "manager",
                "input_keys": [],
                "output_key": "analysis",
                "prompt_template": "Analyze the request",
                "validation_rules": {}
            },
            {
                "name": "execute",
                "agent_role": "writer",
                "input_keys": ["analysis"],
                "output_key": "output",
                "prompt_template": "Execute the task",
                "validation_rules": {}
            },
            {
                "name": "validate",
                "agent_role": "qa",
                "input_keys": ["output"],
                "output_key": "final",
                "prompt_template": "Validate the output",
                "validation_rules": {}
            }
        ]
