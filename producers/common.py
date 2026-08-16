import json
import random
import uuid
from datetime import datetime, timedelta, timezone

# Accepted order statuses
ORDER_STATUSES = [
    "completed",
    "cancelled",
    "pending",
]


# Payment statuses and their generation probabilities
PAYMENT_STATUSES_WEIGHTED = [
    ("successful", 0.85),
    ("failed", 0.08),
    ("pending", 0.05),
    ("refunded", 0.02),
]


def now_iso():
    """Current UTC time in the event timestamp format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def late_iso(min_minutes=2, max_minutes=15):
    """Generate a timestamp several minutes in the past."""
    delta = timedelta(minutes=random.randint(min_minutes, max_minutes))

    return (datetime.now(timezone.utc) - delta).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_event_id(prefix):
    """Generate a unique event ID."""
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def log_event(producer_name, event: dict):
    """Print an event as JSON to the console."""
    print(
        f"[{now_iso()}] " f"[{producer_name}] " f"{json.dumps(event)}",
        flush=True,
    )


def maybe(probability: float) -> bool:
    """Return True with the given probability."""
    return random.random() < probability
