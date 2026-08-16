import argparse
import os
import random
import sys
import time

# Allow this file to import producers/common.py
sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))

from producers.common import (  # noqa: E402
    now_iso,
    late_iso,
    new_event_id,
    log_event,
    maybe,
    ORDER_STATUSES,
)

# Small pools of IDs.
# These stay the same while the producer is running.
CUSTOMER_POOL = [f"CUS_{i}" for i in range(101, 301)]
PRODUCT_POOL = [f"PROD_{i}" for i in range(1, 51)]

CURRENCY = "PKR"


def build_order_event(event_id_override=None):
    """
    Create one normal order event.
    """

    order_id = f"ORD_{random.randint(5000, 59999)}"

    event = {
        "event_id": event_id_override or new_event_id("evt"),
        "order_id": order_id,
        "customer_id": random.choice(CUSTOMER_POOL),
        "product_id": random.choice(PRODUCT_POOL),
        "quantity": random.randint(1, 5),
        "amount": round(random.uniform(500, 15000), 2),
        "currency": CURRENCY,
        "timestamp": now_iso(),
        "status": random.choice(ORDER_STATUSES),
    }

    return event


def inject_dirty_data(event: dict) -> dict:
    """
    Occasionally introduce one realistic data-quality problem.
    """

    if maybe(0.01):
        # Invalid amount: negative
        event["amount"] = -abs(event["amount"])

    elif maybe(0.01):
        # Invalid amount: non-numeric
        event["amount"] = "N/A"

    elif maybe(0.01):
        # Negative quantity
        event["quantity"] = -10

    elif maybe(0.01):
        # Missing required field
        event.pop("customer_id", None)

    elif maybe(0.01):
        # Late event
        event["timestamp"] = late_iso()

    elif maybe(0.01):
        # Unknown status
        event["status"] = "proccessed"

    return event


def run(events_per_sec_range, max_events):
    """
    Generate orders continuously or until max_events is reached.
    """

    count = 0
    last_event = None

    while max_events is None or count < max_events:

        # Create a normal order
        event = build_order_event()

        # Occasionally duplicate the previous event
        if last_event and maybe(0.01):
            log_event("orders", last_event)
            count += 1
            continue

        # Occasionally make the event dirty
        event = inject_dirty_data(event)

        # Print event to console
        log_event("orders", event)

        # Remember the event for possible duplication
        last_event = event

        count += 1

        # Wait 1-3 seconds before next event
        time.sleep(random.uniform(*events_per_sec_range))

    print(
        f"[orders] stopped after {count} events",
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
        run(
            events_per_sec_range=(1, 3),
            max_events=args.max_events,
        )

    except KeyboardInterrupt:
        print(
            "\n[orders] shutting down gracefully",
            flush=True,
        )
