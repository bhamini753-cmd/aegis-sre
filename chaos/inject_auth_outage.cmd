@echo off
echo Injecting Scenario B: Auth Service JWT Signature Mismatch Outage...
curl -X POST http://localhost:8000/api/inject -H "Content-Type: application/json" -d "{\"scenario_id\": \"auth_outage\"}"
echo.