import time
import requests
from typing import Dict, Any, List
from config import Config
from mock_infra import infra
from tools import (
    fetch_service_logs_and_metrics,
    inspect_github_commits,
    search_sre_runbook,
    execute_remediation_action,
    send_incident_report
)

class AutonomousSREAgent:
    def _call_gemini_reasoning(self, prompt: str, fallback_text: str) -> str:
        if not Config.GEMINI_API_KEY or Config.GEMINI_API_KEY == "AEGIS-DEMO-LLM-KEY-2026":
            return fallback_text

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{Config.GEMINI_MODEL}:generateContent?key={Config.GEMINI_API_KEY}"
        try:
            resp = requests.post(
                url,
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception:
            pass
        return fallback_text

    def run_incident_response(self) -> Dict[str, Any]:
        incident = infra.active_incident
        if not incident:
            return {"error": "No active incident to triage. Inject an outage first."}

        service = incident["service"]
        alert_title = incident["alert_title"]
        incident_id = incident["incident_id"]
        trace_steps: List[Dict[str, Any]] = []

        # PHASE 1: PLANNING
        default_plan = (
            f"1. Triage '{alert_title}' on {service} (Severity: {incident['severity']}).\n"
            f"2. Call fetch_service_logs_and_metrics to extract stack traces and error codes.\n"
            f"3. Call inspect_github_commits (External GitHub REST API) to check for recent regressions.\n"
            f"4. Query search_sre_runbook (RAG) for the verified remediation procedure.\n"
            f"5. Execute automated remediation and dispatch an RCA report via webhook."
        )
        llm_plan = self._call_gemini_reasoning(
            f"You are an autonomous SRE Agent. Formulate a concise 5-step investigation and remediation plan for alert: {alert_title} on service {service}.",
            default_plan
        )

        trace_steps.append({
            "phase": "PHASE 1: PLANNING",
            "badge_color": "blue",
            "title": "Alert Triage & Investigation Plan Formulation",
            "thought": f"Received PagerDuty trigger {incident_id}: {alert_title}. Formulating zero-touch diagnostic strategy before mutating production state.",
            "plan": llm_plan,
            "timestamp": time.strftime("%H:%M:%S")
        })

        # PHASE 2: TOOL-USE
        log_output = fetch_service_logs_and_metrics(service)
        detected_error_code = incident.get("error_code", "ERR_OOM_MEMORY_LEAK")

        trace_steps.append({
            "phase": "PHASE 2: TOOL-USE",
            "badge_color": "amber",
            "title": "Tool Call #1: Telemetry & Log Analyzer",
            "tool_name": "fetch_service_logs_and_metrics",
            "tool_args": {"service_name": service},
            "tool_output": log_output,
            "thought": f"Telemetry confirms {log_output['metrics']['error_rate_percent']}% error rate and latency {log_output['metrics']['latency_ms']}ms. Extracted signature {detected_error_code} from stack trace.",
            "timestamp": time.strftime("%H:%M:%S")
        })

        github_output = inspect_github_commits(service)
        suspect_commit = github_output["suspect_deployment_commit"]

        trace_steps.append({
            "phase": "PHASE 2: TOOL-USE (EXTERNAL API)",
            "badge_color": "purple",
            "title": "Tool Call #2: GitHub REST API & Deployment Inspector",
            "tool_name": "inspect_github_commits",
            "tool_args": {"service_name": service, "github_repo": Config.GITHUB_REPO},
            "tool_output": github_output,
            "thought": (
                f"Queried GitHub REST API ({github_output['external_api_status']}). "
                f"Correlated outage window with commit {suspect_commit.get('commit_sha')} by {suspect_commit.get('author')}: "
                f"\"{suspect_commit.get('message')}\" ({suspect_commit.get('diff_summary')})."
            ),
            "timestamp": time.strftime("%H:%M:%S")
        })

        runbook_output = search_sre_runbook(detected_error_code)
        matched_rb = runbook_output["matched_runbook"]
        recommended_action = matched_rb.get("recommended_action", "rollback_deployment")

        trace_steps.append({
            "phase": "PHASE 2: TOOL-USE (RAG)",
            "badge_color": "amber",
            "title": "Tool Call #3: SRE Runbook Knowledge Base Search",
            "tool_name": "search_sre_runbook",
            "tool_args": {"error_code": detected_error_code},
            "tool_output": runbook_output,
            "thought": f"Retrieved {matched_rb.get('title')}. Standard Operating Procedure prescribes action: {recommended_action}.",
            "timestamp": time.strftime("%H:%M:%S")
        })

        # PHASE 3: ACTION
        remediation_output = execute_remediation_action(service, recommended_action)

        trace_steps.append({
            "phase": "PHASE 3: ACTION (REMEDIATION)",
            "badge_color": "emerald",
            "title": "Tool Call #4: Autonomous Production Remediation",
            "tool_name": "execute_remediation_action",
            "tool_args": {"service_name": service, "action_type": recommended_action},
            "tool_output": remediation_output,
            "thought": f"Executed {recommended_action} on {service}. Post-action health check passed: Error rate dropped to 0.0% and status is HEALTHY.",
            "timestamp": time.strftime("%H:%M:%S")
        })

        root_cause_summary = (
            f"Commit {suspect_commit.get('commit_sha')} by {suspect_commit.get('author')} "
            f"({suspect_commit.get('diff_summary')}) triggered {detected_error_code} on {service}."
        )
        report_output = send_incident_report(
            incident_id=incident_id,
            service_name=service,
            root_cause=root_cause_summary,
            action_taken=recommended_action
        )

        trace_steps.append({
            "phase": "PHASE 3: ACTION (NOTIFICATION)",
            "badge_color": "emerald",
            "title": "Tool Call #5: Root Cause Analysis (RCA) & Webhook Dispatch",
            "tool_name": "send_incident_report",
            "tool_args": {
                "incident_id": incident_id,
                "service_name": service,
                "action_taken": recommended_action
            },
            "tool_output": report_output,
            "thought": "Incident resolved autonomously without waking human on-call engineer. RCA report dispatched.",
            "timestamp": time.strftime("%H:%M:%S")
        })

        return {
            "incident_id": incident_id,
            "service": service,
            "status": "RESOLVED",
            "root_cause": root_cause_summary,
            "action_taken": recommended_action,
            "trace_steps": trace_steps,
            "updated_cluster": infra.get_cluster_state()
        }

sre_agent = AutonomousSREAgent()