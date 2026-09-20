# Chapter 6: Microservices, REST & system design

*[← Chapter 5](interview-topics-chapter-5.md) · [Contents](interview-topics-README.md)*

- [ ] **Mark as read**

The previous chapters were single technologies; this one is how they **fit together**. Most backend loops include a focused design round — "design an order service," "design a notification system" — and a JD that lists Java + Spring + Postgres + Redis + Kafka is practically handing you the components. The concept beneath the brand here isn't a tool; it's a **method**: the one from [HLD](../HLD/hld-README.md) — *start simple, find the bottleneck, add one thing.*

The principle, applied to design: don't lead with the fancy component. **Earn it** by naming the pain it solves. Reaching for Kafka or sharding before you've established a bottleneck reads as pattern-matching, not reasoning.

---

## REST API design: the everyday version of design sense

> 💡 **Concept notes — what a clean API shows**
> - **Resource nouns + correct verbs/status codes** (`POST /orders` → 201; not found → 404; conflict → 409).
> - **Pagination, versioning, validation, a consistent error shape** (the `@ControllerAdvice` pattern from Chapter 2).
> - **Idempotency** — especially for retried POSTs: a stable idempotency key so a duplicate request produces the same end state. This becomes essential the moment async messaging enters (Chapter 4).

> 💡 **Concept notes — the status codes you should reach for without thinking**
> - **2xx success:** `200 OK` (read/update returned a body), `201 Created` (a POST made a resource — return its `Location`), `202 Accepted` (async: taken, not done yet), `204 No Content` (success, nothing to return — a `DELETE`).
> - **3xx redirect:** `301` moved permanently, `304 Not Modified` (the client's cached copy is still good — pairs with ETags/caching).
> - **4xx — the client is wrong (don't retry unchanged):** `400 Bad Request` (malformed), `401 Unauthorized` (not authenticated — *you haven't logged in*), `403 Forbidden` (authenticated but not allowed — *you can't do this*), `404 Not Found`, `409 Conflict` (clashes with current state — duplicate, version conflict), `422 Unprocessable` (well-formed but semantically invalid), `429 Too Many Requests` (rate-limited — back off).
> - **5xx — the server is wrong (safe to retry with backoff):** `500 Internal Server Error` (unhandled bug), `502 Bad Gateway` / `503 Service Unavailable` (a dependency is down / overloaded — the signal to shed load), `504 Gateway Timeout`.
> The two distinctions interviewers listen for: **401 vs 403** (authentication vs authorization) and **4xx vs 5xx** (whose fault it is — and therefore whether retrying can possibly help).

---

## Service boundaries

> 💡 **Concept notes — split by capability, own your data**
> Microservices split by **business capability**, each **owning its own data** (no shared database — that's the distributed-monolith trap). They talk via **sync** (REST/gRPC, when the caller needs the answer now) or **async** (Kafka/Pub-Sub, for side-effects, decoupling, and traffic spikes). Async trades immediate consistency for resilience and throughput. (Deeper: [HLD Ch 7](../HLD/hld-chapter-7.md).)

> 💡 **Concept notes — how services actually talk (and the mesh underneath)**
> - **REST/JSON** — ubiquitous, human-readable, great for public/edge APIs; verbose on the wire.
> - **gRPC/Protobuf** — a compact *binary* contract defined in a `.proto` schema, with generated client/server stubs and HTTP/2 streaming. Faster and strongly typed; the common default for *internal* service-to-service calls where both sides are yours. Cost: not browser-friendly, harder to eyeball and debug.
> - **Async messaging (Kafka/Pub-Sub)** — no direct call at all: the sender emits an event and moves on. For side-effects, decoupling, and spike absorption.
> - **Service mesh (Istio/Linkerd)** — once you have dozens of services, retries, timeouts, mTLS, and traffic routing shouldn't be re-implemented in every one. A mesh pushes those concerns into a **sidecar** proxy beside each service, so the platform handles cross-service plumbing and your code just makes the call. You pay for it with an extra hop and operational complexity — earn it.

---

## The arc that uses the whole stack

> 💡 **Concept notes — a strong design walkthrough**
> For "design an order/notification service," a clean arc that touches every JD keyword naturally:
> **REST API (Spring Boot)** → **Postgres** as the source of truth → **Redis** cache for hot reads (cache-aside + TTL) → **Kafka** for async side-effects (notify, update downstream) so the request path stays fast → then discuss **delivery guarantees, idempotency, and failure handling.**
> Clarify scale and consistency *first*; introduce each component when the previous design hits a wall.

> 💡 **Concept notes — the cross-cutting concerns that signal seniority**
> - **Idempotency** under at-least-once delivery (dedupe by id) — name it the moment you add Kafka.
> - **Retries with backoff, timeouts, circuit breakers** for unreliable dependencies.
> - **The outbox pattern** — write the state change and an "outbox" row in the *same* DB transaction, then a relay publishes the outbox to Kafka. Solves the dual-write problem (DB commits but the event publish fails, or vice versa).
> - **Observability** — logs, metrics, traces.

---

## Try it

Answer aloud:

1. Design an order service out loud. Start simple and add each component (Postgres, Redis, Kafka) only when you hit the bottleneck that justifies it.
2. Sync vs async between services — how do you choose? What does async cost you?
3. How do you make an operation idempotent, and why does at-least-once delivery force the question?
4. What's the dual-write problem, and how does the outbox pattern solve it?
5. Why is sharing one database across services an anti-pattern?
6. What status code for each: a successful `DELETE`; a POST that duplicates an existing unique record; a request with an expired login; a logged-in user hitting an endpoint they lack permission for?
7. REST vs gRPC between two internal services — when do you pick gRPC, and what do you give up? What does a service mesh take off your plate?

*Write your answers in [interview-topics-chapter-6-tryit.md](code/interview-topics-chapter-6-tryit.md).*

## The bumper sticker

> *A design round that lists Java/Spring/Postgres/Redis/Kafka is handing you the components — but the skill is the method, not the parts. Start simple, find the bottleneck, add one thing. Earn each component by naming the pain it solves, and the moment async enters, say "idempotency" before they ask.*

Next: the concern every one of those services shares — **auth** — the two questions (who are you? what may you do?) and the token that answers them.

---

<div align="right">

[Chapter 7 →](interview-topics-chapter-7.md)

</div>
