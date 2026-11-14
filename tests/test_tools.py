import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mock_infra import infra
from tools import (
    fetch_service_logs_and_metrics,
    inspect_github_commits,
    search_sre_runbook
)

def test_telemetry_and_log_parser():
    infra.inject_incident("memory_leak")
    res = fetch_service_logs_and_metrics("payment-service")
    assert res["service"] == "payment-service"
    assert res["metrics"]["status"] == "CRITICAL"
    assert any("ERR_OOM_MEMORY_LEAK" in line for line in res["recent_logs"])

def test_runbook_rag_lookup():
    rb = search_sre_runbook("ERR_OOM_MEMORY_LEAK")
    assert rb["matched_runbook"]["id"] == "RB-101"
    assert rb["matched_runbook"]["recommended_action"] == "rollback_deployment"

def test_github_commit_inspector():
    gh = inspect_github_commits("payment-service")
    assert gh["suspect_deployment_commit"]["commit_sha"] == "a1b2c3d"
    assert "external_api_status" in gh

if __name__ == "__main__":
    test_telemetry_and_log_parser()
    test_runbook_rag_lookup()
    test_github_commit_inspector()
    print("[PASS] test_tools.py: All tool unit tests passed!")