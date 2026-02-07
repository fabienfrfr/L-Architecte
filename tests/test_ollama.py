import pytest
import httpx
import os
import yaml

from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


# Function to load specifications
def get_specs():
    with open("specs/functional/req_ollama.yaml", "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def ollama_env():
    return {
        "url": os.getenv("OLLAMA_URL", "http://localhost:11434"),
        "specs": get_specs(),
    }


# Single responsibility test functions
@pytest.mark.asyncio
async def test_requirement_ollama_server_reachable(ollama_env):
    """
    REQ-OLLAMA / INFRA-01: Verify physical availability of the API.
    """
    target = ollama_env["specs"]["must_have"]["server"]
    url = f"{ollama_env['url']}{target['endpoint']}"

    async with httpx.AsyncClient(timeout=2.0) as client:
        try:
            response = await client.get(url)
            assert response.status_code == target["expected_status"], (
                f"Requirement {target['id']} failed: Server returned {response.status_code}"
            )
        except (httpx.ConnectError, httpx.ConnectTimeout):
            pytest.fail(f"Infrastructure error: Service unreachable at {url}")


@pytest.mark.asyncio
async def test_requirement_ollama_model_present(ollama_env):
    """
    REQ-OLLAMA / MODEL-01: Verify that the required model is pulled.
    """
    target = ollama_env["specs"]["must_have"]["model"]
    url = f"{ollama_env['url']}{target['endpoint']}"
    model_name = target["name"]

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url)
            assert response.status_code == 200

            models_data = response.json().get("models", [])
            local_names = [m["name"] for m in models_data]

            assert any(model_name in name for name in local_names), (
                f"Requirement {target['id']} failed: Model {model_name} not found. Please run 'ollama pull {model_name}'"
            )

        except (httpx.ConnectError, httpx.TimeoutException) as e:
            pytest.fail(f"Infrastructure error during model check: {str(e)}")
