# Kafka Topics

## Phase 3 — Topic Configuration

NexPulse uses exactly three Kafka topics:

| Topic | Partitions | Replication Factor |
|---|---:|---:|
| orders | 3 | 1 |
| payments | 3 | 1 |
| inventory | 3 | 1 |

Topics were created explicitly using Kafka's `kafka-topics` CLI.

Verification was performed using:

```bash
docker exec -it nexpulse-kafka kafka-topics --describe --bootstrap-server localhost:9092