import requests
from typing import Dict, Any
from config import Config
from mock_infra import infra

def fetch_service_logs_and_metrics(service_name: str) -> Dict[str, Any]:
    """Tool 1: Queries telemetry metrics and recent error stack traces for a service."""
    service_metrics = infra.services.get(service_name, {})
    service_logs = infra.logs.get(service_name, ["No logs found."])
    return {
        "tool": "fetch_service_logs_and_metrics",
        "service": service_name,
        "metrics": service_metrics,
        "recent_logs": service_logs
    }

def inspect_github_commits(service_name: str) -> Dict[str, Any]:
    """
    Tool 2 (EXTERNAL API): Calls the live GitHub REST API to fetch recent repository
    commits and correlates them with the microservice deployment commit log.
    """
    local_commit = infra.commits_db.get(service_name, {})
    github_api_url = f"https://api.github.com/repos/{Config.GITHUB_REPO}/commits?per_page=2"
    headers = {"Accept": "application/vnd.github.v3+json", "User-Agent": "AegisSRE-AgentX"}
    if Config.GITHUB_TOKEN:
        headers["Authorization"] = f"token {Config.GITHUB_TOKEN}"

    live_github_commits = []
    api_status = "LIVE_GITHUB_API_200_OK"
    try:
        resp = requests.get(github_api_url, headers=headers, timeout=4)
        if resp.status_code == 200:
            for item in resp.json():
                live_github_commits.append({
                    "sha": item.get("sha", "")[:7],
                    "author": item.get("commit", {}).get("author", {}).get("name", "unknown"),
                    "message": item.get("commit", {}).get("message", "").split("\n")[0]
                })
        else:
            api_status = f"GITHUB_API_HTTP_{resp.status_code}"
    except Exception as e:
        api_status = f"OFFLINE_FALLBACK ({str(e)[:40]})"

    return {
        "tool": "inspect_github_commits",
        "external_api_status": api_status,
        "github_repo_queried": Config.GITHUB_REPO,
        "suspect_deployment_commit": local_commit,
        "recent_upstream_github_commits": live_github_commits
    }

def search_sre_runbook(error_code: str) -> Dict[str, Any]:
    """Tool 3 (RAG): Searches the SRE Runbook database for standard operating procedures."""
    matched_runbook = infra.runbooks.get(error_code)
    if not matched_runbook:
        for code, rb in infra.runbooks.items():
            if code in error_code or error_code in code:
                matched_runbook = rb
                break
    return {
        "tool": "search_sre_runbook",
        "queried_error_code": error_code,
        "matched_runbook": matched_runbook or {"error": "No matching runbook found; escalate to L3."}
    }

def execute_remediation_action(service_name: str, action_type: str) -> Dict[str, Any]:
    """Tool 4 (ACTION): Executes automated remediation (rollback, restart, or pool scale)."""
    result = infra.remediate_service(service_name, action_type)
    return {
        "tool": "execute_remediation_action",
        "remediation_result": result
    }

def send_incident_report(incident_id: str, service_name: str, root_cause: str, action_taken: str) -> Dict[str, Any]:
    """Tool 5 (EXTERNAL API): Dispatches the Root Cause Analysis (RCA) to a Discord Webhook."""
    webhook_status = "SIMULATED_WEBHOOK_DELIVERED (Set DISCORD_WEBHOOK_URL in config.py for live Discord alert)"
    payload = {
        "username": "AegisSRE Autonomous Agent",
        "content": (
            f"🚨 **INCIDENT RESOLVED: {incident_id}**\n"
            f"**Service:** {service_name}\n"
            f"**Root Cause:** {root_cause}\n"
            f"**Automated Action Taken:** {action_taken}\n"
            f"**Current Status:** HEALTHY (Error Rate: 0.0%)"
        )
    }

    if Config.DISCORD_WEBHOOK_URL and Config.DISCORD_WEBHOOK_URL.startswith("http"):
        try:
            r = requests.post(Config.DISCORD_WEBHOOK_URL, json=payload, timeout=4)
            webhook_status = f"LIVE_DISCORD_WEBHOOK_SENT (HTTP {r.status_code})"
        except Exception as e:
            webhook_status = f"WEBHOOK_ERROR: {str(e)}"

    return {
        "tool": "send_incident_report",
        "webhook_delivery_status": webhook_status,
        "rca_payload": payload["content"]
    }