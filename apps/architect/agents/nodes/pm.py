from typing import List, Dict, Any
from pydantic_ai import Agent, ModelSettings
from apps.architect.dao.llm_client import get_llm_model
from apps.architect.dto.contracts import PMAnalysisReport
from apps.architect.domain.models import TechnicalSpec

class PMAgent:
    """
    Project Manager Agent using PydanticAI.
    Ensures strict JSON output matching domain models.
    """

    def __init__(self) -> None:
        self.model = get_llm_model()
        self.settings = ModelSettings(temperature=0.0)

        # Agent for SMART validation
        self._checker_agent = Agent(
            model=self.model,
            output_type=PMAnalysisReport,
            model_settings=self.settings,
            retries=2,
            instructions=(
                "You are a strict Project Manager. Analyze requirements using SMART criteria. "
                "Reason VERY briefly. "
                "If ANY detail is missing, set 'is_smart' to false. "
                f"Output MUST be JSON with keys: {list(PMAnalysisReport.model_fields.keys())}."
            )
        )

        # Agent for Technical Specifications
        self._spec_agent = Agent(
            model=self.model,
            output_type=List[TechnicalSpec],
            model_settings=self.settings,
            retries=2,
            instructions=(
                "Generate 5 detailed technical requirements. "
                "Reason VERY briefly. "
                "Each item must strictly follow the TechnicalSpec schema: "
                f"{list(TechnicalSpec.model_fields.keys())}."
            )
        )

    async def check_requirements(self, requirements: str) -> PMAnalysisReport:
        """
        Validates raw input and maps it to PMAnalysisReport.
        """
        result = await self._checker_agent.run(requirements)
        report = result.output
        report.content = requirements
        return report

    async def generate_specs(self, validated_data: Dict[str, Any]) -> List[TechnicalSpec]:
        """
        Generates formal technical specifications from validated data.
        """
        result = await self._spec_agent.run(f"Points: {validated_data}")
        return result.output

    async def fill_gaps_with_hypotheses(self, report: PMAnalysisReport) -> List[str]:
        """
        Generates technical assumptions for missing information gaps.
        """
        # Specialized agent for list of strings
        agent = Agent(
            model=self.model,
            output_type=List[str],
            model_settings=self.settings,
            retries=2,
            instructions=(
                "Reason VERY briefly about technical gaps, "
                "then generate hypotheses. Return a JSON list of strings."
            )
        )
        result = await agent.run(f"Gaps: {report.gaps}")
        return result.output