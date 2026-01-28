import os
from typing import Generator
import httpx
import pytest

@pytest.fixture(scope="session")
def client() -> Generator[httpx.Client, None, None]:
    """ Handles the URL and the HTTP session.  """
    server_url = os.getenv("APP_URL", "http://localhost:8080")
    
    with httpx.Client(base_url=server_url, timeout=5.0) as client:
        yield client