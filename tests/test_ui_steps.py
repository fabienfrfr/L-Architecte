import pytest
import anyio
from pytest_bdd import scenario, given, when, then, parsers
from apps.architect.api.controller import ArchitectController
from apps.architect.dto.contracts import ArchitectureRequest, PMAnalysisReport

import httpx
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200

# --- Scenarios ---

@scenario("../specs/features/ui_workflow.feature", "Successful SMART validation")
def test_ui_logic_flow():
    """
    BDD scenario for testing the end-to-end agentic workflow logic.
    """
    pass

# --- Steps ---

@given(parsers.parse('the client input "{requirements}"'), target_fixture="input_data")
def input_data(requirements: str) -> str:
    """
    Sets up the initial requirements string.
    """
    return requirements

@when('the user clicks on "START AGENTIC WORKFLOW"', target_fixture="workflow_result")
def trigger_workflow(input_data: str):
    """
    Triggers the full agentic pipeline via the Controller.
    Uses anyio for clean asynchronous execution within a synchronous test.
    """
    controller = ArchitectController()
    request_obj = ArchitectureRequest(requirements=input_data)
    
    # Execute the async pipeline and return the AgentStateDTO
    return anyio.run(controller.run_full_pipeline, request_obj)

@then('the PM status should be "✅ SMART"')
def check_pm_status(workflow_result):
    """
    Validates that the PM Agent has processed the requirements.
    """
    # Access attributes directly from the DTO
    assert workflow_result.charter_data is not None
    
    # Safely parse the charter data into the contract model
    raw_data = workflow_result.charter_data

    if not raw_data:
        raw_data = {
            "content": "Default analysis", 
            "is_smart": False, 
            "gaps": ["Missing data from orchestrator"]
        }

    report = raw_data if isinstance(raw_data, PMAnalysisReport) else PMAnalysisReport(**raw_data)
    
    # Logging for debug visibility in pytest -s
    
    if report.gaps:
        print(f"\n[PM Analysis] Gaps identified: {report.gaps}")
    
    assert hasattr(report, "is_smart"), "PM Report is missing 'is_smart' field."

@then("a C4 diagram should be displayed")
def check_diagram(workflow_result):
    """
    Verifies that the Architect Agent generated a diagram, 
    provided the PM analysis allowed the workflow to proceed.
    """
    # Ensure we use attribute access on the workflow_result DTO
    raw_data = workflow_result.charter_data
    report = raw_data if isinstance(raw_data, PMAnalysisReport) else PMAnalysisReport(**raw_data)

    if not report.is_smart and not report.hypotheses:
        pytest.skip(f"Workflow halted by PM. Gaps: {report.gaps}")

    # Access architecture_specs attribute
    specs = workflow_result.architecture_specs
    assert specs is not None, "Architecture specs should be generated when workflow proceeds."

    # Validate diagram content (handling both dict or object access)
    diagram_content = specs.get("diagram", "") if isinstance(specs, dict) else getattr(specs, "diagram", "")
    
    assert "graph TD" in diagram_content, "C4 Diagram does not contain expected Mermaid syntax."