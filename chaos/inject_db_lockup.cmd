@echo off
echo Injecting Scenario C: Order Database Connection Pool Exhaustion...
curl -X POST http://localhost:8000/api/inject -H "Content-Type: application/json" -d "{\"scenario_id\": \"db_lockup\"}"
echo.