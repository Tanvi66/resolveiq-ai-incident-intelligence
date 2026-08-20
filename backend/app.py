import os, json, random
from datetime import datetime, timezone
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.cloud import bigquery
from resolveiq_agent.bridge import ask_agent

app = FastAPI(title="ResolveIQ API", version="0.1.0")
bq_client = bigquery.Client()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

INCIDENTS = [
    {"id":"INC-1001","service":"Checkout","priority":"P1","category":"Payment","status":"Open","age_hours":5.2,"sla_hours":6,"customer_impact":420,"repeat_count":7},
    {"id":"INC-1002","service":"Search","priority":"P2","category":"Performance","status":"Investigating","age_hours":3.1,"sla_hours":8,"customer_impact":180,"repeat_count":4},
    {"id":"INC-1003","service":"Login","priority":"P2","category":"Authentication","status":"Open","age_hours":6.4,"sla_hours":8,"customer_impact":310,"repeat_count":6},
    {"id":"INC-1004","service":"Orders","priority":"P3","category":"Data","status":"Resolved","age_hours":2.2,"sla_hours":24,"customer_impact":35,"repeat_count":2},
    {"id":"INC-1005","service":"Checkout","priority":"P1","category":"Payment","status":"Investigating","age_hours":4.8,"sla_hours":6,"customer_impact":520,"repeat_count":9},
    {"id":"INC-1006","service":"Catalog","priority":"P3","category":"Data","status":"Open","age_hours":15.5,"sla_hours":24,"customer_impact":70,"repeat_count":3},
]

def risk_score(x):
    time_ratio = min(x["age_hours"] / x["sla_hours"], 1.5)
    impact = min(x["customer_impact"] / 500, 1)
    recurrence = min(x["repeat_count"] / 10, 1)
    priority = {"P1":1.0,"P2":0.65,"P3":0.35}.get(x["priority"],0.2)
    score = 100*(0.4*time_ratio + 0.25*impact + 0.2*recurrence + 0.15*priority)
    return round(min(score,100),1)

class AskRequest(BaseModel):
    question: str

@app.get("/")
def root():
    return FileResponse("frontend/index.html")

@app.get("/api/incidents")
def incidents():
    query = """
    SELECT
        incident_id,
        service,
        priority,
        category,
        status,
        age_hours,
        sla_hours,
        hours_remaining,
        customer_impact,
        repeat_count,
        ROUND(sla_score, 2) AS sla_risk,
        ROUND(impact_score, 2) AS impact_score,
        ROUND(recurrence_score, 2) AS recurrence_score,
        ROUND(priority_score, 2) AS priority_score,
        ROUND(risk_score, 2) AS risk_score,
        risk_level
    FROM `resolveiq-patchamomma.resolveiq.incident_risk`
    ORDER BY risk_score DESC
    LIMIT 100
    """

    rows = bq_client.query(query).result()

    return [dict(row) for row in rows]


@app.get("/api/summary")
def summary():
    query = """
    SELECT
        COUNTIF(status != "Resolved") AS open_incidents,
        COUNTIF(risk_score >= 70) AS high_risk,
        SUM(IF(status != "Resolved", customer_impact, 0)) AS customer_impact
    FROM `resolveiq-patchamomma.resolveiq.incident_risk`
    """

    row = list(bq_client.query(query).result())[0]

    service_query = """
    SELECT
        service,
        SUM(customer_impact) AS total_impact
    FROM `resolveiq-patchamomma.resolveiq.incident_risk`
    WHERE status != "Resolved"
    GROUP BY service
    ORDER BY total_impact DESC
    LIMIT 1
    """

    service_row = list(bq_client.query(service_query).result())[0]

    risk_query = """
    SELECT
        incident_id,
        service,
        priority,
        status,
        customer_impact,
        risk_score,
        risk_level
    FROM `resolveiq-patchamomma.resolveiq.incident_risk`
    ORDER BY risk_score DESC
    LIMIT 3
    """

    top_risks = [dict(x) for x in bq_client.query(risk_query).result()]

    return {
        "open_incidents": row.open_incidents,
        "high_risk": row.high_risk,
        "customer_impact": row.customer_impact or 0,
        "top_service": service_row.service,
        "top_risks": top_risks
    }


@app.post("/api/ask")
def ask(req: AskRequest):
    q = req.question.lower()

    if "sla" in q or "breach" in q:
        query = """
        SELECT incident_id, risk_score
        FROM `resolveiq-patchamomma.resolveiq.incident_risk`
        ORDER BY risk_score DESC
        LIMIT 3
        """

        rows = bq_client.query(query).result()

        ranked = [
            f"{row.incident_id} ({round(row.risk_score, 2)}%)"
            for row in rows
        ]

        answer = "Highest SLA-risk incidents: " + ", ".join(ranked) + "."

    elif "service" in q or "impact" in q:
        query = """
        SELECT service, SUM(customer_impact) AS total_impact
        FROM `resolveiq-patchamomma.resolveiq.incident_risk`
        GROUP BY service
        ORDER BY total_impact DESC
        LIMIT 1
        """

        row = list(bq_client.query(query).result())[0]

        answer = (
            f"{row.service} currently has the highest modeled "
            f"customer impact ({row.total_impact} affected users)."
        )

    elif "repeat" in q or "recurr" in q:
        query = """
        SELECT category, service, SUM(repeat_count) AS total_repeats
        FROM `resolveiq-patchamomma.resolveiq.incident_risk`
        GROUP BY category, service
        ORDER BY total_repeats DESC
        LIMIT 3
        """

        rows = bq_client.query(query).result()

        ranked = [
            f"{row.category} on {row.service} ({row.total_repeats} repeats)"
            for row in rows
        ]

        answer = "Most recurring patterns: " + ", ".join(ranked) + "."

    else:
        answer = (
            "I can analyze SLA risk, customer impact, recurring incidents, "
            "and priority trends. Try: "
            "'Which incidents are most likely to breach SLA?'"
        )

    return {"answer": answer, "mode": "bigquery-rule-engine"}


def _cache():
    return [dict(x, sla_risk=risk_score(x)) for x in INCIDENTS]

app.state_cache=_cache


@app.post("/api/ask-ai")
async def ask_ai(req: AskRequest):
    answer = await ask_agent(req.question)

    return {
        "answer": answer,
        "mode": "adk-gemini-bigquery"
    }
