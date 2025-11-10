from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)
r = client.get("/")
assert r.status_code == 200
