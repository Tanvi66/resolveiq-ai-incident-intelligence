from google.cloud import bigquery

PROJECT_ID = "resolveiq-patchamomma"
TABLE = f"`{PROJECT_ID}.resolveiq.incident_risk`"

bq_client = bigquery.Client(project=PROJECT_ID)


def get_sla_risk() -> str:
    """Get the incidents with the highest risk of breaching their SLA.
    Use this when the user asks about SLA risk, SLA breaches, or incidents
    most likely to breach their SLA.
    """
    query = f"""
    SELECT
        incident_id,
        service,
        priority,
        status,
        age_hours,
        sla_hours,
        hours_remaining,
        customer_impact,
        risk_score,
        risk_level
    FROM {TABLE}
    ORDER BY risk_score DESC
    LIMIT 5
    """

    rows = bq_client.query(query).result()

    results = []

    for row in rows:
        results.append(
            f"{row.incident_id}: service={row.service}, "
            f"priority={row.priority}, status={row.status}, "
            f"risk={round(row.risk_score, 2)}%, "
            f"hours_remaining={round(row.hours_remaining, 2)}, "
            f"impact={row.customer_impact}"
        )

    if not results:
        return "No incident risk data was found."

    return "Highest SLA-risk incidents:\n" + "\n".join(results)


def get_customer_impact() -> str:
    """Find which service currently has the highest modeled customer impact.
    Use this when the user asks about customer impact, affected users,
    business impact, or the most impacted service.
    """
    query = f"""
    SELECT
        service,
        SUM(customer_impact) AS total_impact,
        COUNT(*) AS incident_count
    FROM {TABLE}
    WHERE status != 'Resolved'
    GROUP BY service
    ORDER BY total_impact DESC
    LIMIT 5
    """

    rows = bq_client.query(query).result()

    results = []

    for row in rows:
        results.append(
            f"{row.service}: {row.total_impact} affected users "
            f"across {row.incident_count} active incidents"
        )

    if not results:
        return "No active customer-impact data was found."

    return "Customer impact by service:\n" + "\n".join(results)


def get_recurring_incidents() -> str:
    """Find the most recurring incident patterns by category and service.
    Use this when the user asks about recurring incidents, repeated issues,
    patterns, or services/categories with the most repeats.
    """
    query = f"""
    SELECT
        category,
        service,
        SUM(repeat_count) AS total_repeats
    FROM {TABLE}
    GROUP BY category, service
    ORDER BY total_repeats DESC
    LIMIT 5
    """

    rows = bq_client.query(query).result()

    results = []

    for row in rows:
        results.append(
            f"{row.category} on {row.service}: "
            f"{row.total_repeats} repeats"
        )

    if not results:
        return "No recurring incident data was found."

    return "Most recurring incident patterns:\n" + "\n".join(results)


def get_priority_recommendation() -> str:
    """Recommend which incidents should receive immediate attention.
    Use this when the user asks which incidents to prioritize,
    escalate, or act on first.
    """
    query = f"""
    SELECT
        incident_id,
        service,
        priority,
        status,
        hours_remaining,
        customer_impact,
        risk_score
    FROM {TABLE}
    WHERE status != 'Resolved'
    ORDER BY risk_score DESC, customer_impact DESC
    LIMIT 5
    """

    rows = bq_client.query(query).result()

    results = []

    for row in rows:
        action = "Immediate escalation"

        if row.hours_remaining > 0:
            action = "Prioritize before SLA breach"

        results.append(
            f"{row.incident_id}: service={row.service}, "
            f"priority={row.priority}, status={row.status}, "
            f"risk={round(row.risk_score, 2)}%, "
            f"hours_remaining={round(row.hours_remaining, 2)}, "
            f"impact={row.customer_impact}, "
            f"recommended_action={action}"
        )

    if not results:
        return "No active incidents require prioritization."

    return "Priority recommendations:\n" + "\n".join(results)

def get_incident_details(incident_id: str) -> str:
    """Get detailed information about a specific incident.
    Use this when the user asks to analyze, investigate, or get details
    about a specific incident ID.
    """
    query = f"""
    SELECT
        incident_id,
        service,
        priority,
        status,
        age_hours,
        sla_hours,
        hours_remaining,
        customer_impact,
        risk_score,
        risk_level,
        category,
        repeat_count
    FROM {TABLE}
    WHERE incident_id = @incident_id
    LIMIT 1
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "incident_id", "STRING", incident_id
            )
        ]
    )

    rows = bq_client.query(
        query,
        job_config=job_config
    ).result()

    for row in rows:
        action = "Immediate escalation"

        if row.hours_remaining > 0:
            action = "Prioritize before SLA breach"

        return (
            f"Incident: {row.incident_id}\n"
            f"Service: {row.service}\n"
            f"Priority: {row.priority}\n"
            f"Status: {row.status}\n"
            f"Category: {row.category}\n"
            f"Age: {round(row.age_hours, 2)} hours\n"
            f"SLA: {round(row.sla_hours, 2)} hours\n"
            f"Hours remaining: {round(row.hours_remaining, 2)}\n"
            f"Customer impact: {row.customer_impact}\n"
            f"SLA risk: {round(row.risk_score, 2)}%\n"
            f"Risk level: {row.risk_level}\n"
            f"Repeat count: {row.repeat_count}\n"
            f"Recommended action: {action}"
        )

    return f"No incident was found with ID {incident_id}."
