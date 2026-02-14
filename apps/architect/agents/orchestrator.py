import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

# --- Standardized Imports ---
from apps.architect.agents.nodes.pm import PMAgent
from apps.architect.agents.nodes.analyst import AnalystAgent
from apps.architect.agents.nodes.architect import ArchitectAgent
from apps.architect.agents.nodes.engineer import EngineerAgent

from apps.architect.dto.contracts import PMAnalysisReport

# --- State Definition ---

@dataclass
class AgentState:
    """
    State of the workflow, migrated from TypedDict to Dataclass for Pydantic Graph.
    Maintains all original fields for functional parity.
    """
    requirements: str
    charter_data: Optional[Dict[str, Any]] = None
    analysis_report: Optional[Dict[str, Any]] = None
    architecture_specs: Optional[Dict[str, Any]] = None
    final_code: Optional[Dict[str, Any]] = None
    is_ready: bool = False
    retry_count: int = 0
    latest_error: Optional[str] = None

# --- Node Definitions ---

PMNodeReturnValue = Union['PMNode', 'AnalystNode', End[None]]
AnalystNodeReturnValue = Union['ArchitectNode', End[None]]
ArchitectNodeReturnValue = Union['EngineerNode', End[None]]
EngineerNodeReturnValue = Union['ReviewerNode', End[None]]


@dataclass
class PMNode(BaseNode[AgentState, Any, None]):
    """
    Handles requirements validation using the PM Agent.
    Strict type checking ensures compatibility with the agentic workflow.
    """
    async def run(self, ctx: GraphRunContext[AgentState]) -> PMNodeReturnValue:
        agent = PMAgent()
        
        # Direct execution: exceptions will propagate and stop the graph if they occur
        report = await agent.check_requirements(ctx.state.requirements)
        
        # Type guard to handle non-deterministic LLM outputs in CI
        if not isinstance(report, PMAnalysisReport):
            logging.error(f"Invalid output format received: {type(report)}")
            return End(None)

        # Logic for non-SMART requirements
        if not report.is_smart:
            # Pass the full report object to satisfy Pyright signature requirements
            report.hypotheses = await agent.fill_gaps_with_hypotheses(report)

        # Update state using standardized model dumping
        ctx.state.charter_data = report.model_dump()
        ctx.state.is_ready = True
        
        return AnalystNode()

@dataclass
class AnalystNode(BaseNode[AgentState, Any, None]):
    """Analyst Agent: Performs data discovery."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> AnalystNodeReturnValue:
        agent = AnalystAgent()
        report = await agent.analyze(ctx.state.requirements)
        ctx.state.analysis_report = report.model_dump()
        return ArchitectNode()

@dataclass
class ArchitectNode(BaseNode[AgentState, Any, None]):
    """Architect Agent: Generates C4 diagrams and ADRs."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> ArchitectNodeReturnValue:
        agent = ArchitectAgent()
        # Assuming existing methods are migrated to async
        diagram = await agent.generate_c4_diagram({"req": ctx.state.requirements})
        adr = await agent.generate_adr({"context": "Local Deployment"})

        ctx.state.architecture_specs = {
            "diagram": diagram,
            "adr": adr.model_dump(),
        }
        return EngineerNode()

@dataclass
class EngineerNode(BaseNode[AgentState, Any, None]):
    """Engineer Agent: Generates SOLID-compliant code."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> EngineerNodeReturnValue:
        agent = EngineerAgent()
        specs = ctx.state.architecture_specs

        if not specs:
            raise ValueError("Critical Error: Missing architecture specs for Engineer Agent.")

        code = await agent.generate_solid_code(specs["adr"], specs["diagram"])
        ctx.state.final_code = code.model_dump()
        return ReviewerNode()

@dataclass
class ReviewerNode(BaseNode[AgentState, Any, None]):
    """Critiques the proposed solution based on 'Less is More' principle."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> End:
        # Objective review logic placeholder
        return End(None)

# --- Graph Construction ---

architect_graph = Graph(
    nodes=(PMNode, AnalystNode, ArchitectNode, EngineerNode, ReviewerNode),
)

# Export for application use
app_workflow = architect_graph