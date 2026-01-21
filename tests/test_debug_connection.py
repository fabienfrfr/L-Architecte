import os
import socket
from contextlib import closing

import pytest

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