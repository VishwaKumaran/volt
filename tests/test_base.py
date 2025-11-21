import pytest

from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.asyncio
def test_base():
    client = TestClient(app)
    r = client.get("/")
    assert r.status_code == 200
