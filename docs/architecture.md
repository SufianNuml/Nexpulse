## Kafka Concepts (NexPulse Implementation)

### Topics & Partitions

NexPulse uses three Kafka topics:

- `orders`
- `payments`
- `inventory`

Each topic has **3 partitions**. The local development Kafka cluster uses a **replication factor of 1** because it runs on a single broker.

The three partitions allow Kafka consumers in the same consumer group to process different partitions in parallel. For example, up to three consumer instances can consume the partitions of a topic concurrently.

In production, NexPulse would use multiple Kafka brokers and a higher replication factor, such as 3, for fault tolerance.

### Message Keys & Partitioning

NexPulse uses message keys when publishing events to Kafka.

- **Orders** use `event_id` as the message key.
- **Inventory** uses `event_id` as the message key.
- **Payments** use `order_id` as the message key.

Using `order_id` for payments is intentional. Payment events belonging to the same order are routed to the same Kafka partition, preserving their ordering within that order.

The smoke-test consumer verified that Kafka was distributing messages across partitions and that the message key was available to consumers.

### Consumer Groups & Offsets

NexPulse uses Kafka consumer groups to track consumption progress.

During Phase 3, I created a temporary `smoke-test-group` consumer that subscribed to all three topics.

Kafka maintained a separate committed offset for each topic partition for this consumer group. After the smoke test completed, the consumer-group inspection showed:

- `orders` — lag 0 on all partitions
- `payments` — lag 0 on all partitions
- `inventory` — lag 0 on all partitions

This demonstrated that the consumer successfully processed the available messages and committed its progress.

A consumer restarted with the same group ID can continue from its committed offsets instead of treating the stream as completely new.

Multiple consumers using the same group can share partitions, while consumers belonging to different groups maintain independent consumption positions.

### Retention Policy

The local development Kafka topics use the broker's default retention configuration.

Kafka is not intended to be the long-term storage layer for NexPulse. Kafka provides the streaming transport layer, while the Bronze Delta Lake layer introduced later in the architecture provides durable historical storage.

This keeps Kafka focused on real-time event delivery while Delta Lake becomes the long-term analytical storage layer.

### Delivery Semantics

The NexPulse producers use an **at-least-once delivery approach**.

A producer may retry delivery when a transient Kafka failure occurs. As a result, the same logical event can potentially appear more than once.

NexPulse deliberately includes duplicate-event generation and other dirty-data scenarios in the producers so that downstream data-quality and processing logic can handle realistic streaming conditions.

Deduplication is therefore treated as a downstream responsibility rather than something handled entirely by Kafka. The Silver layer will identify and remove duplicate events using the event identifiers and appropriate processing logic.

This design allows the streaming layer to prioritize reliable event delivery while the data-processing layer handles data quality and deduplication.