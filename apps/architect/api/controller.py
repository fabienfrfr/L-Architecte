import asyncio
from typing import Dict, Any
from apps.architect.agents.orchestrator import app_workflow
from apps.architect.dto.contracts import ArchitectureRequest
from apps.architect.dto.states import AgentStateDTO


class ArchitectController:
    """Handles the logic execution for the UI."""

    async def run_full_pipeline(self, request: ArchitectureRequest) -> Dict[str, Any]:
        state = AgentStateDTO(requirements=request.requirements)

        return await asyncio.to_thread(app_workflow.invoke, state.model_dump())
