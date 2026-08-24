import json
import asyncio

from google.cloud import pubsub_v1

from resolveiq_agent.bridge import ask_agent


PROJECT_ID = "resolveiq-patchamomma"
SUBSCRIPTION_ID = "resolveiq-incidents-sub"


subscriber = pubsub_v1.SubscriberClient()

subscription_path = subscriber.subscription_path(
    PROJECT_ID,
    SUBSCRIPTION_ID
)


def callback(message):
    print("\n=== ResolveIQ Pub/Sub Event Received ===")

    try:
        data = json.loads(message.data.decode("utf-8"))

        incident_id = data.get("incident_id")
        service = data.get("service")
        priority = data.get("priority")
        status = data.get("status")
        event_type = data.get("event_type")

        print("Incident ID:", incident_id)
        print("Service:", service)
        print("Priority:", priority)
        print("Status:", status)
        print("Event Type:", event_type)

        print("\n=== Sending Incident to ResolveIQ Agent ===")

        question = f"""
Analyze incident {incident_id}.

Incident details:
- Incident ID: {incident_id}
- Service: {service}
- Priority: {priority}
- Status: {status}
- Event Type: {event_type}

Provide:
1. SLA risk
2. Customer impact
3. Recommended priority/action
4. Any relevant recurring pattern
"""

        result = asyncio.run(ask_agent(question))

        print("\n=== ResolveIQ Agent Analysis ===")
        print(result)
        print("========================================\n")

        message.ack()

    except Exception as e:
        print("Error processing message:", e)
        message.nack()


streaming_pull_future = subscriber.subscribe(
    subscription_path,
    callback=callback
)

print(f"Listening on: {subscription_path}")

try:
    streaming_pull_future.result()

except KeyboardInterrupt:
    streaming_pull_future.cancel()
    streaming_pull_future.result()
