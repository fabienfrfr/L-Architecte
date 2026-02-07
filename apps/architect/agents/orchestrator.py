import json
import logging
from typing import TypedDict, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END

# --- Standardized Imports ---
from apps.architect.agents.nodes.pm import PMAgent
from apps.architect.agents.nodes.analyst import AnalystAgent
from apps.architect.agents.nodes.architect import ArchitectAgent
from apps.architect.agents.nodes.engineer import EngineerAgent

# --- State Definition ---


class AgentState(TypedDict):
    requirements: str
    charter_data: Optional[Dict[str, Any]]
    analysis_report: Optional[Dict[str, Any]]
    architecture_specs: Optional[Dict[str, Any]]
    final_code: Optional[Dict[str, Any]]
    is_ready: bool
    retry_count: int
    latest_error: Optional[str]


# --- Node Functions ---


def pm_node(state: AgentState) -> Dict[str, Any]:
    """Executes PM analysis and catches potential parsing errors."""
    agent = PMAgent()
    current_retry = state.get("retry_count", 0)

    try:
        # Step 1: Initial SMART Check
        response = agent.check_requirements(state["requirements"])
        content = response.content if hasattr(response, "content") else response
        data = json.loads(content)

        # Step 2: Adaptive Logic
        # If not SMART, we use the agent's second method to fill gaps
        if not data.get("is_smart", False):
            logging.info("Requirements not SMART. Calling hypotheses generation...")
            hypotheses_res = agent.fill_gaps_with_hypotheses(data)

            # Integration of hypotheses into the charter data
            hyp_content = (
                hypotheses_res.content
                if hasattr(hypotheses_res, "content")
                else hypotheses_res
            )
            hyp_data = json.loads(hyp_content)
            data["hypotheses"] = hyp_data.get("hypotheses", [])

        return {
            "charter_data": data,
            "is_ready": True,  # We force True because we now have hypotheses to proceed
            "latest_error": None,
            "retry_count": current_retry,
        }
    except Exception as e:
        logging.error(f"Inference error on try {current_retry}: {str(e)}")
        return {"latest_error": str(e), "retry_count": current_retry + 1}


def analyst_node(state: AgentState) -> Dict[str, Any]:
    """Analyst Agent: Performs data discovery."""
    agent = AnalystAgent()
    report = agent.analyze(state["requirements"])
    return {
        "analysis_report": (
            report.model_dump() if hasattr(report, "model_dump") else report.dict()
        )
    }


def architect_node(state: AgentState) -> Dict[str, Any]:
    """Architect Agent: Generates C4 diagrams and ADRs."""
    agent = ArchitectAgent()
    diagram = agent.generate_c4_diagram({"req": state["requirements"]})
    adr = agent.generate_adr({"context": "Local Deployment"})

    return {
        "architecture_specs": {
            "diagram": diagram,
            "adr": adr.model_dump() if hasattr(adr, "model_dump") else adr.dict(),
        }
    }


def engineer_node(state: AgentState) -> Dict[str, Any]:
    """Engineer Agent: Generates SOLID-compliant code."""
    agent = EngineerAgent()
    specs = state.get("architecture_specs")

    if not specs:
        raise ValueError(
            "Critical Error: Missing architecture specs for Engineer Agent."
        )

    code = agent.generate_solid_code(specs["adr"], specs["diagram"])
    return {
        "final_code": code.model_dump() if hasattr(code, "model_dump") else code.dict()
    }


def review_node(state: AgentState) -> Dict[str, Any]:
    """Critiques the proposed solution based on 'Less is More' principle."""
    # Simplified placeholder for the review logic
    # Put in context, say "it was a competing agent who produced result". (Mistral vs GPT)
    # But also, say "You are an objective reviewer". (Two perspectives)
    return state


# --- Routing Logic ---


def retry_router(state: AgentState) -> str:
    """Explicit Router for Error Handling and Business Logic."""
    if state.get("latest_error") and state.get("retry_count", 0) < 3:
        return "retry"
    if state.get("is_ready"):
        return "continue"
    return "stop"


# --- Graph Construction Function ---


def create_architect_graph() -> StateGraph:
    """
    Constructs and compiles the AgenticArchitect workflow.
    This encapsulation follows the 'Analyst -> Architect -> Engineer' methodology.
    """
    builder = StateGraph(AgentState)

    # Add all agents as nodes
    builder.add_node("pm", pm_node)
    builder.add_node("analyst", analyst_node)
    builder.add_node("architect", architect_node)
    builder.add_node("engineer", engineer_node)
    builder.add_node("reviewer", review_node)

    # Define the flow
    builder.add_edge(START, "pm")

    builder.add_conditional_edges(
        "pm",
        retry_router,
        {
            "retry": "pm",
            "continue": "analyst",
            "stop": END,
        },
    )

    builder.add_edge("analyst", "architect")
    builder.add_edge("architect", "engineer")
    builder.add_edge("engineer", "reviewer")
    builder.add_edge("reviewer", END)

    return builder.compile()


# --- Executable App Export ---
# This is the object you will import in your main.py and pass to layout.update_graph()
app_workflow = create_architect_graph()
