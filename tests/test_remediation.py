import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mock_infra import infra
from agent import sre_agent

def test_autonomous_incident_resolution():
    for scenario, service in [
        ("memory_leak", "payment-service"),
        ("auth_outage", "auth-service"),
        ("db_lockup", "order-db-pool")
    ]:
        infra.inject_incident(scenario)
        assert infra.services[service]["status"] == "CRITICAL"

        result = sre_agent.run_incident_response()
        assert result["status"] == "RESOLVED"
        assert len(result["trace_steps"]) == 6
        assert infra.services[service]["status"] == "HEALTHY"
        assert infra.services[service]["error_rate_percent"] == 0.0

if __name__ == "__main__":
    test_autonomous_incident_resolution()
    print("[PASS] test_remediation.py: All 3 outage scenarios autonomously resolved!")