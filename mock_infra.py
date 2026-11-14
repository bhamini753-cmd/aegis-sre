import time
from typing import Dict, Any, List

class MockInfrastructure:
    def __init__(self):
        self.reset_cluster()

    def reset_cluster(self) -> Dict[str, Any]:
        self.active_incident = None
        self.services = {
            "payment-service": {
                "status": "HEALTHY",
                "cpu_percent": 24,
                "memory_mb": 410,
                "error_rate_percent": 0.1,
                "latency_ms": 45,
                "version": "v2.4.1",
                "last_commit": "7f8e9a0"
            },
            "auth-service": {
                "status": "HEALTHY",
                "cpu_percent": 18,
                "memory_mb": 290,
                "error_rate_percent": 0.0,
                "latency_ms": 22,
                "version": "v1.9.0",
                "last_commit": "3c4d5e6"
            },
            "order-db-pool": {
                "status": "HEALTHY",
                "cpu_percent": 31,
                "memory_mb": 1024,
                "error_rate_percent": 0.0,
                "latency_ms": 12,
                "version": "pg-15.2",
                "last_commit": "9a8b7c6"
            }
        }
        self.logs: Dict[str, List[str]] = {
            "payment-service": [
                "[INFO] 2026-11-14T02:00:01Z Worker initialized on port 8081",
                "[INFO] 2026-11-14T02:00:05Z Payment gateway healthcheck: 200 OK"
            ],
            "auth-service": [
                "[INFO] 2026-11-14T02:00:02Z JWT verification public key loaded",
                "[INFO] 2026-11-14T02:00:10Z Token refresh rate normal (140 req/s)"
            ],
            "order-db-pool": [
                "[INFO] 2026-11-14T02:00:00Z Connection pool active: 18/100 connections"
            ]
        }
        self.commits_db = {
            "payment-service": {
                "commit_sha": "a1b2c3d",
                "author": "dev-rahul",
                "timestamp": "12 minutes ago",
                "message": "feat(payment): enable unbounded in-memory retry cache for webhook payloads",
                "diff_summary": "Changed LRUCache(max_size=500) -> DictCache(unbounded=True) in worker.py"
            },
            "auth-service": {
                "commit_sha": "f9e8d7c",
                "author": "devops-priya",
                "timestamp": "8 minutes ago",
                "message": "chore(config): rotate JWT_SIGNING_SECRET in production env",
                "diff_summary": "Updated ENV JWT_SECRET_KEY in k8s-deployment.yaml without reloading Redis session store"
            },
            "order-db-pool": {
                "commit_sha": "b4n5m6k",
                "author": "backend-karthik",
                "timestamp": "19 minutes ago",
                "message": "perf(orders): remove connection timeout in analytics batch query",
                "diff_summary": "Set statement_timeout=0 and max_pool_connections=15 in db_config.json"
            }
        }
        self.runbooks = {
            "ERR_OOM_MEMORY_LEAK": {
                "id": "RB-101",
                "title": "Runbook RB-101: Memory Leak & OOMKilled in Worker Services",
                "symptom": "High memory utilization (>90%), HTTP 502 Bad Gateway, OutOfMemoryError stack traces.",
                "sop_steps": [
                    "1. Verify memory spike and OOM stack trace in service logs.",
                    "2. Inspect recent Git commits for caching or buffer regressions.",
                    "3. Execute automated rollback to previous stable release (rollback_deployment) and restart container."
                ],
                "recommended_action": "rollback_deployment"
            },
            "ERR_JWT_SIGNATURE_MISMATCH": {
                "id": "RB-204",
                "title": "Runbook RB-204: Auth Service 401/500 Spike After Secret Rotation",
                "symptom": "Sudden spike in InvalidSignatureError and HTTP 500 on /api/v1/verify.",
                "sop_steps": [
                    "1. Check auth-service error logs for JWT signature failures.",
                    "2. Check deployment config changes in Git.",
                    "3. Run sync_env_and_flush_sessions to synchronize secrets and flush stale token cache."
                ],
                "recommended_action": "sync_env_and_flush_sessions"
            },
            "ERR_DB_POOL_EXHAUSTED": {
                "id": "RB-309",
                "title": "Runbook RB-309: PostgreSQL Connection Pool Exhaustion",
                "symptom": "TimeoutError: QueuePool limit reached, latency > 2500ms.",
                "sop_steps": [
                    "1. Confirm QueuePool timeout errors in order-db-pool logs.",
                    "2. Terminate hanging batch queries and scale connection pool (scale_db_connection_pool)."
                ],
                "recommended_action": "scale_db_connection_pool"
            }
        }
        return self.get_cluster_state()

    def inject_incident(self, scenario_id: str) -> Dict[str, Any]:
        self.reset_cluster()
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if scenario_id == "memory_leak":
            self.services["payment-service"].update({
                "status": "CRITICAL",
                "cpu_percent": 94,
                "memory_mb": 3980,
                "error_rate_percent": 68.4,
                "latency_ms": 3420,
                "version": "v2.4.2-canary",
                "last_commit": "a1b2c3d"
            })
            self.logs["payment-service"] = [
                f"[WARN] {timestamp} Heap usage crossed 92% threshold (3.98 GB / 4.00 GB)",
                f"[ERROR] {timestamp} ERROR_CODE=ERR_OOM_MEMORY_LEAK java.lang.OutOfMemoryError: Heap space in PaymentRetryWorker.java:142",
                f"[CRITICAL] {timestamp} Upstream NGINX returning HTTP 502 Bad Gateway for /api/v2/checkout"
            ]
            self.active_incident = {
                "incident_id": "INC-2026-8841",
                "severity": "SEV-1 (P0)",
                "service": "payment-service",
                "alert_title": "HTTP 502 Bad Gateway Spike & High Memory (>95%) on payment-service",
                "error_code": "ERR_OOM_MEMORY_LEAK",
                "triggered_at": timestamp
            }

        elif scenario_id == "auth_outage":
            self.services["auth-service"].update({
                "status": "CRITICAL",
                "cpu_percent": 76,
                "memory_mb": 620,
                "error_rate_percent": 91.2,
                "latency_ms": 890,
                "version": "v1.9.1",
                "last_commit": "f9e8d7c"
            })
            self.logs["auth-service"] = [
                f"[ERROR] {timestamp} ERROR_CODE=ERR_JWT_SIGNATURE_MISMATCH jwt.InvalidSignatureError: HMAC key mismatch against Redis session store",
                f"[CRITICAL] {timestamp} 91.2% of login requests failing with HTTP 500 Internal Server Error"
            ]
            self.active_incident = {
                "incident_id": "INC-2026-8842",
                "severity": "SEV-1 (P0)",
                "service": "auth-service",
                "alert_title": "Mass HTTP 500 Authentication Failures on auth-service",
                "error_code": "ERR_JWT_SIGNATURE_MISMATCH",
                "triggered_at": timestamp
            }

        elif scenario_id == "db_lockup":
            self.services["order-db-pool"].update({
                "status": "CRITICAL",
                "cpu_percent": 99,
                "memory_mb": 1950,
                "error_rate_percent": 54.0,
                "latency_ms": 4850,
                "version": "pg-15.2-patched",
                "last_commit": "b4n5m6k"
            })
            self.logs["order-db-pool"] = [
                f"[WARN] {timestamp} Active connections: 15/15 (Wait queue: 412 queries)",
                f"[ERROR] {timestamp} ERROR_CODE=ERR_DB_POOL_EXHAUSTED sqlalchemy.exc.TimeoutError: QueuePool limit of size 15 overflow 0 reached",
                f"[CRITICAL] {timestamp} Database deadlock detected on table orders_ledger"
            ]
            self.active_incident = {
                "incident_id": "INC-2026-8843",
                "severity": "SEV-1 (P0)",
                "service": "order-db-pool",
                "alert_title": "Database Connection Pool Exhaustion & High Latency (4850ms)",
                "error_code": "ERR_DB_POOL_EXHAUSTED",
                "triggered_at": timestamp
            }

        return self.get_cluster_state()

    def remediate_service(self, service_name: str, action_type: str) -> Dict[str, Any]:
        timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        if service_name in self.services:
            self.services[service_name].update({
                "status": "HEALTHY",
                "cpu_percent": 21,
                "memory_mb": 380,
                "error_rate_percent": 0.0,
                "latency_ms": 34,
                "version": "v2.4.1-stable (Rolled Back)"
            })
            self.logs[service_name].append(
                f"[SUCCESS] {timestamp} Automated Remediation '{action_type}' executed by AegisSRE Agent. Healthcheck: 200 OK."
            )
        if self.active_incident and self.active_incident["service"] == service_name:
            self.active_incident["status"] = "RESOLVED"
        return {
            "status": "SUCCESS",
            "service": service_name,
            "action_executed": action_type,
            "new_metrics": self.services.get(service_name),
            "timestamp": timestamp
        }

    def get_cluster_state(self) -> Dict[str, Any]:
        return {
            "active_incident": self.active_incident,
            "services": self.services,
            "logs": self.logs
        }

infra = MockInfrastructure()