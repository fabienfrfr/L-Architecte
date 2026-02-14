import pytest
from apps.architect.agents.nodes.engineer import EngineerAgent

import httpx
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


@pytest.mark.bdd
class TestEngineerAgent:
    async def test_generate_solid_code(self):
        agent = EngineerAgent()
        code = await agent.generate_solid_code({}, {})
        assert code.class_name == "DataValidator"
        assert "validate" in code.methods
