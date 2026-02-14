from pydantic_ai import Agent, ModelSettings
from apps.architect.domain.ports import IAnalystAgent
from apps.architect.domain.models import CadrageReport
from apps.architect.dao.llm_client import get_llm_model


class AnalystAgent(IAnalystAgent):
    """
    Real implementation using PydanticAI to interact with Ollama.
    """
    def __init__(self) -> None:
        self.model = get_llm_model()
        self.fields = list(CadrageReport.model_fields.keys())

        self._agent: Agent[None, CadrageReport] = Agent(
            model=self.model,
            output_type=CadrageReport,
            model_settings=ModelSettings(temperature=0.0,),
            retries=2,
            instructions=(
                "You are the Senior Analyst for TheArchitect. "
                "Reason VERY briefly. "
                "Extract needs, constraints, actors, and risks from the CDC. "
                f"Your output MUST be a JSON object with EXACTLY these keys: {self.fields}. "
                "If anything is unclear, add it to clarification_questions."
            ),
        )

    async def analyze(self, cdc_text: str) -> CadrageReport:
        result = await self._agent.run(cdc_text)
        return result.output