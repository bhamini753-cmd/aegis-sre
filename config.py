import os

class Config:
    # 1. Google Gemini API Key (Includes pre-loaded demo fallback key so it runs out of the box)
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AEGIS-DEMO-LLM-KEY-2026")
    GEMINI_MODEL = "gemini-2.5-flash"

    # 2. External Tool #1: Live GitHub REST API target repository
    GITHUB_REPO = os.getenv("GITHUB_REPO", "tiangolo/fastapi")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

    # 3. External Tool #2: Optional Discord Webhook URL for live RCA alerts
    DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "")

    # 4. Web Server Settings
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))