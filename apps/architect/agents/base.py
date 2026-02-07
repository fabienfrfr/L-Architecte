import json
import re
from typing import Generic, TypeVar, List, Any, Type
from pydantic import BaseModel
from pydantic_ai import Agent, ModelSettings, RunContext

T = TypeVar("T", bound=BaseModel)

# TODO: build agent wrapper (work with or without tool included in ollama output)
class RobustAgent(Generic[T]):
    """
    Base agent to handle JSON repairing and structural enforcement for SLMs.
    """
    def __init__(self, model: Any, output_model: Type[T], instructions: str) -> None:
        self.output_model = output_model
        self.fields: List[str] = list(output_model.model_fields.keys())
        
        self._agent: Agent[None, str] = Agent(
            model=model,
            output_type=str,
            model_settings=ModelSettings(response_format={'type': 'json_object'}),
            instructions=f"{instructions} Output MUST be a JSON object with EXACTLY these keys: {self.fields}"
        )
        self._agent.output_validator(self._post_process_result)

    def _post_process_result(self, ctx: RunContext[None], result_str: str) -> str:
        # 1. Sanitization (Markdown removal)
        content = result_str.strip()
        if content.startswith('```'):
            content = re.sub(r'^```(?:json)?\s*|```$', '', content, flags=re.MULTILINE).strip()
        
        # 2. Structure enforcement (Key recovery)
        try:
            raw_data = json.loads(content)
        except json.JSONDecodeError:
            raw_data = {}
            
        full_data = {field: raw_data.get(field, []) for field in self.fields}
        return json.dumps(full_data)

    async def _call_llm(self, user_input: str) -> T:
        """Internal call to the agent and Pydantic validation."""
        result = await self._agent.run(user_input)
        return self.output_model.model_validate_json(result.output)