@echo off
echo Injecting Scenario A: Payment Service Memory Leak & HTTP 502 Outage...
curl -X POST http://localhost:8000/api/inject -H "Content-Type: application/json" -d "{\"scenario_id\": \"memory_leak\"}"
echo.