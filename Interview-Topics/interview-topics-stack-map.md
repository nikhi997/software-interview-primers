# Field guide: one authenticated order through the stack

*[← Chapter 9](interview-topics-chapter-9.md) · [Contents](interview-topics-README.md)*

The chapters are recall cards per tool. The appendix is the skim-the-morning-of reference. This field guide does a different job: it follows **one concrete request** across the tools so you can explain why each brand sits where it sits.

Scenario: **create an authenticated order**.

Principle: **feel the concept beneath the brand name, then trace the failure branch before naming the fix.**

---

## The request, end to end

The user sends `POST /orders` with a bearer token, an `Idempotency-Key`, and an order body. The happy path is:

`POST /orders` → cloud load balancer / API gateway → OIDC/JWT validation + `orders:create` authorization → **one** application framework lane (Spring Boot **or** FastAPI) → Redis rate limit + idempotency key → Postgres transaction writes `order` + `outbox_event` → `201 Created` → outbox relay publishes `OrderCreated` to Kafka → payment and notification consumers process idempotently → `GET /orders/{id}` uses Redis cache-aside → service runs on Cloud Run or Kubernetes with managed data services, IAM, secrets, and observability.

Spring Boot and FastAPI are **alternative framework lanes**, not two services in the same flow. Pick the lane that matches your background, then map the concepts across.

---

## The stack map

| Hop | Brand / tool | Concept beneath it | Why it sits here | Must-know follow-up | Portable equivalent |
|---|---|---|---|---|---|
| Edge entry | Cloud load balancer | One stable front door that spreads requests across healthy instances | Keeps clients away from individual containers and survives instance churn | Health checks, TLS termination, timeouts, and what happens during a partial outage | AWS ALB/NLB, Azure Load Balancer, Nginx/Envoy, Kubernetes Ingress. Concept: [HLD scaling](../HLD/hld-README.md). |
| Edge policy | API gateway | Central request policy before app code | Token checks, routing, rate limits, request IDs, and coarse authorization belong at the boundary | Gateway auth is not business authorization; services still enforce sensitive permissions | AWS API Gateway, Apigee, Kong, Envoy, Spring Cloud Gateway. Concept: [HLD Ch 7](../HLD/hld-chapter-7.md). |
| Identity | OIDC + JWT | A signed claim about who the caller is | The order service can verify identity without calling the identity provider on every request | Validate signature, issuer, audience, expiry, and scopes; do not merely decode the token | Sessions, opaque tokens with introspection, SAML at enterprise edge. Concept: [Foundations networking](../Foundations/3-networking/ch8-networking.md) and [Chapter 7](interview-topics-chapter-7.md). |
| Permission | `orders:create` scope | Authorization: what the authenticated user may do | Creating an order is a business action, not just a logged-in state | `401` means token missing/invalid/expired; `403` means authenticated but not allowed | RBAC roles, ACLs, policy engines like OPA, Spring `@PreAuthorize`, FastAPI dependency checks. |
| Java lane | Spring Boot controller | Dependency injection + HTTP routing | It receives the request, delegates to services, and keeps business logic out of the controller | Constructor injection, centralized errors, `@Transactional` boundaries, bean validation | FastAPI route, Express/Nest controller, ASP.NET controller. Concept: [LLD dependency inversion](../LLD/lld-README.md). |
| Java validation | Bean Validation (`@Valid`) | A schema check at the boundary | Bad input should fail before it touches business logic or the database | Validation failure is usually `400` or `422` depending on API convention; keep the error shape stable | Pydantic, Joi/Zod, JSON Schema, Rails validations. |
| Python lane | FastAPI route | ASGI routing + dependency injection | Same application role as Spring, but Python async and type-driven | Do not block the event loop with sync I/O inside `async def`; use async clients or a threadpool | Spring Boot, Django/DRF, Flask, ASP.NET. Concept: [Chapter 9](interview-topics-chapter-9.md). |
| Python validation/auth | Pydantic + `Depends` | Typed parsing plus dependencies handed in by the framework | Pydantic validates the body; `Depends` injects current user, DB session, and clients | Pydantic v1/v2 differences; dependency overrides make tests clean | Bean Validation + Spring Security filters, middleware, manual validators. |
| Abuse control | Redis rate limit | Fast shared counter with expiry | A per-user or per-token counter protects the write path before expensive work | Use Lua or a transaction so the increment and first expiry cannot split; decide fail-open vs fail-closed if Redis is down | In-process limiter, API gateway quota, Cloud Armor/WAF, token bucket in a database. Concept: [HLD Ch 5](../HLD/hld-chapter-5.md). |
| Retry safety | Redis idempotency key | Remember that a client retry already produced a result | `POST /orders` can be retried by clients, gateways, or networks; the key prevents duplicate orders | Store request fingerprint + status/result; handle in-progress keys; TTL must match retry window | Unique DB constraint on `(user_id, idempotency_key)`, DynamoDB conditional write, application dedupe table. |
| Source of truth | PostgreSQL | Relational state with transactions, constraints, and isolation | Orders need durable, queryable truth and invariants like unique idempotency keys | Index the idempotency key; use the right isolation or row locks for invariants; every index slows writes | MySQL, SQL Server, Oracle, Cloud SQL/RDS/Azure Database. Concept: [Foundations SQL](../Foundations/1-sql-and-databases/sql/ch3-sql.md). |
| Atomic change | Postgres transaction | All-or-nothing write | The `order` row and `outbox_event` row must commit or roll back together | Atomicity covers the database transaction only; it does not guarantee Kafka publish | Any ACID relational transaction. Concept: [Foundations transactions](../Foundations/1-sql-and-databases/sql/ch3-sql.md). |
| Async bridge | Transactional outbox | Store the event beside the state change, then publish later | Avoids the dual-write bug: DB commit succeeds but publish fails, or publish succeeds and DB rolls back | Relay must be idempotent; mark or delete sent rows carefully; monitor relay lag | Change data capture, Debezium outbox, queue table, event sourcing. Concept: [HLD queues](../HLD/hld-chapter-6.md). |
| Event stream | Kafka topic `OrderCreated` | Partitioned, replayable, append-only log | Payment and notification do not need to run inside the request path | Ordering is only within a partition; choose a key like `order_id` or `customer_id` based on the ordering you need | GCP Pub/Sub, SQS/SNS, RabbitMQ, Pulsar. Concept: [HLD Ch 6–7](../HLD/hld-chapter-6.md). |
| Consumers | Kafka consumer groups | Independent readers over the same event stream | Payment and notification can scale separately and replay without blocking order creation | At-least-once means duplicates happen; commit offsets after durable processing | Pub/Sub subscriptions, SQS worker fleets, RabbitMQ consumers. |
| Consumer safety | Idempotent payment/notification handlers | Repeating the same message has the same effect | Kafka redelivery, retries, and deploys can run a handler twice | Use business keys, processed-event tables, or provider idempotency keys; never assume exactly-once end to end | Same pattern in any queue, cron retry, webhook receiver, or batch job. |
| Failure parking | Retries + DLQ | Try transient failures, isolate poison messages | A bad payment payload should not block the whole partition forever | Backoff, max attempts, alerting, replay procedure, and privacy of DLQ payloads | Pub/Sub dead-letter topics, SQS DLQ, RabbitMQ DLX. |
| Read path | `GET /orders/{id}` + Redis cache-aside | Read-through-by-application cache | Hot reads can skip Postgres while Postgres remains source of truth | Miss → DB → cache with TTL; write/update → invalidate or update cache; TTL bounds staleness | CDN for public data, local cache, Memcached, database read replica. Concept: [HLD Ch 5](../HLD/hld-chapter-5.md). |
| Runtime | Cloud Run | Managed container runtime | Good when you want request-driven autoscaling without managing nodes | Cold starts, concurrency per instance, connection pooling, max request duration | AWS App Runner/Lambda containers, Azure Container Apps, Fly.io. |
| Runtime | Kubernetes | Container orchestration platform | Good when you need long-running workers, custom networking, sidecars, or platform control | Readiness/liveness probes, rolling deploys, resource limits, service accounts | GKE/EKS/AKS, Nomad, ECS. Concept: [HLD](../HLD/hld-README.md). |
| Managed data | Managed Postgres / Redis / Kafka | Outsourced operations for stateful systems | Backups, patching, failover, and scaling are platform concerns, not app code | Know what is still yours: schema, indexes, connection pools, TTLs, partition keys, ACLs | Cloud SQL/RDS, Memorystore/ElastiCache, MSK/Confluent Cloud/Pub/Sub. |
| Access control | IAM / service accounts | Machine identity and least privilege | The service should access only the DB, cache, broker, and secrets it needs | Distinguish user identity from service identity; rotate and scope credentials | AWS IAM roles, Azure managed identities, Kubernetes service accounts. |
| Configuration | Secret Manager | Runtime secret delivery outside source control | DB passwords, signing keys, and broker credentials must not live in code or images | Rotation plan, versioning, least privilege, and no secret values in logs | AWS Secrets Manager/SSM, Vault, Kubernetes Secrets with external secret operators. |
| Observability | Logs, metrics, traces | The feedback loop for production behavior | You need to see one request across gateway, app, DB, Kafka relay, and consumers | Correlation IDs, RED metrics, consumer lag, outbox lag, error rates, p95/p99 latency | OpenTelemetry, Cloud Logging/Monitoring/Trace, Datadog, Prometheus/Grafana. Concept: [HLD reliability](../HLD/hld-README.md). |

---

## The happy path, spoken like an interview answer

"A client calls `POST /orders` through the cloud load balancer and API gateway. The gateway validates the OIDC JWT — signature, issuer, audience, expiry — and the service authorizes the `orders:create` scope. In the app I would implement the route in either Spring Boot with bean validation or FastAPI with Pydantic and `Depends`; same role, different framework lane.

Before the expensive write, Redis enforces a rate limit and checks the idempotency key. Then Postgres is the source of truth: in one transaction I insert the `orders` row and an `outbox_event` row. If that commits, the API can return `201 Created`. A relay later publishes `OrderCreated` from the outbox to Kafka. Payment and notification are separate consumer groups, and because Kafka is at-least-once, those consumers are idempotent and use retries plus a DLQ. Reads use cache-aside: `GET /orders/{id}` checks Redis, falls back to Postgres on a miss, and invalidates or refreshes on updates. I would run it on Cloud Run or Kubernetes with managed Postgres/Redis/Kafka, least-privilege IAM, secrets outside code, and logs/metrics/traces wired end to end."

Notice the shape: every component earns its place by solving a specific pain.

---

## Failure branches you must be able to trace

| Failure | What happens | Strong answer | What not to overstate |
|---|---|---|---|
| Expired token | JWT `exp` is in the past, or issuer/audience/signature is invalid | Reject at the gateway or auth middleware with `401`; client uses refresh flow if allowed | Decoding a JWT is not validation; authorization scopes are a separate check. |
| Missing `orders:create` | User is authenticated but lacks permission | Return `403`; log enough to audit without leaking sensitive claims | Do not call this authentication failure. |
| Redis outage during rate limit | The fast shared counter is unavailable | Decide explicitly: fail-open for availability with tighter downstream protection, or fail-closed for abuse-sensitive endpoints; alert either way | Redis is not the source of truth for the order. |
| Redis outage during idempotency check | Retry protection layer is unavailable | Prefer a DB unique constraint on `(user_id, idempotency_key)` as the durable backstop; Redis is the fast path | Do not rely only on an in-memory app map across instances. |
| Duplicate idempotency key | Same client retries the same create | If fingerprint matches and original succeeded, return the original result; if payload differs, return `409 Conflict`; if still in progress, return a retryable response | Do not create a second order just because the network retried. |
| DB rollback | Order insert or outbox insert fails inside the transaction | Roll back both rows; return the right 4xx for constraint/validation conflicts or 5xx for unexpected dependency failure | The outbox only helps if state and event row share the same DB transaction. |
| Publish failure | Kafka is unavailable after the order committed | API result stays valid because the outbox row is durable; relay retries with backoff and exposes outbox lag | Do not publish inside the DB transaction or claim the API has published when only the outbox commit happened. |
| Duplicate Kafka delivery | Consumer processes an event, crashes before committing offset, then receives it again | Consumer is idempotent: processed-event table, upsert by business key, or downstream idempotency key | Do not promise end-to-end exactly-once; design for at-least-once. |
| Consumer poison message | Same event fails every retry | Send to DLQ after bounded retries; alert; keep replay tooling | Do not let one bad event block a partition forever. |
| Consumer lag | Payment/notification falls behind | Monitor lag, scale consumers within partition limits, check downstream bottlenecks, and shed noncritical work if needed | More consumers than partitions in one group will not increase parallelism. |
| Stale cache | `GET /orders/{id}` returns old data after update | Update Postgres first, then invalidate or refresh Redis; TTL bounds the worst-case stale window | Cache-aside is not a consistency guarantee; Postgres remains truth. |
| Cache stampede | Hot key expires and many requests hit Postgres | Use TTL jitter, single-flight rebuild, short locks, or pre-warming | A cache can move load; it can also concentrate failure. |

---

## The interviewer follow-up checklist

Before you move on, make sure your answer has these safeguards:

- JWTs are **validated**, not just decoded: signature, issuer, audience, expiry, and scopes.
- The `order` and `outbox_event` write is atomic **inside Postgres**; Kafka publish is deliberately outside and retried by the relay.
- Idempotency exists at two levels: client retries for `POST /orders`, and at-least-once event processing for consumers.
- Kafka ordering is per partition, not global; delivery is commonly at-least-once, so duplicates are normal.
- Cache-aside makes reads faster but can be stale; invalidation plus TTL bounds the problem, it does not erase it.
- Managed cloud services reduce operations; they do not remove schema design, partition keys, IAM, secrets, or observability from your job.

## The bumper sticker

> *A named stack is not a pile of tools; it is one request crossing boundaries. Gateway checks identity, app enforces the action, Redis protects the hot path, Postgres owns truth, the outbox bridges to Kafka, consumers assume duplicates, and the cache is fast but not truth. Name the concept at each hop and the brands become portable.*

---

<div align="right">

[Honest pivots →](interview-topics-honest-pivots.md)

</div>
