import pytest
from pytest_bdd import scenario, given, when, then, parsers
from apps.architect.agents.nodes.pm import PMAgent

import anyio

import httpx
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


@scenario(
    "../specs/features/pm.feature",
    "Incomplete requirements trigger gaps identification",
)
def test_pm_logic():
    pass


@given(parsers.parse('a client provides "{requirements}"'), target_fixture="context")
def client_requirements(requirements):
    return {"input": requirements}


@when("the PM Agent analyzes the request")
def analyze_request(context):
    agent = PMAgent()
    # The agent returns an AIMessage object
    context["result"] = anyio.run(agent.check_requirements, context["input"])


@then("the Charter should be marked as incomplete")
def check_analysis_result(context):
    report = context["result"]
    # Pydantic object.
    assert report.is_smart is False
