import pytest
from apps.architect.agents.nodes.analyst import AnalystAgent
from apps.architect.domain.models import CadrageReport

import httpx

from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


@pytest.mark.bdd
class TestAnalystAgent:
    
    @pytest.mark.asyncio
    async def test_analyze_cdc(self):
        """
        Testing the real integration with Ollama via PydanticAI.
        Ensures the Domain Model is correctly populated.
        """
        # 1. Arrange
        agent = AnalystAgent()
        test_cdc = (
            "The client wants a system to automate data validation for ArangoDB. "
            "The budget is limited and scope creep is a major risk."
        )

        # 2. Act
        # We MUST use await now because PydanticAI is async
        report = await agent.analyze(test_cdc)

        # 3. Assert
        assert isinstance(report, CadrageReport)
        # TODO: We check for semantic meaning rather than exact strings
        #  --> construct an other test ? 1 test = 1 assert
        assert any("validation" in n.lower() for n in report.needs)
        assert any("scope" in r.lower() for r in report.risks)
        assert len(report.actors) >= 0  # Should be a list, even if empty