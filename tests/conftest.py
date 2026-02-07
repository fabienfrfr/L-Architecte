import os
import socket
import pytest
import httpx
from typing import Generator


def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.1)
        return s.connect_ex((host, port)) == 0


app_offline = not is_port_open("127.0.0.1", 8080)


@pytest.fixture(scope="session")
def client() -> Generator[httpx.Client, None, None]:
    server_url = os.getenv("APP_URL", "http://localhost:8080")
    with httpx.Client(base_url=server_url, timeout=5.0) as client:
        yield client
