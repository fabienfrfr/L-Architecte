import json
import pytest
from pytest_bdd import scenario, given, when, then, parsers
from apps.architect.agents.pm import PMAgent

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
    context["result"] = agent.check_requirements(context["input"])


@then("the Charter should be marked as incomplete")
def check_analysis_result(context):
    # Extract the string content from the AIMessage and parse it
    raw_json = context["result"].content
    data = json.loads(raw_json)

    # Assert using your defined key 'is_smart'
    assert data["is_smart"] is False
