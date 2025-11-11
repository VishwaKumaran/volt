from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_root_endpoint():
    """Test that the root endpoint returns a welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "Welcome to" in data["message"]


def test_healthcheck_endpoint():
    """Test that the /health endpoint returns a valid status"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data.get("status") == "ok"
    assert data.get("database") == "reachable"

if __name__ == "__main__":
    test_healthcheck_endpoint()
    test_root_endpoint()