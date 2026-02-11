import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any, Union

from pydantic_graph import BaseNode, End, Graph, GraphRunContext

# --- Standardized Imports ---
from apps.architect.agents.nodes.pm import PMAgent
from apps.architect.agents.nodes.analyst import AnalystAgent
from apps.architect.agents.nodes.architect import ArchitectAgent
from apps.architect.agents.nodes.engineer import EngineerAgent

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

@dataclass
class PMNode(BaseNode[AgentState]):
    """
    Executes PM analysis with SMART validation and hypothesis generation.
    Handles internal retries based on the state.
    """
    async def run(self, ctx: GraphRunContext[AgentState]) -> Union['PMNode', 'AnalystNode', End]:
        agent = PMAgent()
        
        try:
            # Step 1: Initial SMART Check
            # Using await as PydanticAI agents are async
            report = await agent.check_requirements(ctx.state.requirements)
            
            # Step 2: Adaptive Logic
            if not report.is_smart:
                logging.info("Requirements not SMART. Calling hypotheses generation...")
                hypotheses = await agent.fill_gaps_with_hypotheses(report.gaps)
                report.hypotheses = hypotheses

            ctx.state.charter_data = report.model_dump()
            ctx.state.is_ready = True
            ctx.state.latest_error = None
            
            return AnalystNode()

        except Exception as e:
            logging.error(f"Inference error on try {ctx.state.retry_count}: {str(e)}")
            ctx.state.latest_error = str(e)
            
            if ctx.state.retry_count < 3:
                ctx.state.retry_count += 1
                return self  # Equivalent to "retry" in retry_router
            return End(data="Max retries reached or stop condition.")

@dataclass
class AnalystNode(BaseNode[AgentState]):
    """Analyst Agent: Performs data discovery."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> 'ArchitectNode':
        agent = AnalystAgent()
        report = await agent.analyze(ctx.state.requirements)
        ctx.state.analysis_report = report.model_dump()
        return ArchitectNode()

@dataclass
class ArchitectNode(BaseNode[AgentState]):
    """Architect Agent: Generates C4 diagrams and ADRs."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> 'EngineerNode':
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
class EngineerNode(BaseNode[AgentState]):
    """Engineer Agent: Generates SOLID-compliant code."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> 'ReviewerNode':
        agent = EngineerAgent()
        specs = ctx.state.architecture_specs

        if not specs:
            raise ValueError("Critical Error: Missing architecture specs for Engineer Agent.")

        code = await agent.generate_solid_code(specs["adr"], specs["diagram"])
        ctx.state.final_code = code.model_dump()
        return ReviewerNode()

@dataclass
class ReviewerNode(BaseNode[AgentState]):
    """Critiques the proposed solution based on 'Less is More' principle."""
    async def run(self, ctx: GraphRunContext[AgentState]) -> End:
        # Objective review logic placeholder
        return End(data="Architecture flow completed successfully.")

# --- Graph Construction ---

architect_graph = Graph(
    nodes=(PMNode, AnalystNode, ArchitectNode, EngineerNode, ReviewerNode),
)

# Export for application use
app_workflow = architect_graph