#!/usr/bin/env bash
set -e
echo "[AegisSRE] Installing dependencies..."
pip install -r requirements.txt
echo "[AegisSRE] Starting Autonomous On-Call Incident Agent on http://localhost:8000 ..."
python3 main.py