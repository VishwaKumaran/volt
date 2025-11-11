from app.main import app
from fastapi.testclient import TestClient

with TestClient(app) as client:
    r = client.get("/")
    assert r.status_code == 200
    assert "Welcome to" in r.json()["message"]

    r2 = client.get("/health")
    assert r2.status_code == 200
    data = r2.json()
    assert data.get("status") == "ok"
    assert data.get("database") == "reachable"
