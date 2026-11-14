import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_full_api_lifecycle():
    # 1. Check initial healthy state
    r_state = client.get("/api/state")
    assert r_state.status_code == 200
    assert r_state.json()["active_incident"] is None

    # 2. Inject outage via POST /api/inject
    r_inject = client.post("/api/inject", json={"scenario_id": "auth_outage"})
    assert r_inject.status_code == 200
    assert r_inject.json()["services"]["auth-service"]["status"] == "CRITICAL"

    # 3. Trigger autonomous agent via POST /api/run-agent
    r_agent = client.post("/api/run-agent")
    assert r_agent.status_code == 200
    assert r_agent.json()["status"] == "RESOLVED"

    # 4. Reset cluster via POST /api/reset
    r_reset = client.post("/api/reset")
    assert r_reset.status_code == 200
    assert r_reset.json()["active_incident"] is None

if __name__ == "__main__":
    test_full_api_lifecycle()
    print("[PASS] test_api_endpoints.py: All FastAPI endpoints verified!")