import json
import os
import random
import uuid
from datetime import datetime, timedelta, timezone

from confluent_kafka import Producer
from dotenv import load_dotenv

# Load variables from .env
load_dotenv()


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


# ---------------------------------------------------------
# Kafka configuration
# ---------------------------------------------------------


def build_kafka_config():
    """Build Kafka client configuration from environment variables."""

    bootstrap_servers = os.environ["KAFKA_BOOTSTRAP_SERVERS"]

    protocol = os.environ.get(
        "KAFKA_SECURITY_PROTOCOL",
        "PLAINTEXT",
    )

    config = {
        "bootstrap.servers": bootstrap_servers,
        "security.protocol": protocol,
    }

    # SASL settings are only required when using SASL_SSL.
    if protocol == "SASL_SSL":
        config["sasl.mechanisms"] = os.environ["KAFKA_SASL_MECHANISMS"]
        config["sasl.username"] = os.environ["KAFKA_SASL_USERNAME"]
        config["sasl.password"] = os.environ["KAFKA_SASL_PASSWORD"]

    return config


def get_producer():
    """Create and return a Kafka Producer."""
    return Producer(build_kafka_config())


def delivery_report(err, msg):
    """Report whether a Kafka message was delivered successfully."""

    if err is not None:
        print(
            f"[kafka] delivery FAILED: {err}",
            flush=True,
        )
    else:
        print(
            f"[kafka] delivered -> " f"{msg.topic()} " f"[partition {msg.partition()}]",
            flush=True,
        )
