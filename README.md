# AegisSRE — Autonomous On-Call Incident Agent

**Hackathon:** AgentX | Agentic AI Showcase (Sahyadri College of Engineering & Management, Mangaluru)  
**Problem Track:** On-Call Incident Agent – Engineering  

## 1. Overview
AegisSRE is an autonomous DevOps and Site Reliability Engineering (SRE) agent that detects, diagnoses, and resolves production microservice incidents using a structured **Planning -> Tool-Use -> Action** workflow without human intervention.

## 2. Quick Start (Windows / Linux / macOS)

### Option A: Run Directly with Python
1. Install dependencies:
   pip install -r requirements.txt
2. Start the server:
   python main.py
3. Open http://localhost:8000 in your browser.

### Option B: Run with Docker Compose
1. Build and start the container mesh:
   docker compose up --build -d
2. Open http://localhost:8000 in your browser.

## 3. Running the Automated Verification Suite
python tests/test_tools.py
python tests/test_remediation.py
python tests/test_api_endpoints.py