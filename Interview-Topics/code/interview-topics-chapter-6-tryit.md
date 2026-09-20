# Chapter 6: Microservices, REST & system design — Try it

*Answers for the Try it questions in [interview-topics-chapter-6.md](../interview-topics-chapter-6.md).*

1. Design an order service out loud. Start simple and add each component (Postgres, Redis, Kafka) only when you hit the bottleneck that justifies it.



2. Sync vs async between services — how do you choose? What does async cost you?



3. How do you make an operation idempotent, and why does at-least-once delivery force the question?



4. What's the dual-write problem, and how does the outbox pattern solve it?



5. Why is sharing one database across services an anti-pattern?



6. What status code for each: a successful `DELETE`; a POST that duplicates an existing unique record; a request with an expired login; a logged-in user hitting an endpoint they lack permission for?



7. REST vs gRPC between two internal services — when do you pick gRPC, and what do you give up? What does a service mesh take off your plate?
