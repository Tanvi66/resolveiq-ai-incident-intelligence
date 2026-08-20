# ResolveIQ — Patchamomma 2026 Build Plan

## Problem
Support teams often react to incidents one ticket at a time. This hides recurring patterns, SLA risk, and customer impact until it is too late.

## Product
ResolveIQ converts incident history into a live operations intelligence layer. It ranks incidents by modeled SLA-breach risk, identifies recurring patterns, estimates customer impact, and uses Gemini agents to explain what operators should do next.

## Agent design
1. Triage Agent — classifies severity and affected service.
2. SLA Risk Agent — calculates and explains breach risk.
3. Pattern Agent — clusters recurring categories/services.
4. Handover Agent — creates shift handover summaries.
5. Orchestrator — combines agent outputs into one operator recommendation.

## Google Cloud stack
- BigQuery: analytical incident warehouse and feature generation.
- Firestore: users, saved investigations, case state.
- Pub/Sub: incident event ingestion.
- Gemini / ADK: agentic analysis and explanations.
- Cloud Run: API and agent services.
- Cloud Storage: uploaded synthetic datasets / exports.
- Looker Studio: executive operations dashboard.
- Cloud Logging / IAM: observability and security.

BigQuery public datasets can also be used for additional non-confidential benchmark data.

## Demo story
A new P1 incident arrives. Pub/Sub triggers analysis. ResolveIQ combines incident history, SLA policy, recurrence, and impact to produce a risk score. Gemini explains the evidence and recommends the next diagnostic step. The dashboard shows the incident, why it is risky, and the broader recurring pattern.

## Checkpoints
Aug 15–20: MVP + synthetic data + first dashboard.
Aug 21–28: Gemini/ADK agents + BigQuery analytics + Pub/Sub.
Aug 29–Sep 5: Looker dashboard + security + evaluation + polish.
Sep 6–7: lock demo, documentation, architecture diagram, pitch.
Sep 10: results.
Sep 24: finale.

## Success metrics
- SLA-risk precision on a labeled synthetic test set.
- Reduction in time to identify high-risk incidents.
- Recurring-pattern detection accuracy.
- Quality score of AI-generated handovers using a human rubric.
- End-to-end event-to-insight latency.
