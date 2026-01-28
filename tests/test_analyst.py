import pytest
from apps.architect.agents.analyst import AnalystAgent

import httpx

def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200

@pytest.mark.bdd
class TestAnalystAgent:
    def test_analyze_cdc(self):
        agent = AnalystAgent()
        report = agent.analyze("Test CDC")
        assert "Automate data validation" in report.needs
        assert "High risk of scope creep" in report.risks
