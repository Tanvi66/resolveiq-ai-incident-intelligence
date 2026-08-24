from google.cloud import pubsub_v1
import json

PROJECT_ID = "resolveiq-patchamomma"
TOPIC_ID = "resolveiq-incidents"

publisher = pubsub_v1.PublisherClient()

topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

incident = {
    "incident_id": "INC-9428",
    "service": "Search",
    "priority": "P1",
    "status": "Open",
    "event_type": "incident.created"
}

data = json.dumps(incident).encode("utf-8")

future = publisher.publish(topic_path, data)

message_id = future.result()

print(f"Published incident event: {message_id}")
print(json.dumps(incident, indent=2))
