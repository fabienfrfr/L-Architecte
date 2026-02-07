import json
import re
from typing import Any
from json_repair import repair_json

from pydantic_ai import Agent, ModelSettings, RunContext
from apps.architect.domain.ports import IAnalystAgent
from apps.architect.domain.models import CadrageReport
from apps.architect.dao.llm_client import get_llm_model # NEW FACTORY

# TODO: move to utils
def sanitize_json_response(content: str) -> str:
    """Removes markdown and repairs malformed JSON."""
    content = content.strip()
    if content.startswith('```'):
        content = re.sub(r'^```(?:json)?\s*|```$', '', content, flags=re.MULTILINE)
    return repair_json(content.strip())

class AnalystAgent(IAnalystAgent):
    """
    Real implementation using PydanticAI to interact with Ollama.
    """
    def __init__(self) -> None:
        self.model = get_llm_model()
        self.fields = list(CadrageReport.model_fields.keys())

        self._agent: Agent[None, str] = Agent(
            model=self.model,
            output_type=str,
            model_settings=ModelSettings(
                temperature=0.0,
                response_format={'type': 'json_object'}
            ),
            instructions=(
                "You are the Senior Analyst for TheArchitect. "
                "Extract needs, constraints, actors, and risks from the CDC. "
                f"Your output MUST be a JSON object with EXACTLY these keys: {self.fields}. "
                "If anything is unclear, add it to clarification_questions."
            ),
        )
        # We bind the external function to the agent's lifecycle
        self._agent.output_validator(self._post_process_result)

    def _post_process_result(self, ctx: RunContext[None], result_str: str) -> str:
        """Adapter method to bridge the agent and the utility function."""
        sanitized = sanitize_json_response(result_str)
        raw_data: dict[str, Any] = json.loads(sanitized)
        
        full_data = {field: raw_data.get(field, []) for field in self.fields}
        
        return json.dumps(full_data)
        
    async def analyze(self, cdc_text: str) -> CadrageReport:
        # Result is already sanitized by the validator
        result = await self._agent.run(cdc_text)
        return CadrageReport.model_validate_json(result.output)