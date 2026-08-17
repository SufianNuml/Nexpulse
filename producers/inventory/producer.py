import argparse
import atexit
import json
import os
import random
import sys
import time

# Allow this file to import producers/common.py
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))  # noqa: E402

from producers.common import (  # noqa: E402
    delivery_report,
    get_producer,
    log_event,
    maybe,
    new_event_id,
    now_iso,
)

PRODUCT_POOL = [f"PROD_{i}" for i in range(1, 51)]
WAREHOUSE_POOL = [f"WH_{i:02d}" for i in range(1, 6)]
SUPPLIER_POOL = [f"SUP_{i:02d}" for i in range(1, 15)]


# Initial stock level for every product/warehouse combination
stock_levels = {
    (product, warehouse): random.randint(50, 500)
    for product in PRODUCT_POOL
    for warehouse in WAREHOUSE_POOL
}


# Create one Kafka producer for this process
kafka_producer = get_producer()

# Make sure buffered Kafka messages are delivered when the process exits
atexit.register(lambda: kafka_producer.flush())


def build_inventory_event():
    """Generate one inventory event."""

    key = random.choice(list(stock_levels.keys()))
    product_id, warehouse_id = key

    # 30% chance of restocking
    # 70% chance of stock depletion
    if maybe(0.3):
        delta = random.randint(20, 100)
    else:
        delta = -random.randint(1, 10)

    stock_levels[key] = max(0, stock_levels[key] + delta)

    return {
        "event_id": new_event_id("evt"),
        "product_id": product_id,
        "warehouse_id": warehouse_id,
        "stock_quantity": stock_levels[key],
        "supplier_id": random.choice(SUPPLIER_POOL),
        "timestamp": now_iso(),
    }


def inject_dirty_data(event: dict) -> dict:
    """Inject a small amount of realistic dirty data."""

    if maybe(0.01):
        # Invalid negative stock
        event["stock_quantity"] = -event["stock_quantity"]

    elif maybe(0.01):
        # Missing required field
        event.pop("warehouse_id", None)

    return event


def run(max_events):
    """Generate inventory events continuously or until max_events is reached."""

    count = 0

    while max_events is None or count < max_events:
        event = build_inventory_event()
        event = inject_dirty_data(event)

        # Keep console logging for visibility during local development
        log_event("inventory", event)

        # Publish the same event to Kafka
        kafka_producer.produce(
            "inventory",
            key=event.get("event_id", "unknown"),
            value=json.dumps(event),
            callback=delivery_report,
        )

        # Trigger delivery callbacks without blocking
        kafka_producer.poll(0)

        count += 1

        # Generate one event every 2–5 seconds
        time.sleep(random.uniform(2, 5))

    print(
        f"[inventory] stopped after {count} events",
        flush=True,
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--max-events",
        type=int,
        default=os.getenv("EVENT_COUNT"),
    )

    args = parser.parse_args()

    try:
        run(max_events=args.max_events)

    except KeyboardInterrupt:
        print(
            "\n[inventory] shutting down gracefully",
            flush=True,
        )
        kafka_producer.flush()
