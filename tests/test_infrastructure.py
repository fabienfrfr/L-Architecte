import socket
import pytest
import os
import yaml


# Helper to load specs
def get_tunnel_specs():
    spec_path = "specs/functional/req_tunnels.yaml"
    if not os.path.exists(spec_path):
        pytest.fail(f"Specification file not found at {spec_path}")
    with open(spec_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a specific port is open on a host."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, socket.timeout, OSError):
        return False


@pytest.fixture
def tunnel_env():
    return {"specs": get_tunnel_specs()}


@pytest.mark.infra
class TestInfrastructure:
    """Tests to verify that the AgenticArchitect tunnels are correctly established."""

    def test_requirement_tunnels_active(self, tunnel_env):
        """
        REQ-TUNNELS / NET-01: Verify that all required port-forwards are active on localhost.
        """
        target = tunnel_env["specs"]["must_have"]["port_forwarding"]
        mappings = target["mapping"]

        failed_ports = []

        for entry in mappings:
            name = entry["name"]
            port = entry["local_port"]

            if not is_port_open("localhost", port):
                failed_ports.append(f"{name} (port {port})")

        assert not failed_ports, (
            f"Requirement {target['id']} failed: The following tunnels are closed: {', '.join(failed_ports)}. "
            "Action: Run 'make tunnels' to establish connectivity with the Kubernetes cluster."
        )

    def test_requirement_data_directory_ready(self):
        """
        Check for the critical PDF file used in ETL/Architect tests.
        """
        pdf_path = "tests/data/specification.pdf"
        assert os.path.exists(pdf_path), (
            f"Critical file missing: {pdf_path}. "
            "Please ensure the file is present in the repository or generated before tests."
        )
