import pytest
from apps.architect.agents.engineer import EngineerAgent

import httpx

def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200

@pytest.mark.bdd
class TestEngineerAgent:
    def test_generate_solid_code(self):
        agent = EngineerAgent()
        code = agent.generate_solid_code({}, {})
        assert code.class_name == "DataValidator"
        assert "validate" in code.methods
