# Chapter 6: When work can wait — Try it

*Answers for the Try it questions in [hld-chapter-6.md](../hld-chapter-6.md).*

1. A user uploads a video. List which steps must be synchronous (user waits) and which should go on a queue, and justify each.


2. Explain load leveling: a launch causes 200,000 image-resize jobs in 30 seconds, but your workers can only do 2,000/sec. What does the queue do, how long until the backlog clears, and why does the user-facing app stay fast?


3. A payment-charge message gets delivered twice due to at-least-once delivery. What goes wrong if the handler isn't idempotent, and exactly how would you make it idempotent?


4. When would you choose Kafka (event log) over a simple task queue? Tie it to the Observer pattern.


5. Give one piece of work that must stay synchronous even though it's slow, and explain why it can't go on a queue.
