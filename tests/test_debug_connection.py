import os
import sys
import socket
from contextlib import closing

import pytest

import httpx
from conftest import app_offline


@pytest.mark.skipif(app_offline, reason="Apps don't listen 8080 port")
def test_status(client: httpx.Client):
    """Check if the UI is reachable."""
    assert client.get("/api/status").status_code == 200


def is_debug_active() -> bool:
    """Check if debugpy is actually listening for connections."""
    debugpy = sys.modules.get("debugpy")
    if not debugpy:
        return False
    try:
        # Returns (host, port) if listening, otherwise raises RuntimeError
        return bool(debugpy.address())
    except (AttributeError, RuntimeError):
        return False

@pytest.mark.skipif(not is_debug_active(), reason="debugpy is not listening")
def test_debugpy_port_is_reachable():
    """
    Verify that the debugpy port is accessible via the local port-forward.
    This ensures that the k3d pod is listening and the tunnel is active.
    """
    host = "127.0.0.1"
    port = int(os.getenv("DEBUG_PORT", "5678"))
    timeout = 2.0

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
        sock.settimeout(timeout)
        connection_result = sock.connect_ex((host, port))

        assert connection_result == 0, (
            f"Debug port {port} is not reachable on {host}. "
            "Ensure 'skaffold dev' or 'kubectl port-forward' is running."
        )
