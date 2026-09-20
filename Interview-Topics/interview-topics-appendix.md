# Appendix: Interview-Topics cheat-sheet kit

*[← Chapter 9](interview-topics-chapter-9.md) · [Contents](interview-topics-README.md)*

The skim-the-morning-of reference for the whole track: a one-line concept per technology, a per-chapter glossary, and a full interview question bank. Each technology's "concept beneath the brand" is the thing to recall first — everything else hangs off it.

Use the companion [stack map](interview-topics-stack-map.md) when you need to integrate the tools across one concrete request, and the [honest-pivots drill deck](interview-topics-honest-pivots.md) when you need to rehearse gap-bridging without implying experience you do not have.

---

## The concept beneath each brand (memorize these first)

| Technology | What it *is*, in one line | Concept book |
|---|---|---|
| Java collections | hash tables + arrays with a Java API | [Foundations Ch 6](../Foundations/2-operating-systems/ch6-os.md) |
| Java concurrency | OS threads + locks with a Java API | [Foundations Ch 5](../Foundations/2-operating-systems/ch5-os.md) |
| Spring Boot | dependency injection + conveniences | [LLD](../LLD/lld-README.md) |
| PostgreSQL | a relational DB engine: indexes, plans, transactions | [Foundations Ch 3](../Foundations/1-sql-and-databases/sql/ch3-sql.md) |
| Kafka | a partitioned, replayable, append-only log | [HLD Ch 6–7](../HLD/hld-chapter-6.md) |
| Redis | an in-memory cache / key-value store | [HLD Ch 5](../HLD/hld-chapter-5.md) |
| Microservices/REST | services split by capability, owning their data | [HLD Ch 7](../HLD/hld-chapter-7.md) |
| Auth (JWT/OAuth2) | a verifiable token proving *who you are* + *what you may do* | [Foundations Ch 8](../Foundations/3-networking/ch8-networking.md) |
| GCP / cloud | the same portable primitives under a brand name | [HLD](../HLD/hld-README.md) |
| FastAPI | an async (ASGI) web framework: Pydantic validation + dependency injection | [LLD](../LLD/lld-README.md) |

---

## Glossary by chapter

### Ch 1 — Java
- **equals/hashCode contract** — equal objects must return equal hash codes; override both together or hash-based collections break.
- **volatile** — guarantees visibility across threads, **not** atomicity of compound actions.
- **synchronized / Lock** — mutual exclusion + visibility; use for read-modify-write.
- **ExecutorService / Future / CompletableFuture** — managed thread pool, async result, composable async.
- **Deadlock** — mutual exclusion + hold-and-wait + no preemption + circular wait; break with global lock ordering.
- **String immutability** — every change makes a new object; `==` is reference, `equals` is content. Loops → `StringBuilder`.
- **Checked vs unchecked** — checked must be declared/caught; unchecked (RuntimeException) needn't.
- **Type erasure** — generics are compile-time only; runtime sees raw `List`. No `new T[]`, no `instanceof List<String>`.
- **Streams/lambdas** — lazy intermediate ops (`map`/`filter`) + terminal op (`collect`/`reduce`); a lambda implements a functional interface; source isn't mutated. `Optional` = typed maybe-null; records = immutable data carriers.

### Ch 2 — Spring Boot
- **IoC container** — creates and wires beans (`@Component`/`@Service`/`@Repository`/`@Configuration`).
- **Constructor injection** — explicit, `final`-able, testable without Spring; fails fast on cycles.
- **@Transactional** — proxy begins/commits/rolls-back a transaction; rolls back on unchecked by default. Self-invocation bypasses the proxy.
- **N+1 problem** — one query per parent row; fix with fetch join / `@EntityGraph` / batch size.
- **@ControllerAdvice / @ExceptionHandler** — centralized, consistent error responses.
- **Bean scope** — singleton by default (must be stateless/thread-safe); prototype = new per request.
- **Autoconfiguration** — starter on classpath + defaults wires beans; override by defining your own.
- **Security/JWT** — filter chain authenticates then authorizes; JWT = signed per-request token, no server session.
- **AOP** — proxy wraps a bean for cross-cutting code; the mechanism behind `@Transactional`/`@Cacheable`.

### Ch 3 — PostgreSQL
- **B-tree index** — sorted side-structure; speeds reads, slows writes, costs storage.
- **Leftmost-prefix rule** — a `(a, b)` index helps `a` or `a AND b`, not `b` alone.
- **Sargable** — a query the planner can satisfy with an index (no function wrapping the column).
- **EXPLAIN ANALYZE** — the actual query plan; spot seq scans, bad estimates, costly sorts.
- **Isolation levels** — read-committed → repeatable-read → serializable, by anomalies prevented. **MVCC** — readers don't block writers.
- **Index types** — B-tree default; GIN for JSONB/full-text, partial/expression for narrow or computed columns.
- **VACUUM** — reclaims dead tuples left by MVCC; skip it and tables bloat and slow down.
- **Connection pool** — connections are processes; use HikariCP/PgBouncer instead of one per request.

### Ch 4 — Kafka
- **Topic / partition / offset** — a topic is partitioned ordered logs; offset = read position.
- **Consumer group** — one consumer per partition within a group; how Kafka scales.
- **Ordering** — guaranteed only within a partition; the key picks the partition.
- **At-least-once** — the default; expect duplicates → **idempotent consumers**.
- **Honest pivot** — name the adjacent concept you've used (Pub/Sub) → map → demonstrate.

### Ch 5 — Redis
- **Cache-aside** — read: check cache → miss → DB → write with TTL; write: update DB → invalidate.
- **Invalidation** — bound staleness with TTLs + explicit deletes; the real interview question.
- **Stampede** — hot key expires → DB hammered; fix with single-flight lock, randomized TTLs, pre-warming.
- **RDB vs AOF** — snapshot (can lose recent writes) vs append-only log (more durable).
- **Beyond cache** — session store, rate limiter (`INCR`), leaderboard (ZSET), distributed lock (`SET NX PX`).

### Ch 6 — Microservices, REST & design
- **The method** — start simple, find the bottleneck, add one thing.
- **Idempotency key** — stable key so a retried/duplicated request yields the same end state.
- **Outbox pattern** — write state + outbox row in one transaction; relay publishes to Kafka (fixes dual-write).
- **Sync vs async** — REST/gRPC when you need the answer now; Kafka for side-effects, decoupling, spikes.
- **Distributed-monolith trap** — services sharing one database.
- **HTTP status codes** — 201 created, 204 no-content, 401 vs 403 (authn vs authz), 409 conflict, 429 rate-limited; 4xx is the client's fault, 5xx the server's (retry only 5xx).
- **gRPC/Protobuf** — compact binary contract over HTTP/2 defined in a `.proto`; the default for internal service-to-service calls.
- **Service mesh (sidecar)** — pushes retries/timeouts/mTLS/routing into a sidecar proxy so every service needn't re-implement them.

### Ch 7 — Auth
- **Authn vs authz** — who are you (401) vs what may you do (403).
- **Session vs JWT** — stateful + easily revoked (server store) vs stateless + scalable (signed token, hard to revoke early → keep short-lived + refresh token).
- **OAuth2 / OIDC** — delegated authorization (access token) / identity layer on top (ID token); the refresh token renews access without re-login.
- **SSO** — one identity provider, many apps; log in once.
- **Gateway auth + propagation** — validate the token once at the edge, carry the user's identity inward; **mTLS** secures service-to-service hops.
- **Password hashing** — slow, salted (bcrypt/argon2); never plaintext or fast hashes.
- **Token storage** — httpOnly cookie (needs CSRF defense) vs localStorage (XSS-readable).

### Ch 8 — Cloud
- **Pub/Sub** — topics/subscriptions, push/pull, at-least-once, ack deadlines, DLQ, ordering keys — Kafka's concepts, GCP's name.
- **Portable primitives** — managed DB, object storage, IAM, secrets, autoscaling, container runtime, CI/CD.
- **Provider-agnostic reasoning** — architecture transfers across clouds; the console is the only thing to relearn.

### Ch 9 — FastAPI
- **ASGI / Uvicorn** — async server interface; one worker handles many I/O-bound requests concurrently.
- **Pydantic** — type-hint-driven validation/serialization; `BaseSettings` for config; v1 vs v2.
- **Depends** — dependency injection (auth, DB session, validated body); `yield` deps for setup/teardown.
- **Blocking-in-async trap** — a sync call in an `async def` stalls the whole event loop; use async libs or a threadpool.
- **async ≠ parallel** — one thread; I/O concurrency, not CPU parallelism (use multiple workers for cores).
- **lifespan / app factory** — startup/shutdown for client pools; factory keeps startup testable.
- **BackgroundTasks vs queue** — in-process fire-and-forget vs a durable Celery/Pub/Sub worker.

---

## Interview question bank (by chapter)

**Ch 1 — Java**
1. Explain `HashMap` internals and the average/worst-case complexity.
2. Does `volatile` make `count++` thread-safe? What do you use instead?
3. Name the four deadlock conditions and the most practical fix.
4. `Runnable` vs `Callable`; how do you run async work and get a result?
5. What's a memory leak in a GC'd language? Give an example.
6. Why is `String` immutable; `==` vs `equals`; checked vs unchecked.
7. Rewrite a loop as a stream — name intermediate vs terminal ops; what is type erasure?

**Ch 2 — Spring Boot**
1. Constructor vs field injection — which and why?
2. What does `@Transactional` do, and what are the three gotchas?
3. Why might a `@Transactional` method not roll back when called from the same class?
4. What is the N+1 problem and how do you fix it?
5. How do you handle errors consistently across a REST API?
6. What does Boot add over Spring; explain autoconfiguration and bean scopes.
7. Sessions vs JWT; what is AOP doing under `@Transactional`?

**Ch 3 — PostgreSQL**
1. Why do indexes speed reads but slow writes? When would you not add one?
2. Does a `(a, b)` composite index help a query filtering only on `b`?
3. Walk through debugging a slow query.
4. Name the isolation levels and what each prevents.
5. Normalize vs denormalize — when and why denormalize on purpose?
6. What is VACUUM for; why does a high-update table slow without it?
7. Why a connection pool; when GIN/partial over B-tree?

**Ch 4 — Kafka**
1. What is Kafka, in one sentence?
2. How does it scale consumption, and what's the ordering guarantee?
3. What's the default delivery guarantee, and how do you avoid duplicates?
4. Kafka vs a traditional queue?
5. Give your honest-pivot answer for "have you used Kafka in production?"

**Ch 5 — Redis**
1. What is Redis, in one sentence?
2. Walk through cache-aside on a read and a write.
3. What is a cache stampede and how do you prevent it?
4. Is Redis durable? RDB vs AOF?
5. Three uses of Redis beyond caching, and how one works.

**Ch 6 — Microservices, REST & design**
1. Design an order service, adding components only as bottlenecks justify them.
2. Sync vs async — how do you choose, and what does async cost?
3. How do you make an operation idempotent, and why does at-least-once force it?
4. What's the dual-write problem and how does the outbox solve it?
5. Why is a shared database across services an anti-pattern?
6. Pick the status code: a successful `DELETE`; a duplicate unique record; an expired login; a permitted user hitting a forbidden endpoint. (204 / 409 / 401 / 403.)
7. REST vs gRPC for internal calls — when gRPC, and what do you trade? What does a service mesh handle for you?

**Ch 7 — Auth**
1. Authentication vs authorization — define each and the status code each failure returns.
2. Sessions vs JWTs — the tradeoff, and how do you revoke a JWT before it expires?
3. What does OAuth2 solve and what does OIDC add? Name the access, refresh, and ID tokens' jobs.
4. Trace a logged-in user's identity from the browser through an API gateway to an internal service, and where each hop is secured.
5. How are passwords stored safely, and where should a browser keep its token (and the attack each choice exposes)?

**Ch 8 — Cloud**
1. Describe a real system you built on a cloud — specifics.
2. Pub/Sub vs Kafka?
3. "We're on AWS, you're GCP — is that a problem?"
4. Name the portable primitives and two cross-provider equivalents.
5. Why does architecture reasoning transfer across clouds?

**Ch 9 — FastAPI**
1. What is FastAPI in one sentence, and what three pieces does it combine?
2. A blocking DB call in an `async def` route — what happens under load, and the two fixes?
3. Is `async` the same as parallel? When does it actually make a service faster?
4. What does `Depends` do, and which concept from the other tracks is it?
5. `BackgroundTasks` vs a task queue — when is `BackgroundTasks` the wrong choice?
6. What does the `lifespan` context manager do, and why an app factory?
7. Give your honest-pivot answer for a Spring/Java vs FastAPI/Python mismatch.

---

## The bumper sticker

> *A job description names tools; an interviewer tests the concepts underneath. Recall the one-line concept beneath each brand first — then the must-knows, the likely questions, and the honest pivot for any gap all hang off it. Brand on top, concept underneath.*
