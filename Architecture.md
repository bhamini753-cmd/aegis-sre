# AegisSRE — Technical Architecture & Data Flow

## 1. Four-Tier Modular Architecture
1. Presentation Tier (static/index.html): Real-time SRE War-Room UI displaying service telemetry, chaos outage triggers, and the animated agent trace feed.
2. API Control Plane (main.py): FastAPI REST controller exposing /api/state, /api/inject, /api/run-agent, and /api/reset.
3. Autonomous Agent Core (agent.py & tools.py): Implements the Planning -> Tool-Use -> Action loop integrating Google Gemini, GitHub REST API, Runbook RAG, and Discord Webhooks.
4. Infrastructure Simulation & Container Mesh (mock_infra.py & docker-compose.yml): Simulates three production microservices (payment-service, auth-service, order-db-pool) and three realistic failure modes.

## 2. Incident Lifecycle Data Flow
1. Outage Injection: User triggers Scenario A, B, or C via the UI or chaos/*.cmd scripts.
2. Phase 1 (Planning): Agent receives the PagerDuty alert payload and generates a 5-step diagnostic plan.
3. Phase 2 (Tool-Use): Agent extracts the error signature from container logs, queries the live GitHub REST API for recent commits, and retrieves the matching runbook SOP.
4. Phase 3 (Action): Agent executes the prescribed remediation action, verifies that the service error rate returns to 0.0%, and dispatches the RCA webhook notification.