import pytest
from apps.architect.agents.nodes.architect import ArchitectAgent

import httpx
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


@pytest.mark.bdd
class TestArchitectAgent:
    async def test_generate_c4(self):
        agent = ArchitectAgent()
        diagram = await agent.generate_c4_diagram({})
        assert "graph TD" in diagram

    async def test_generate_adr(self):
        agent = ArchitectAgent()
        adr = await agent.generate_adr({})
        assert adr.title == "Use ChromaDB"
