import csv
import random
from datetime import datetime, timedelta

random.seed(42)

NUM_RECORDS = 10000

services = {
    "Checkout": ["Payment", "Order", "Cart"],
    "Account": ["Authentication", "Profile", "Access"],
    "Search": ["Search", "Performance"],
    "Orders": ["Order", "Shipping", "Inventory"],
    "Catalog": ["Product", "Pricing", "Inventory"],
}

priorities = ["P1", "P2", "P3", "P4"]
statuses = ["Open", "Investigating", "Resolved", "Closed"]

sla_by_priority = {
    "P1": 6,
    "P2": 12,
    "P3": 24,
    "P4": 48,
}

descriptions = {
    "Payment": [
        "Payment gateway timeout",
        "Payment authorization failure",
        "Transaction processing delay",
        "Payment service unavailable",
    ],
    "Authentication": [
        "Users unable to login",
        "Authentication service timeout",
        "Invalid session errors",
        "Login service unavailable",
    ],
    "Order": [
        "Order creation failure",
        "Order processing delay",
        "Order status not updating",
        "Order service unavailable",
    ],
    "Cart": [
        "Cart update failure",
        "Items disappearing from cart",
        "Cart service timeout",
    ],
    "Search": [
        "Search results delayed",
        "Search service timeout",
        "Incorrect search results",
    ],
    "Performance": [
        "Application response time increased",
        "High API latency",
        "Service performance degradation",
    ],
    "Shipping": [
        "Shipping calculation failure",
        "Shipment status unavailable",
        "Delivery estimate incorrect",
    ],
    "Inventory": [
        "Inventory count mismatch",
        "Stock availability incorrect",
        "Inventory service timeout",
    ],
    "Profile": [
        "Profile update failure",
        "Customer profile unavailable",
    ],
    "Access": [
        "Access permission failure",
        "Unauthorized access error",
    ],
    "Product": [
        "Product information unavailable",
        "Product page failure",
    ],
    "Pricing": [
        "Incorrect product pricing",
        "Pricing service unavailable",
    ],
}

rows = []

start_date = datetime.now() - timedelta(days=180)

for i in range(1, NUM_RECORDS + 1):

    service = random.choice(list(services.keys()))
    category = random.choice(services[service])

    priority = random.choices(
        priorities,
        weights=[5, 20, 45, 30]
    )[0]

    sla_hours = sla_by_priority[priority]

    age_hours = round(
        random.uniform(0.2, sla_hours * 1.5),
        2
    )

    status = random.choices(
        statuses,
        weights=[20, 25, 35, 20]
    )[0]

    customer_impact = random.randint(1, 2000)

    # Higher-priority incidents tend to affect more customers
    if priority == "P1":
        customer_impact = random.randint(300, 3000)
    elif priority == "P2":
        customer_impact = random.randint(50, 1500)

    repeat_count = random.choices(
        range(1, 13),
        weights=[30, 20, 15, 10, 7, 5, 4, 3, 2, 2, 1, 1]
    )[0]

    # Repeated problems take slightly longer to resolve
    resolution_time = round(
        random.uniform(0.5, sla_hours * 1.2)
        + (repeat_count * 0.1),
        2
    )

    created_at = start_date + timedelta(
        minutes=random.randint(0, 180 * 24 * 60)
    )

    description = random.choice(
        descriptions.get(category, ["Service incident reported"])
    )

    rows.append([
        f"INC-{1000 + i}",
        created_at.strftime("%Y-%m-%d %H:%M:%S"),
        service,
        priority,
        category,
        status,
        age_hours,
        sla_hours,
        customer_impact,
        repeat_count,
        resolution_time,
        description,
    ])

with open("data/incidents.csv", "w", newline="") as f:

    writer = csv.writer(f)

    writer.writerow([
        "incident_id",
        "created_at",
        "service",
        "priority",
        "category",
        "status",
        "age_hours",
        "sla_hours",
        "customer_impact",
        "repeat_count",
        "resolution_time_hours",
        "description",
    ])

    writer.writerows(rows)

print(f"Generated {NUM_RECORDS} synthetic incidents.")
