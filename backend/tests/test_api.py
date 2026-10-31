from fastapi.testclient import TestClient
from app.main import app
client=TestClient(app)
def test_health(): assert client.get("/api/health").status_code==200
def test_food_profiles(): assert len(client.get("/api/foods").json())==5
def test_ingest_requires_auth():
    r=client.post("/api/sensors/ingest",json={"message_id":"x","session_id":"x","food":"milk","measured_at":"2026-10-31T10:00:00Z","measurements":{"ph":6.7}})
    assert r.status_code==401
