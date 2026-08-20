# ResolveIQ — AI Incident Intelligence Platform

ResolveIQ is a Google Cloud-native, data-driven incident intelligence platform for IT/support operations.

## What it does
- Ingests synthetic incident records
- Scores SLA-breach risk
- Detects recurring incident patterns
- Generates AI-assisted triage and handover summaries
- Provides an operations dashboard
- Uses BigQuery for analytics, Firestore for app state, Pub/Sub for event flow, Gemini/ADK for agentic reasoning, and Cloud Run for deployment

## Architecture
Frontend -> Cloud Run API -> BigQuery / Firestore / Pub/Sub -> Gemini/ADK
                                  -> Looker Studio (analytics)

## Important
All sample data is synthetic. Do not upload confidential employer/work data.

## Local run
```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload --port 8080
```
Then open `frontend/index.html` and point the API URL to `http://localhost:8080`.

## Cloud deployment
See `infra/deploy.sh`.
