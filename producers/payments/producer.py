import argparse
import os
import random
import time
from collections import deque

from producers.common import (
    PAYMENT_STATUSES_WEIGHTED,
    log_event,
    maybe,
    new_event_id,
    now_iso,
)

# Stores synthetic orders waiting for their payment
pending_orders = deque()


def weighted_status():
    """Choose payment status using the defined probabilities."""
    r = random.random()
    cumulative = 0

    for status, weight in PAYMENT_STATUSES_WEIGHTED:
        cumulative += weight

        if r <= cumulative:
            return status

    return PAYMENT_STATUSES_WEIGHTED[-1][0]


def enqueue_new_order():
    """Create a synthetic order that will receive a payment later."""
    order_id = f"ORD_{random.randint(5000, 59999)}"

    amount = round(
        random.uniform(500, 15000),
        2,
    )

    delay = random.uniform(1, 10)

    pending_orders.append(
        (
            order_id,
            amount,
            time.time() + delay,
        )
    )


def build_payment_event(order_id, amount):
    """Build one payment event."""
    return {
        "event_id": new_event_id("evt"),
        "payment_id": f"PAY_{random.randint(7000, 79999)}",
        "order_id": order_id,
        "amount": amount,
        "payment_method": random.choice(
            [
                "card",
                "bank_transfer",
                "wallet",
                "cod",
            ]
        ),
        "status": weighted_status(),
        "timestamp": now_iso(),
    }


def inject_dirty_data(event: dict) -> dict:
    """Inject a small amount of realistic dirty data."""

    if maybe(0.01):
        # Invalid amount
        event["amount"] = -abs(event["amount"])

    elif maybe(0.01):
        # Missing required field
        event.pop("order_id", None)

    elif maybe(0.01):
        # Unknown status
        event["status"] = "sucessful"

    return event


def run(max_events):
    count = 0

    while max_events is None or count < max_events:

        # Occasionally create a new synthetic order
        if maybe(0.5):
            enqueue_new_order()

        now = time.time()

        # Check whether the oldest pending order is ready
        if pending_orders and pending_orders[0][2] <= now:

            order_id, amount, _ = pending_orders.popleft()

            event = build_payment_event(
                order_id,
                amount,
            )

            # Occasionally duplicate the payment event
            if maybe(0.01):
                log_event("payments", event)
                count += 1

                if max_events is not None and count >= max_events:
                    break

            # Apply dirty-data injection
            event = inject_dirty_data(event)

            # Print payment event
            log_event("payments", event)

            count += 1

        time.sleep(1)

    print(
        f"[payments] stopped after {count} events",
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
            "\n[payments] shutting down gracefully",
            flush=True,
        )
