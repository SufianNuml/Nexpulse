from confluent_kafka import Consumer

conf = {
    "bootstrap.servers": "localhost:9092",
    "group.id": "smoke-test-group",
    "auto.offset.reset": "earliest",
}

consumer = Consumer(conf)

consumer.subscribe(
    [
        "orders",
        "payments",
        "inventory",
    ]
)

print(
    "Smoke test consumer running. Ctrl+C to stop.",
    flush=True,
)

try:
    while True:
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            print(
                f"Consumer error: {msg.error()}",
                flush=True,
            )
            continue

        key = msg.key().decode("utf-8") if msg.key() else None

        value = msg.value().decode("utf-8")

        print(
            f"[{msg.topic()}] "
            f"partition={msg.partition()} "
            f"offset={msg.offset()} "
            f"key={key} "
            f"value={value}",
            flush=True,
        )

except KeyboardInterrupt:
    print(
        "\nStopping smoke test consumer.",
        flush=True,
    )

finally:
    consumer.close()
    print(
        "Smoke test consumer closed.",
        flush=True,
    )
