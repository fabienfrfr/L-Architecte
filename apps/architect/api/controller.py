from typing import Dict, Any
from apps.architect.agents.orchestrator import app_workflow, PMNode, AgentState
from apps.architect.dto.contracts import ArchitectureRequest
from apps.architect.dto.states import AgentStateDTO


class ArchitectController:
    """Handles the logic execution for the UI."""

    async def run_full_pipeline(self, request: ArchitectureRequest) -> Dict[str, Any]:
        internal_state = AgentState(requirements=request.requirements)
        
        result = await app_workflow.run(PMNode(), state=internal_state)

        return AgentStateDTO(
            requirements=result.state.requirements,
            charter_data=result.state.charter_data or {},
            analysis_report=result.state.analysis_report,
            architecture_specs=result.state.architecture_specs,
            final_code=result.state.final_code,
            is_ready=result.state.is_ready,
            retry_count=result.state.retry_count
        )