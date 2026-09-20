# Chapter 4: Kafka

*[← Chapter 3](interview-topics-chapter-3.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

Kafka is the technology most likely to be the *gap* on a backend resume — and the one where the brand name does the most to obscure a simple concept. Strip the label and Kafka is a **partitioned, replayable, append-only log**: the durable message queue from [HLD Ch 6–7](../HLD/hld-chapter-6.md), with retention so consumers can re-read history. This chapter gives you the must-knows *and* doubles as the template for answering any technology gap honestly.

The principle, sharpened: **feel the concept beneath the brand name** — *especially* when you haven't used the brand. If you've used any pub/sub system (GCP Pub/Sub, SQS, RabbitMQ), you've used the concept; you can bridge to Kafka instead of bluffing.

---

## The mental model

> 💡 **Concept notes — topic → partitions → consumer groups**
> - A **topic** is split into **partitions**, each an ordered, append-only log.
> - **Producers** write; **consumer groups** read. Within a group, **each partition is consumed by one consumer** — that's how Kafka scales out and load-balances.
> - **Offsets** track each consumer's read position; commit them after processing.
> - **Ordering is guaranteed only within a partition.** The producer's **key** chooses the partition (hash of the key), so same-key messages stay ordered. There is **no global ordering** — claiming it is a classic mistake.
> - Brokers **replicate** partitions for durability; **retention** lets you **replay** from an old offset.

---

## Delivery semantics: the question you must nail

> 💡 **Concept notes — at-least-once and idempotency**
> Three semantics: at-most-once, **at-least-once** (the practical default), exactly-once. At-least-once **will deliver duplicates** (a consumer crashes after processing but before committing the offset → redelivery). So the rule: **make consumers idempotent** — upsert by a business key, or dedupe with a Redis/DB key. Exactly-once exists (idempotent producer + transactions) but costs throughput and complexity, so reach for *idempotent at-least-once* first.

> 💡 **Concept notes — Kafka vs a classic queue**
> A traditional queue (RabbitMQ, SQS) is great for per-message routing/ack and task distribution; a message is typically consumed once and gone. Kafka is a **durable, replayable log with retention**: multiple consumer groups read the **same** stream independently, and you can replay from an offset. For event streaming, high throughput, and "several teams consume the same events," Kafka fits.

---

## The honest pivot — the template for any gap

> 💡 **Concept notes — bridge, don't bluff**
> When asked "have you used Kafka in production?" and you haven't, do **not** fake specifics — interviewers dig, and a shaky bluff is worse than an honest bridge. The template:
> 1. **Name the adjacent concept you *have* used** — "My event-driven work has been on GCP Pub/Sub."
> 2. **Map the concepts across** — "topics, partitions, consumer groups, at-least-once delivery, idempotent consumers — these carry over directly."
> 3. **Pivot to demonstrating understanding** — "Let me walk you through how I'd design a Kafka consumer."
> Honest, confident, forward. This same three-step move works for *any* technology gap (see Redis, Chapter 5).

---

## Build it, don't just read it

The fastest way to convert this gap: spin up Kafka locally (Docker), write a Spring Boot **producer + consumer** with `@KafkaListener`/`KafkaTemplate`, send/consume JSON, then force a duplicate and make the consumer **idempotent** (upsert by business key). One demo lets you answer almost any Kafka question from memory instead of theory.

---

## Try it

Answer aloud:

1. In one sentence, what *is* Kafka (the concept under the brand)?
2. How does Kafka scale consumption, and what's the ordering guarantee? What does the key control?
3. What delivery guarantee does Kafka give by default, and how do you avoid processing duplicates?
4. When would you choose Kafka over a traditional queue like RabbitMQ?
5. You've never used Kafka in production but you've used Pub/Sub. Give your honest-pivot answer out loud.

*Write your answers in [interview-topics-chapter-4-tryit.md](code/interview-topics-chapter-4-tryit.md).*

## The bumper sticker

> *Kafka is a partitioned, replayable log — name that and the questions follow: ordering is per-partition, delivery is at-least-once so consumers must be idempotent, and retention is what makes it more than a queue. And if it's a gap, bridge from the pub/sub concept you do know — the honest pivot beats the bluff every time.*

Next: the other common gap — **Redis** — where "it's a cache" is the concept, and *invalidation* is the hard part.

---

<div align="right">

[Chapter 5 →](interview-topics-chapter-5.md)

</div>
