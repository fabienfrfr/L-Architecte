import pytest
import os
import yaml
import httpx
import socket
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


# Function to load specifications
def get_specs():
    # Update the path to your new YAML filename
    with open("specs/functional/req_observability.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def obs_env():
    return {"specs": get_specs()}


@pytest.mark.asyncio
async def test_requirement_phoenix_env_vars_exist(obs_env):
    """
    REQ-OBSERVABILITY / ENV-01: Check if Phoenix environment variables are set.
    """
    target = obs_env["specs"]["must_have"]["environment"]
    missing_keys = [key for key in target["keys"] if not os.getenv(key)]

    assert not missing_keys, (
        f"Requirement {target['id']} failed: Missing environment variables: {', '.join(missing_keys)}"
    )


@pytest.mark.asyncio
async def test_requirement_phoenix_connection(obs_env):
    """
    REQ-OBSERVABILITY / CONN-01: Verify that the Phoenix UI/API is reachable.
    """
    target = obs_env["specs"]["must_have"]["connection"]
    url = target["target_url"]

    async with httpx.AsyncClient() as client:
        try:
            # Checking the Phoenix UI/API health
            response = await client.get(f"{url}/customer-artifact/healthz", timeout=5.0)
            assert response.status_code == 200, (
                f"Requirement {target['id']} failed: Server returned {response.status_code}"
            )
        except Exception as e:
            pytest.fail(
                f"Infrastructure error: Could not connect to Phoenix at {url}. "
                f"Ensure 'make services-up' is running. Details: {str(e)}"
            )


@pytest.mark.asyncio
async def test_requirement_otlp_port_open(obs_env):
    """
    Check if the OTLP Collector port (4317) is accepting connections.
    """
    # Simple: Get the host from your YAML specs
    host = obs_env["specs"]["must_have"]["connection"]["otlp_host"]
    port = 4317

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    result = sock.connect_ex((host, port))
    sock.close()

    assert result == 0, f"OTLP Collector port {port} is closed on {host}."
